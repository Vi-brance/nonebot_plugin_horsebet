import random
from typing import List

from attr import Attribute

from .horse import horse
from .config import *


# 马场信息类
class Race:
    # 初始化
    def __init__(self, init_horse_num: int, uid: int):
        # 马场马匹数
        self.horse_num = init_horse_num
        # 初始化每匹马
        self.horses = [horse(i) for i in range(self.horse_num)]
        # 当前回合数
        self.round = 0
        # 比赛开始信息，True为开始
        self.start = False
        # 马场赌金
        self.gold = setting_base_gold
        # 创建马场的玩家id
        self.host_id = uid

        # 分配每匹马下注的初始金额
        for i in self.horses:
            i.base_gold = int(
                self.gold * i.get_attribute() / self.get_attributes())
            i.odds(self.gold)

    # 返回所有马匹总属性
    def get_attributes(self) -> int:
        attribute = 0
        for i in self.horses:
            attribute += i.get_attribute()
        return attribute

    # 查找玩家下注的马号
    def find_player(self, uid: int) -> int:
        for x in self.horses:
            if uid in x.uid_gold.keys():
                return x.num
        return -1

    # 返回所有下注的玩家id和对应金币
    def get_uid_gold(self) -> Dict[int, int]:
        uid_gold = {}
        for x in self.horses:
            for y in x.uid_gold.keys():
                if y in uid_gold.keys():
                    uid_gold[y] += x.uid_gold[y]
                else:
                    uid_gold[y] = x.uid_gold[y]
        return uid_gold

    # 添加马儿的赌金信息，返回True则为加注，False为下注
    def add_coin(self, bet_horse: int, uid: int, gold: int) -> bool:
        self.gold += gold
        return self.horses[bet_horse].add_coin(uid, gold)

    # 马儿移动
    def move(self):
        for i in self.horses:
            i.move(self.round)

    # 获取胜者信息
    def get_winner(self) -> List:
        winner = []
        max_track = track_length
        for i in range(len(self.horses)):
            if self.horses[i].location == max_track:
                winner.append(self.horses[i].num)
            elif self.horses[i].location > max_track:
                max_track = self.horses[i].location
                winner.clear()
                winner.append(self.horses[i].num)
        return winner

    # 显示马匹属性面板
    def display_horse_attribute(self) -> str:
        display = '编号 | 速度 | 持久 | 爆发 | 状态'
        for x in self.horses:
            display += (f'\n [{x.num + 1:02}]'
                        f' | {attribute_name[x.attribute["speed"] - 1]}'
                        f' | {attribute_name[x.attribute["persis"] - 1]}'
                        f' | {attribute_name[x.attribute["explode"] - 1]}'
                        f' | {attribute_name[x.attribute["state"] - 1]}')
        return display

    # 显示赔率信息
    def show_odds(self) -> str:
        odds = ''
        for i in range(len(self.horses)):
            odds += '\n' + \
                    self.horses[i].odds(int(self.gold * (1 - setting_maker_rate)))
        return odds[1: len(odds)]

    # 显示马场界面
    def display(self) -> str:
        display = '[00]'
        ahead_pos = max(x.location for x in self.horses) + 2
        for i in range(track_display_length):
            display += '🚩' if (ahead_pos - i) % track_gape == 0 else '☁️'
        for i in range(len(self.horses)):
            display += '\n' + self.horses[i].display(ahead_pos)  # 每行为每匹马的路线
        return display
