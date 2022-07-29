from nonebot.adapters.onebot.v11 import GroupMessageEvent
import json
import random
from time import strftime

from .setting import *


# 玩家信息类
class Player:
    # 初始化
    def __init__(self, group: int):
        # 玩家信息：{key: user_id, value: {'nickname': str, 'gold': int, 'is_signed': bool}}
        self.players = {}
        # 所在群号
        self.group = group
        # 玩家信息文件目录
        self.file = player_file_path / 'player.json'

    # 读取玩家信息
    def load(self):
        self.file.parent.mkdir(exist_ok=True, parents=True)  # 创建文件夹
        if not self.file.exists():  # 新建玩家信息文件
            with open(self.file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
        with open(self.file, 'r', encoding='utf-8') as f:
            player_file: Dict = json.load(f)
            if str(self.group) in player_file.keys():
                self.players = keyToInt(player_file[str(self.group)])  # key转换为int，便于操作
            else:  # 该群没有玩家信息
                self.players = {}

    # 保存玩家信息
    def save(self):
        with open(self.file, 'r', encoding='utf-8') as f:
            player_file = json.load(f)  # 读取原信息
        player_file[str(self.group)] = self.players  # 替换该群玩家信息
        with open(self.file, 'w', encoding='utf-8') as f:
            json.dump(player_file, f, ensure_ascii=False, indent=4)  # 保存新信息

    # 初始化玩家信息
    def init_player_data(self, event: GroupMessageEvent):
        user_id = event.user_id
        nickname = event.sender.card if event.sender.card else event.sender.nickname
        self.load()
        if user_id not in self.players.keys():  # 没有玩家信息则初始化信息
            self.players[user_id] = {
                'nickname': nickname,
                'gold': 0,
                'is_signed': 0,
                'win': 0
            }

    # 玩家签到
    def sign(self, event: GroupMessageEvent) -> int:
        self.load()
        self.init_player_data(event)  # 初始化新玩家信息
        uid = event.user_id
        if self.players[uid]['is_signed'] == int(strftime('%j', cur_time)):  # 已签到
            return -1
        gold = random.randint(sign_gold[0], sign_gold[1])
        self.players[uid]['gold'] += gold
        self.players[uid]['is_signed'] = int(strftime('%j', cur_time))
        self.save()
        return gold

    # 返回玩家拥有金币
    def get_gold(self, uid: int) -> int:
        self.load()
        return self.players[uid]['gold']

    # 结算玩家金币    
    def change_gold(self, uid: int, gold: int):
        self.load()
        self.players[uid]['gold'] += gold
        self.save()

    # 玩家赢场次计数
    def add_win(self, uid: int):
        self.load()
        self.players[uid]['win'] += 1
        self.save()

    # 显示玩家拥有的金币数
    def display_gold(self, uid: int) -> str:
        self.load()
        if uid not in self.players.keys():
            return '你未在本系统中登录过'
        cur_player = self.players[uid]
        return f"{cur_player['nickname']} 有 {cur_player['gold']} 枚金币"

    # 显示玩家金币排行
    def display_gold_rank(self) -> str:
        self.load()
        rank = []
        for player in self.players.values():
            rank.append({'nickname': player['nickname'], 'gold': player['gold']})
        rank = sorted(rank, key=lambda x: x['gold'], reverse=True)
        display = ''
        for i in range(len(rank)):
            if i == 5:
                return display[1: len(display)]
            display += '\n' + f'{rank[i]["gold"]:4}：{rank[i]["nickname"]}'
        return display[1: len(display)]
