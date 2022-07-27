from pathlib import Path
from typing import Dict


# 跑道长度
setting_track_length = 20
# 每回合基础移动力范围
base_move = (1, 5)
# 马儿脚力范围
setting_horse_buff = (-3, 3)
# 马道数范围
setting_horse_num = (2, 8)
# 超时允许重置最少时间，秒
setting_over_time = 120
# 签到金币范围
sign_gold = (20, 100)
# 信息存取地址
player_file_path = Path() / 'data' / 'horseBet' / 'player_data.json'
# 系统抽成
setting_maker_rate = 0.2
# 奖池基础金币
setting_base_gold = 5000


# dict中key转为int
def keyToInt(x: Dict) -> Dict:
    return {int(k): v for k, v in x.items()}
