import pathlib
from typing import Dict, Tuple
import time

# 当前时间
cur_time = time.localtime()
# 跑道长度
track_length = 50
# 跑道显示长度
track_display_length = 11
# 跑道标记间隔
track_gape = 10

# 基础前进
base_move = (1, 3)
# 爆发触发距离在赛道总长度的比例
explode_start = 0.2
# 属性生成概率
generate_attribute = [1, 1, 1, 2, 2, 3]
# 属性名称映射
attribute_name = ('一般', '良好', '优秀')
# 属性总值范围
attribute_range = (6, 10)
# 基础触发成功率
base_state = 35
# 基础持久
base_persis = 20

# 马道数范围
setting_horse_num = (8, 10)
# 签到金币范围
sign_gold = (50, 100)
# 信息存取地址
player_file_path = pathlib.Path() / 'data' / 'horseBet'
# 系统抽成
setting_maker_rate = 0.2
# 奖池基础金币
setting_base_gold = 5000


# dict中key转为int
def keyToInt(x: Dict) -> Dict:
    return {int(k): v for k, v in x.items()}


# 判断字符串是否是数字
def is_number(s) -> Tuple[bool, float]:
    try:
        return True, float(s)
    except ValueError:
        pass
    try:
        import unicodedata
        return True, unicodedata.numeric(s)
    except (TypeError, ValueError):
        pass
    return False, 0
