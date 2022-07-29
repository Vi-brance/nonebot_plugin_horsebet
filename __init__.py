from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    GROUP,
    GroupMessageEvent,
    Message)
from nonebot.params import CommandArg
from nonebot.log import logger
from typing import Union

from .race import Race
from .player import Player
from .setting import *

RaceSign = on_command('赛马签到', permission=GROUP, priority=5, block=True)
RaceNew = on_command('赛马创建', permission=GROUP, priority=5, block=True)
RaceStart = on_command('赛马开始', permission=GROUP, priority=5, block=True)
RaceStop = on_command('赛马终止', permission=GROUP, priority=5, block=True)
RaceBet = on_command('下注', permission=GROUP, priority=5, block=True)
PlayerGold = on_command('资产查询', permission=GROUP, priority=5, block=True)
PlayerGoldRank = on_command('赛马排行', permission=GROUP, priority=5, block=True)

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
    init_player(event.group_id)
    gold = race_data[event.group_id]['player'].sign(event)
    if gold == -1:  # 已签到
        await RaceSign.finish('今日已签到', at_sender=True)
    else:
        logger.info(f'USER {event.user_id} | GROUP {event.group_id} 获取 {gold} 枚金币')  # 日志记录
        await RaceSign.finish(f'签到成功，你获得了 {gold} 枚金币', at_sender=True)


# 响应赛马创建
@RaceNew.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    global race_data
    group = event.group_id
    init_horse_num = 0
    try:
        init_horse_num = int(arg.extract_plain_text())  # 获取初始化的马道数
    except ValueError:
        await RaceNew.finish('输入 赛马创建+数字 创建赛马')
    try:
        if race_data[group]['race'].start:
            await RaceNew.finish('赛马正在进行中')
        else:
            await RaceNew.finish('赛马已创建')
    except KeyError:
        pass
    if init_horse_num not in range(setting_horse_num[0], setting_horse_num[1] + 1):
        await RaceNew.finish(f'请输入 {setting_horse_num[0]} - {setting_horse_num[1]} 之间的数初始化赛马')
    init_player(group)
    race_data[group]['race'] = Race(init_horse_num)
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
    try:
        args = [int(x) for x in args]  # 参数类型错误
    except ValueError:
        await RaceBet.finish('格式错误，请输入 下注[马道][金币] 加入赛马')
    if len(args) != 2:  # 接受参数个数错误
        await RaceBet.finish('格式错误，请输入 下注[马道][金币] 加入赛马')
    bet_horse, gold = args[0] - 1, args[1]
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
        if not race_data[group]['race'].start:  # 更新赛马开始状态
            race_data[group]['race'].start = True
        else:
            await RaceStart.finish('赛马已经开始了！')
    except KeyError:
        await RaceStart.finish('赛马还没创建')
    # 赛马主体
    while race_data[group]['race'].start is True:
        display = ''  # 显示赛道
        race_data[group]['race'].round += 1
        race_data[group]['race'].move()
        display += race_data[group]['race'].display()
        await RaceStart.send(display)
        time.sleep(3)
        winner = race_data[group]['race'].get_winner()
        if winner:  # 判断是否有马到达终点
            # 赛马结算
            for win in winner:
                win_horse = race_data[group]['race'].horses[win]
                for win_player in win_horse.horse_gold:
                    race_data[group]['player'].change_gold(win_player['uid'],
                                                           int(win_player['gold'] * win_horse.horse_odds))
                    race_data[group]['player'].add_win(win_player['uid'])
            del race_data[group]['race']
            await RaceStart.finish(f'{[x + 1 for x in winner]} 号马成功冲线！')


# 响应赛马终止
@RaceStop.handle()
async def _(event: GroupMessageEvent):
    global race_data
    group = event.group_id
    if not race_data[group]['race']:
        await RaceStop.finish(f'没有进行中的比赛')
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
