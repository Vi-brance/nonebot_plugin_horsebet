from pathlib import Path
from typing import Dict

import nonebot

# 跑道长度
setting_track_length = 20
# 每回合基础移动力范围
base_move = (1, 5)
# 马道数范围
horse_num = (2, 8)
# 超时允许重置最少时间，秒
setting_over_time = 120
# 插件地址
horsebet_path = Path()
# 签到金币范围
sign_gold = (20, 100)
# 信息存取地址
file = Path() / 'data' / 'horsebet_data.json'
# file = horsebet_path / 'data' / 'horsebet_data.json'
# 庄家支付赔金比率
setting_maker_gold = 0.2
# 赔率开始计算的阈值
setting_odd_start = 20

# dict中key转为int
def keyToInt(x: Dict) -> Dict:
    return {int(k): v for k, v in x.items()}
