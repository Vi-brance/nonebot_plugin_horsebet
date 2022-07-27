from pickle import SHORT_BINSTRING
import random

from .setting import *


# 赛马信息
class horse:
    # 初始化
    def __init__(self, init_horse_num: int):
        # 赛马编号
        self.horse_num = init_horse_num
        # 赛马赌金
        self.horse_gold = []
        # 赛马赔率
        self.horse_odds = 1.0
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

    # 马儿移动
    def location_move(self):
        if self.location != setting_track_length:  # 未达到终点
            self.location_add = random.randint(base_move[0], base_move[1])  # 随机前进步数
            self.location += self.location_add  # 更新马儿位置
            if self.location > setting_track_length:  # 判断是否越界
                self.location_add -= self.location - setting_track_length
                self.location = setting_track_length

    # 马儿在赛道上的位置显示
    def display(self):
        display = f'[{self.horse_num + 1}]'
        for i in range(setting_track_length - self.location):
            display += '_'  # 马前的赛道
        display += '🐎'  # 马
        for i in range(self.location_add):
            display += '💨'  # 标记马的奔跑速度
        for i in range(setting_track_length - self.location, setting_track_length - self.location_add - 1):
            display += '_'  # 马后的赛道
        return display

    # 计算马儿的所有赌金
    def get_gold(self) -> int:
        gold_all = 0
        for gold in self.horse_gold:
            gold_all += gold['gold']
        return gold_all

    # 计算并显示赔率信息
    def odds(self, all_gold: int) -> str:
        if all_gold >= setting_odd_start:
            try:
                self.horse_odds = all_gold / self.get_gold()
            except ZeroDivisionError:
                pass
        return f'{self.horse_num + 1} 号马：{self.horse_odds: .1f}'
