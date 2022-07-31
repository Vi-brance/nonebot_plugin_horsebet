from typing import List, Dict

from .horse import horse
from .config import race_config as config


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
        self.gold = config.base_gold
        # 创建马场的玩家id
        self.host_id = uid
        # 下注玩家数
        self.player_num = 0

        # 分配每匹马下注的初始金额
        for i in self.horses:
            i.base_gold = int(
                self.gold * i.get_ppt() / self.get_ppts())
            i.odds(self.gold)

    # 返回所有马匹总属性
    def get_ppts(self) -> int:
        ppt = 0
        for i in self.horses:
            ppt += i.get_ppt()
        return ppt

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
        if self.horses[bet_horse].add_coin(uid, gold):
            return True
        self.player_num += 1
        return False

    # 马儿移动
    def move(self):
        for i in self.horses:
            i.move()

    # 获取胜者信息
    def get_winner(self) -> List:
        winner = []
        max_track = 0
        for x in self.horses:
            if x.is_winner():
                if x.location > max_track:
                    winner.clear()
                    max_track = x.location
                winner.append(x.num)
        return winner

    # 显示马匹属性面板
    def display_horse_ppt(self) -> str:
        display = '编号 | 速度 | 持久 | 爆发 | 状态'
        for x in self.horses:
            display += (
                f'\n [{x.num + 1:02}]'
                f' | {config.ppt_name(x.ppt["speed"])}'
                f' | {config.ppt_name(x.ppt["persis"])}'
                f' | {config.ppt_name(x.ppt["explode"])}'
                f' | {config.ppt_name(x.ppt["state"])}'
            )
        return display

    # 显示赔率信息
    def show_odds(self) -> str:
        odds = ''
        for i in range(len(self.horses)):
            odds += '\n' + \
                    self.horses[i].odds(int(self.gold * (1 - config.maker_rate)))
        return odds[1:]

    # 显示马场界面
    def display(self) -> str:
        display = ''
        display_loc = max(x.location for x in self.horses) + 2
        for i in range(len(self.horses)):
            display += '\n' + self.horses[i].display(display_loc)  # 每行为每匹马的路线
        return display[1:]
