import random

from .setting import *


# 马匹信息类
class horse:
    # 初始化
    def __init__(self, init_horse_num: int, buff: int):
        # 赛马编号
        self.horse_num = init_horse_num
        # 赛马赌金
        self.horse_gold = []
        # 赛马赔率
        self.horse_odds = 1.0
        # 马儿脚力
        self.buff = buff
        # 基础金币
        self.base_gold = 0
        # 马儿位置
        self.location = 0
        # 马儿下一回合前进的步数
        self.location_add = 0

    # 下注
    def add_coin(self, uid: int, gold: int) -> bool:
        for i in self.horse_gold:  # 查找已有信息
            if i['uid'] == uid:
                i['gold'] += gold
                return True
        self.horse_gold.append({'uid': uid, 'gold': gold})  # 创建新信息
        return False

    # 计算马儿的所有赌金
    def get_gold(self) -> int:
        gold_all = self.base_gold
        for gold in self.horse_gold:
            gold_all += gold['gold']
        return gold_all

    # 计算并显示赔率信息
    def odds(self, all_gold: int) -> str:
        self.horse_odds = all_gold / self.get_gold()
        return f'[{self.horse_num + 1:02}]：{self.horse_odds: .2f}'

    # 马儿移动
    def move(self):
        if self.location != track_length:  # 未达到终点
            self.location_add = random.randint(base_move[0], base_move[1] + self.buff)  # 随机前进步数
            self.location += self.location_add  # 更新马儿位置

    # 马儿在赛道上的位置显示
    def display(self, ahead_pos: int):
        display = f'[{self.horse_num + 1:02}]'  # 编号
        if ahead_pos - self.location >= track_display_length:
            for i in range(track_display_length - 1):
                display += '🏁' if ahead_pos - i == track_length else '➖'  # 超出视线范围
            display += '❓'
            return display
        for i in range(ahead_pos - self.location):
            display += '🏁' if ahead_pos - i == track_length else '➖'  # 马前的赛道
        display += '🐎'  # 马
        if ahead_pos - self.location + 1 == track_display_length:
            return display
        for i in range(self.location_add):
            if ahead_pos - self.location + 1 + i == track_display_length:
                return display
            display += '💨'  # 马的奔跑速度
        for i in range(track_display_length - (ahead_pos - self.location) - 1 - self.location_add):
            display += '🚩' if self.location - 1 - self.location_add - i == 0 else '➖'  # 马后的赛道
        return display
