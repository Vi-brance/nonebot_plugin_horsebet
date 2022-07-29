import time
import nonebot
from nonebot.adapters.onebot.v11 import (
    GROUP,
    GroupMessageEvent,
    Message)
from nonebot.params import CommandArg
from nonebot.log import logger

from .race import Race
from .player import Player
from .setting import *

RaceSign = nonebot.on_command('赛马签到', permission=GROUP, priority=5, block=True)
RaceNew = nonebot.on_command('赛马创建', permission=GROUP, priority=5, block=True)
RaceBet = nonebot.on_command('下注', permission=GROUP, priority=5, block=True)
RaceStart = nonebot.on_command('赛马开始', permission=GROUP, priority=5, block=True)
RaceStop = nonebot.on_command('赛马终止', permission=GROUP, priority=5, block=True)
PlayerGold = nonebot.on_command('资产查询', permission=GROUP, priority=5, block=True)
PlayerGoldRank = nonebot.on_command('赛马排行', permission=GROUP, priority=5, block=True)

# 全局数据：{key:群号, value: {'player': Player(), 'race': Race()}}
data = {}


# 初始化data的玩家信息
def init_data(group: int):
    global data
    if group not in data.keys():
        data[group] = {'player': Player(group)}


# 响应赛马签到
@RaceSign.handle()
async def _(event: GroupMessageEvent):
    global data
    init_data(event.group_id)
    gold = data[event.group_id]['player'].sign(event)
    if gold == -1:  # 已签到
        await RaceSign.finish('今日已签到', at_sender=True)
    else:  # 日志记录
        logger.info(f'USER {event.user_id} | GROUP {event.group_id} 获取 {gold} 枚金币')
        await RaceSign.finish(f'签到成功，你获得了 {gold} 枚金币', at_sender=True)


# 响应赛马创建
@RaceNew.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    global data
    group = event.group_id
    try:
        init_horse_num = int(arg.extract_plain_text().strip())  # 获取初始化的马道数
    except ValueError:
        await RaceNew.finish('输入 赛马创建+数字 创建赛马')
    try:
        if data[group]['race'].start:
            await RaceNew.finish('赛马正在进行中')
        else:
            await RaceNew.finish('赛马已创建')
    except KeyError:
        pass
    if init_horse_num not in range(setting_horse_num[0], setting_horse_num[1] + 1):
        await RaceNew.finish(f'请输入 {setting_horse_num[0]} - {setting_horse_num[1]} 之间的数初始化赛马')
    init_data(group)
    data[group]['race'] = Race(init_horse_num)
    await RaceNew.send('赛马准备完毕！\n输入 下注[马道][金币] 即可加入赛马')
    await RaceNew.finish('当前赔率：\n' + data[group]['race'].show_odds())


# 响应下注
@RaceBet.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    global data
    uid = event.user_id
    group = event.group_id
    if group not in data.keys():
        await RaceBet.finish('赛马还没开始')
    try:
        if data[group]['race'].start:  # 比赛已开始
            await RaceBet.finish('比赛已开始')
    except KeyError:
        pass
    args = arg.extract_plain_text().strip().split()
    try:
        for i in range(len(args)):
            args[i] = int(args[i])
    except KeyError:
        pass
    if len(args) != 2:  # 接受参数个数错误
        await RaceBet.finish('格式错误，请输入 下注[马道][金币] 加入赛马！')
    if args[0] not in range(1, data[group]['race'].query_of_horses() + 1):  # 马道数错误
        await RaceBet.finish('没有对应马道')
    if args[1] <= 0:  # 赌金为非正数
        await RaceBet.finish('你还想我给你钱吗？')
    horse_num, gold = int(args[0]) - 1, int(args[1])
    if data[group]['player'].get_gold(uid) < gold:  # 赌金大于拥有金币
        await RaceBet.finish('金币不足')
    horse_bet = data[group]['race'].find_player(uid)
    if horse_bet != -1 and horse_bet + 1 != args[0]:
        await RaceBet.finish(f'你已经给 {horse_bet + 1} 下注了，不能再给其他马下注')
    data[group]['player'].change_gold(uid, -gold)  # 更新玩家拥有的金币
    msg = ''
    if data[group]['race'].add_coin(horse_num, uid, gold):  # 更新马儿的赌金信息
        msg += '加注成功！\n'
    else:
        msg += '下注成功！\n'
    msg += '当前赔率：\n' + data[group]['race'].show_odds()
    await RaceBet.finish(msg, at_sender=True)


# 响应赛马开始
@RaceStart.handle()
async def _(event: GroupMessageEvent):
    global data
    group = event.group_id
    if data[group]['race'].start == 0:  # 更新赛马开始状态
        data[group]['race'].start = True
    else:
        await RaceStart.finish('赛马已经开始了！')
    data[group]['race'].time = time.time()  # 记录开始赛马的时间
    while data[group]['race'].start is True:  # 赛马主体
        display = ''  # 显示界面
        data[group]['race'].round += 1
        data[group]['race'].move()
        display += data[group]['race'].display()
        await RaceStart.send(display)
        time.sleep(3)
        winner = data[group]['race'].get_winner()
        if winner:  # 判断是否有马到达终点
            # 结算
            for win in winner:
                win_horse = data[group]['race'].horses[win]
                for player in win_horse.horse_gold:
                    data[group]['player'].change_gold(player['uid'], int(player['gold'] * win_horse.horse_odds / len(winner)))
                    data[group]['player'].add_win(player['uid'])
            del data[group]['race']
            await RaceStart.finish(f'{[x + 1 for x in winner]} 号马成功冲线！')


# 响应赛马终止
@RaceStop.handle()
async def _(event: GroupMessageEvent):
    global data
    group = event.group_id
    if not data[group]['race']:
        await RaceStop.finish(f'没有进行中的比赛')
    del data[group]['race']
    await RaceStop.finish(f'已终止比赛')


# 响应资产查询
@PlayerGold.handle()
async def _(event: GroupMessageEvent):
    global data
    group = event.group_id
    init_data(group)
    msg = data[group]['player'].display_gold(event.user_id)
    await PlayerGold.finish(msg)


# 响应赛马排行榜
@PlayerGoldRank.handle()
async def _(event: GroupMessageEvent):
    global data
    group = event.group_id
    init_data(group)
    await PlayerGold.finish('赛马资产排行榜：\n' + data[group]['player'].display_gold_rank())
