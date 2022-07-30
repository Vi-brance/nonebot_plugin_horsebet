import random

from .setting import *


# 马匹信息类
class horse:
    # 初始化
    def __init__(self, num: int):
        # 赛马编号
        self.num = num
        # 基础金币
        self.base_gold = 0
        # 赛马赔率
        self.horse_odds = 1.0
        # 赛马赌金
        self.uid_gold = []
        # 属性
        while True:
            self.attribute = {
                'speed': random.choice(generate_attribute),
                'persis': random.choice(generate_attribute),
                'explode': random.choice(generate_attribute),
                'state': random.choice(generate_attribute)
            }
            if self.get_attribute() in range(attribute_range[0], attribute_range[1] + 1):
                break
        # 马儿位置
        self.location = 0
        # 马儿下一回合前进的步数
        self.location_add = 0

    # 返回属性总值
    def get_attribute(self) -> int:
        attribute = 0
        for i in self.attribute.values():
            attribute += i
        return attribute

    # 下注
    def add_coin(self, uid: int, gold: int) -> bool:
        for i in self.uid_gold:  # 查找已有信息
            if i['uid'] == uid:
                i['gold'] += gold
                return True
        self.uid_gold.append({'uid': uid, 'gold': gold})  # 创建新信息
        return False

    # 计算马儿的所有赌金
    def all_gold(self) -> int:
        gold = self.base_gold
        for x in self.uid_gold:
            gold += x['gold']
        return gold

    # 计算并显示赔率信息
    def odds(self, all_gold: int) -> str:
        self.horse_odds = all_gold / self.all_gold()
        return f'[{self.num + 1:02}]：{self.horse_odds: .2f}'

    # 马儿移动
    def move(self, round: int):
        if self.location != track_length:  # 未达到终点
            # 计算前进步数
            mov_min, mov_max = base_move
            state_per = random.randint(1, 100)
            if state_per <= (base_state + self.attribute['state'] * 15) and round <= self.attribute['persis']:
                mov_max += self.attribute['speed']
            state_per = random.randint(1, 100)
            if state_per <= (base_state + self.attribute['state'] * 15) and track_length - self.location <= int(
                    track_length * explode_start):
                mov_max += self.attribute['explode']
            self.location_add = random.randint(mov_min, mov_max)
            self.location += self.location_add  # 更新马儿位置

    # 马儿在赛道上的位置显示
    def display(self, ahead_pos: int):
        display = f'[{self.num + 1:02}]'  # 编号
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
