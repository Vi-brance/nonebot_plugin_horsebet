import random
from typing import List

from .horse import horse
from .setting import *


# 马场信息类
class Race:
    # 初始化
    def __init__(self, init_horse_num: int):
        # 初始化每匹马
        self.horses = [horse(i, random.randint(setting_horse_buff[0], setting_horse_buff[1])) for i in range(init_horse_num)]
        # 当前回合数
        self.round = 0
        # 比赛开始信息，True为开始
        self.start = False
        # 马场赌金
        self.gold = setting_base_gold

        # 分配每匹马下注的初始金额
        for i in self.horses:
            i.base_gold = int(self.gold * odd_buff(i.buff) / 100)
            i.odds(self.gold)

    # 返回参加赛马数
    @property
    def horse_num(self) -> int:
        return len(self.horses)

    # 添加马儿的赌金信息，返回True则为加注，False为下注
    def add_coin(self, bet_horse: int, uid: int, gold: int) -> bool:
        self.gold += gold
        return self.horses[bet_horse].add_coin(uid, gold)

    # 马儿移动
    def move(self):
        for i in range(len(self.horses)):
            self.horses[i].move()

    # 显示马场界面
    def display(self) -> str:
        display = ''
        for i in range(len(self.horses)):
            display += '\n' + self.horses[i].display()  # 每行为每匹马的路线
        return display[1: len(display)]

    # 获取胜者信息
    def get_winner(self) -> List:
        winner = []
        for i in range(len(self.horses)):
            if self.horses[i].location >= setting_track_length:
                winner.append(self.horses[i].horse_num)
        return winner

    # 显示赔率信息
    def show_odds(self) -> str:
        odds = ''
        for i in range(len(self.horses)):
            odds += '\n' + self.horses[i].odds(int(self.gold * (1 - setting_maker_rate)))
        return odds[1: len(odds)]

    # 查找玩家下注的马号
    def find_player(self, uid: int) -> int:
        for horse in self.horses:
            for player in horse.horse_gold:
                if player['uid'] == uid:
                    return horse.horse_num
        return -1
