import nonebot
from nonebot.adapters.onebot.v11 import (
    GROUP,
    GroupMessageEvent,
    Message)
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.log import logger
from typing import Union

from .race import Race
from .player import Player
from .config import *

RaceSign = nonebot.on_fullmatch('赛马签到', permission=GROUP, priority=5, block=True)
RaceNew = nonebot.on_command('赛马创建', permission=GROUP, priority=5, block=True)
RaceStart = nonebot.on_fullmatch('赛马开始', permission=GROUP, priority=5, block=True)
RaceStop = nonebot.on_fullmatch('赛马终止', permission=SUPERUSER, priority=5, block=True)
RaceBet = nonebot.on_command('下注', permission=GROUP, priority=5, block=True)
PlayerGold = nonebot.on_fullmatch('资产查询', permission=GROUP, priority=5, block=True)
PlayerGoldRank = nonebot.on_fullmatch('赛马排行', permission=GROUP, priority=5, block=True)

# 全局数据
race_data: Dict[int, Dict[str, Union[Player, Race]]] = {}


# 初始化data的玩家信息
def init_player(group: int):
    global race_data
    if group not in race_data.keys():
        race_data[group] = {'player': Player(group)}


# 响应赛马签到
@RaceSign.handle()
async def _(event: GroupMessageEvent):
    global race_data
    group = event.group_id
    init_player(group)
    gold = race_data[group]['player'].sign(event)
    if gold == -1:  # 已签到
        await RaceSign.finish('今日已签到', at_sender=True)
    else:
        logger.info(f'USER {event.user_id} | GROUP {group} 获取 {gold} 枚金币')  # 日志记录
        await RaceSign.finish(f'签到成功，你获得了 {gold} 枚金币', at_sender=True)


# 响应赛马创建
@RaceNew.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    global race_data
    group = event.group_id
    try:
        if race_data[group]['race'].start:
            await RaceNew.finish('赛马正在进行中')
        else:
            await RaceNew.finish('赛马已创建')
    except KeyError:
        pass
    init_horse_num = 0
    if is_number(arg.extract_plain_text()):
        init_horse_num = int(arg.extract_plain_text())  # 获取初始化的马道数
    else:
        await RaceNew.finish('输入 赛马创建+数字 创建赛马')
    if init_horse_num not in range(setting_horse_num[0], setting_horse_num[1] + 1):
        await RaceNew.finish(f'请输入 {setting_horse_num[0]} - {setting_horse_num[1]} 之间的数初始化赛马')
    init_player(group)
    race_data[group]['race'] = Race(init_horse_num, event.user_id)
    await RaceNew.send(race_data[group]['race'].display_horse_attribute())
    time.sleep(1)
    await RaceNew.send('赛马准备完毕！\n输入 下注[马道][金币] 即可加入赛马')
    await RaceNew.finish('当前赔率：\n' + race_data[group]['race'].show_odds())


# 响应下注
@RaceBet.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    global race_data
    uid = event.user_id
    group = event.group_id
    init_player(group)
    # 过滤比赛状态错误
    try:
        if race_data[group]['race'].start:  # 比赛已开始
            await RaceBet.finish('比赛已开始')
    except KeyError:  # 赛马未创建
        await RaceBet.finish('赛马还没创建')
    # 过滤参数错误
    args = arg.extract_plain_text().strip().split()
    if len(args) != 2 or not (is_number(args[0]) and is_number(args[1])):  # 接受参数个数错误
        await RaceBet.finish('格式错误，请输入 下注[马道][金币] 加入赛马')
    bet_horse, gold = int(args[0]) - 1, int(args[1])
    # 过滤马道和赌金非法错误
    if bet_horse not in range(race_data[group]['race'].horse_num):  # 马道数错误
        await RaceBet.finish('没有对应马道')
    if gold <= 0:  # 赌金为非正数
        await RaceBet.finish('你还想我给你钱吗？')
    if race_data[group]['player'].get_gold(uid) < gold:  # 赌金大于拥有金币
        await RaceBet.finish('金币不足')
    horse_bet = race_data[group]['race'].find_player(uid) + 1
    if horse_bet and horse_bet != bet_horse:
        await RaceBet.finish(f'你已经给 {horse_bet} 下注了，不能再给其他马下注')
    # 下注成功
    race_data[group]['player'].change_gold(uid, -gold)  # 更新玩家拥有的金币
    msg = '加注成功！\n' if race_data[group]['race'].add_coin(bet_horse, uid, gold) else '下注成功！\n'
    msg += '当前赔率：\n' + race_data[group]['race'].show_odds()
    await RaceBet.finish(msg, at_sender=True)


# 响应赛马开始
@RaceStart.handle()
async def _(event: GroupMessageEvent):
    global race_data
    group = event.group_id
    try:
        if race_data[group]['race'].start:
            await RaceStart.finish('赛马已经开始了！')
        elif race_data[group]['race'].host_id != event.user_id:  # 更新赛马开始状态
            await RaceStart.finish('只有创建赛马的人能开始')
        else:
            race_data[group]['race'].start = True
    except KeyError:
        await RaceStart.finish('赛马还没创建')
    # 赛马主体
    while race_data[group]['race'].start is True:
        display = ''  # 显示赛道
        race_data[group]['race'].round += 1
        race_data[group]['race'].move()
        display += race_data[group]['race'].display()
        await RaceStart.send(display)
        time.sleep(2)
        winner = race_data[group]['race'].get_winner()
        if winner:  # 判断是否有马到达终点
            # 赛马结算
            for win in winner:
                win_horse = race_data[group]['race'].horses[win]
                for win_player in win_horse.uid_gold.keys():
                    race_data[group]['player'].change_gold(win_player, int(win_horse.uid_gold[win_player] * win_horse.horse_odds))
                    race_data[group]['player'].add_win(win_player)
            del race_data[group]['race']
            await RaceStart.finish(f'{[x + 1 for x in winner]} 号马成功冲线！')


# 响应赛马终止
@RaceStop.handle()
async def _(event: GroupMessageEvent):
    global race_data
    group = event.group_id
    if not race_data[group]['race']:
        await RaceStop.finish(f'没有进行中的比赛')
    ret_uid_gold = race_data[group]['race'].get_uid_gold()
    for uid in ret_uid_gold.keys():
        race_data[group]['player'].change_gold(uid, ret_uid_gold[uid])
    del race_data[group]['race']
    await RaceStop.finish(f'已终止比赛')


# 响应资产查询
@PlayerGold.handle()
async def _(event: GroupMessageEvent):
    global race_data
    group = event.group_id
    init_player(group)
    msg = race_data[group]['player'].display_gold(event.user_id)
    await PlayerGold.finish(msg)


# 响应赛马排行榜
@PlayerGoldRank.handle()
async def _(event: GroupMessageEvent):
    global race_data
    group = event.group_id
    init_player(group)
    await PlayerGold.finish('赛马资产排行榜：\n' + race_data[group]['player'].display_gold_rank())
