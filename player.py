import json
import random
from typing import Tuple
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from .setting import *


# 玩家信息类
class player:
    # 初始化
    def __init__(self, group: int):
        self.players = {}  # 玩家信息
        self.group = group
        self.file = player_file_path

    # 读取json信息
    def load(self):
        self.file.parent.mkdir(exist_ok=True, parents=True)
        if not self.file.exists():  # 文件不存在时新建文件
            with open(self.file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
        with open(self.file, 'r', encoding='utf-8') as f:
            players = json.load(f)
            if str(self.group) not in players.keys():  # 该群没有玩家信息
                self.players = {}
            else:
                self.players = keyToInt(players[str(self.group)])

    # 初始化玩家信息
    def init_player_data(self, event: GroupMessageEvent):
        user_id = event.user_id
        nickname = event.sender.card if event.sender.card else event.sender.nickname
        self.load()
        if user_id not in self.players.keys():  # 没有玩家信息则初始化信息
            self.players[user_id] = {
                'nickname': nickname,
                'gold': 0,
                'is_signed': False
            }
    
    # 玩家签到
    def sign(self, event: GroupMessageEvent) -> Tuple[str, int]:
        self.init_player_data(event)  # 若没有玩家信息则先初始化
        uid = event.user_id
        if self.players[uid]['is_signed'] is True:  # 已签到
            return '今日已签到', -1
        gold = random.randint(sign_gold[0], sign_gold[1])
        self.players[uid]['gold'] += gold
        self.players[uid]['is_signed'] = True
        self.save()
        return f'签到成功，你获得了 {gold} 枚金币', gold
    
    # 保存玩家信息
    def save(self):
        with open(self.file, 'r', encoding='utf-8') as f:
            players = json.load(f)  # 读取原信息
        players[str(self.group)] = self.players  # 替换原该群玩家信息
        with open(self.file, 'w', encoding='utf-8') as f:
            json.dump(players, f, ensure_ascii=False, indent=4)  # 保存新信息
    
    # 返回玩家拥有金币
    def get_gold(self, uid: int) -> int:
        self.load()
        return self.players[uid]['gold']

    # 结算玩家金币    
    def add_gold(self, uid: int, gold: int):
        self.players[uid]['gold'] += gold
        self.save()

    def display_gold(self, uid: int) -> str:
        if uid not in self.players.keys():
            return '你未在本系统中登录过'
        cur_player = self.players[uid]
        return f"{cur_player['nickname']} 的金币有 {cur_player['gold']} 枚"
