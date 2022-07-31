import random
import pathlib
import time
from pydantic import BaseSettings, Extra


# 配置类
class Config(BaseSettings, extra=Extra.ignore):
    # race类的config
    class race:
        def __init__(self):
            # 系统抽成
            self.maker_rate = 0.2
            # 初始奖池金币数
            self.base_gold = 5000

        # 属性点数对应的表达
        def ppt_name(self, ppt: int) -> str:
            name_list = ('一般', '良好', '优秀')
            return name_list[ppt - 1]

    # horse类的config
    class horse:
        def __init__(self):
            # 赛道总长度
            self.length = 50
            # 屏幕宽度
            self.display_len = 11
            # 标记节点间隔
            self.display_gape = 10
            # 基础移动
            self.base_move = (1, 3)
            # 爆发触发的位置
            self.explode_start = int(0.8 * self.length)
            # 属性点上限
            self.ppt_max = 3

        # 随机生成属性点，点数越高概率越低
        def generate_ppt(self) -> int:
            generate_list = []
            for i in reversed(range(1, self.ppt_max + 1)):
                for _ in range(self.ppt_max - i + 1):
                    generate_list.append(i)
            return random.choice(generate_list)

        # 属性点数和是否在范围内
        def ppt_in_range(self, x: int) -> bool:
            return x in range(6, 11)

        # 速度属性是否增强
        def is_max_add(self, state: int) -> bool:
            per = random.randint(1, 100)
            return True if per <= 35 + state * 15 else False

        # 持久属性有效距离
        def persis_rate(self, persis: int) -> int:
            return int(self.length * (20 + persis * 10) / 100)

    # player类的config
    class player:
        def __init__(self):
            # 签到天数
            self.cur_time = int(time.strftime('%j', time.localtime()))
            # 保存文件目录
            self.file_path = pathlib.Path() / 'data' / 'horseBet'

        # 金币范围
        def sign_gold(self) -> int:
            return random.randint(50, 100)


# 三个类的配置接口
race_config = Config.race()
horse_config = Config.horse()
player_config = Config.player()
