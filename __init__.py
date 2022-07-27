import time
import nonebot
from nonebot.adapters.onebot.v11 import (
    GROUP,
    GroupMessageEvent,
    MessageSegment,
    Message)
from nonebot.params import CommandArg
from nonebot.log import logger

from .race_group import race_group
from .player import player
from .setting import *

RaceSign = nonebot.on_command('赛马签到', permission=GROUP, priority=5, block=True)
RaceNew = nonebot.on_command('赛马创建', permission=GROUP, priority=5, block=True)
RaceBet = nonebot.on_command('下注', permission=GROUP, priority=5, block=True)
RaceStart = nonebot.on_command('赛马开始', permission=GROUP, priority=5, block=True)
RaceStop = nonebot.on_command('赛马终止', permission=GROUP, priority=5, block=True)
PlayerGold = nonebot.on_command('资产查询', permission=GROUP, priority=5, block=True)
PlayerRank = nonebot.on_command('赛马排行', permission=GROUP, priority=5, block=True)

# 全局数据
data = {}


# 响应赛马签到
@RaceSign.handle()
async def _(event: GroupMessageEvent):
    global data
    group = event.group_id
    if group not in data.keys():  # 未载入本群玩家信息
        data[group] = {'players': player(group)}
    msg, gold = data[group]['players'].sign(event)
    await RaceSign.send(msg, at_sender=True)  # 发送签到结果
    if gold != -1:  # 日志记录
        logger.info(
            f'USER {event.user_id} | GROUP {event.group_id} 获取 {gold} 枚金币')


# 响应赛马创建
@RaceNew.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    global data
    group = event.group_id
    init_horse_num = int(arg.extract_plain_text().strip())  # 获取初始化的马道数
    try:
        if data[group]['race'].start == 1:
            await RaceNew.finish('赛马正在进行中')
    except KeyError:
        pass
    if init_horse_num < horse_num[0] or init_horse_num > horse_num[1]:
        await RaceNew.finish('请输入 {horse_num[0]} - {horse_num[1]} 之间的数初始化赛马')
    if group not in data.keys():
        data[group] = {'race': {}, 'players': player(group)}
    data[group]['race'] = race_group(init_horse_num, event.user_id)
    await RaceNew.finish(f'创建赛马比赛成功！\n输入 下注[马道][金币] 即可加入赛马')


# 响应下注
@RaceBet.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    global data
    uid = event.user_id
    group = event.group_id
    if data[group]['race'].start:  # 比赛已开始
        await RaceBet.finish('比赛已开始')
    args = arg.extract_plain_text().strip().split()
    try:
        for i in range(len(args)):
            args[i] = int(args[i])
    except KeyError:
        pass
    if len(args) != 2:  # 接受参数个数错误
        await RaceBet.finish('格式错误，请输入 下注[马道][金币] 加入赛马！')
    if args[0] > data[group]['race'].query_of_horses() or args[0] < 1:  # 马道数错误
        await RaceBet.finish('没有对应马道')
    if args[1] < 0:  # 赌金为负
        await RaceBet.finish('赌金不能为负！')
    elif args[1] == 0:  # 赌金为0
        await RaceBet.finish('赌金不能为零！')
    horse_num, gold = int(args[0]) - 1, int(args[1])
    if data[group]['players'].get_gold(uid) < gold:  # 赌金大于拥有金币
        await RaceBet.finish('金币不足')
    data[group]['players'].add_gold(uid, -gold)  # 更新玩家拥有的金币
    msg = ''
    if data[group]['race'].add_coin(horse_num, uid, gold) is True:  # 更新马儿的赌金信息
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
        display = f''  # 显示界面
        data[group]['race'].round += 1
        data[group]['race'].move()
        display += data[group]['race'].display()
        await RaceStart.send(display)
        time.sleep(2)
        winner = data[group]['race'].get_winner()
        if winner != []:  # 判断是否有马到达终点
            # 结算
            for win in winner:
                win_horse = data[group]['race'].horses[win]
                for player in win_horse.horse_gold:
                    data[group]['players'].add_gold(player['uid'], int(player['gold'] * win_horse.horse_odds))
                maker = data[group]['race'].maker_uid
                data[group]['players'].add_gold(maker, - int(win_horse.get_gold() * setting_maker_gold))
            del data[group]['race']
            await RaceStart.finish(f'比赛已结束，胜者为：{[x + 1 for x in winner]} 号马！')


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
    msg = data[group]['player'].display_gold(event.user_id)
    await PlayerGold.finish(msg)


# 响应赛马排行榜
@PlayerRank.handle()
async def _(event: GroupMessageEvent):
    global data
    await PlayerRank.finish('排行榜功能开发中...')
