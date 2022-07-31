import random

from .config import horse_config as config


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
        # 赛马赌金：{uid: gold}
        self.uid_gold = {}
        # 属性
        while True:
            self.ppt = {
                'speed': config.generate_ppt(),
                'persis': config.generate_ppt(),
                'explode': config.generate_ppt(),
                'state': config.generate_ppt()
            }
            if config.ppt_in_range(self.get_ppt()):
                break
        # 马儿位置
        self.location = 0
        # 马儿下一回合前进的步数
        self.location_add = 0

    # 返回属性总值
    def get_ppt(self) -> int:
        ppt = 0
        for i in self.ppt.values():
            ppt += i
        return ppt

    # 下注
    def add_coin(self, uid: int, gold: int) -> bool:
        if uid in self.uid_gold.keys():  # 查找已有信息
            self.uid_gold[uid] += gold
            return True
        # 创建新信息
        self.uid_gold[uid] = gold
        return False

    # 计算马儿的所有赌金
    def all_gold(self) -> int:
        gold = self.base_gold
        for x in self.uid_gold.values():
            gold += x
        return gold

    # 检查是否到达终点
    def is_winner(self) -> bool:
        if self.location >= config.length:
            return True
        return False

    # 计算并显示赔率信息
    def odds(self, all_gold: int) -> str:
        self.horse_odds = all_gold / self.all_gold()
        return f'[{self.num + 1:02}]：{self.horse_odds: .2f}'

    # 马儿移动
    def move(self):
        # 计算前进步数
        mov_min, mov_max = config.base_move
        mov_min += self.ppt['speed'] - config.ppt_max + self.ppt['state']
        if config.is_max_add(self.ppt['state']):
            mov_max += self.ppt['speed']
        if self.ppt['persis'] < config.ppt_max and self.location >= config.persis_rate(self.ppt['persis']):
            mov_min -= config.ppt_max - self.ppt['persis']
            mov_max -= config.ppt_max - self.ppt['persis']
        if self.location >= config.explode_start:
            mov_min += self.ppt['explode']
            mov_max += self.ppt['explode']
        self.location_add = mov_max if mov_min >= mov_max else random.randint(mov_min, mov_max)
        self.location += self.location_add  # 更新马儿位置

    # 马儿在赛道上的位置显示
    def display(self, display_loc: int) -> str:
        display_num = f'[{self.num + 1:02}]'
        # 背景
        display_list = ['➖' for _ in range(config.display_len)]  # 跑道
        for i in range(config.display_len):  # 节点旗帜
            if not (display_loc - i) % config.display_gape:
                display_list[i] = '🚩'
        if display_loc >= config.length:
            display_list[display_loc - config.length] = '🏁'  # 终点旗帜
        if display_loc - self.location >= config.display_len:  # 马超出屏幕
            display_list[-1] = '❓'
            return display_num + ''.join(display_list)
        # 主体
        display_list[display_loc - self.location] = '🐎'  # 马
        for i in range(self.location_add):  # 烟
            if display_loc - self.location + 1 + i == config.display_len:  # 烟超出屏幕
                return display_num + ''.join(display_list)
            display_list[display_loc - self.location + 1 + i] = '💨'
        return display_num + ''.join(display_list)
