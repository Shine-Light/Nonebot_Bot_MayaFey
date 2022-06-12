from nonebot import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from typing import Union, List, Tuple
from utils import path
import datetime
from .download import get_preset_config
from ..withdraw import add_target
try:
    import ujson as json
except ModuleNotFoundError:
    import json

data_file = path.morning_data_path
config_file = path.morning_config_path

mor_switcher = {
    '时限': 'get_up_intime',
    '多重起床': 'multi_get_up',
    '超级亢奋': 'super_get_up'
}

nig_switcher = {
    '时限': 'sleep_intime',
    '优质睡眠': 'good_sleep',
    '深度睡眠': 'deep_sleep'
}


class MorningManager:
    def __init__(self):
        self.user_data = {}
        self.config = {}
        self.data_file = data_file
        self.config_file = config_file

        if not data_file.exists():
            with open(data_file, "w+", encoding="utf-8") as f:
                f.write(json.dumps(dict()))
                f.close()

        if data_file.exists():
            with open(data_file, "r", encoding="utf-8") as f:
                self.user_data = json.load(f)

        if not config_file.exists():
            logger.info("Downloading preset morning config resource...")
            with open(config_file, "w+", encoding="utf-8") as f:
                f.write(json.dumps(dict()))
                f.close()
            
            get_preset_config(config_file)
        
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                self.config = json.load(f)

    '''
        初始化用户数据
    '''
    def _init_data(self, group_id: str) -> None:
        if group_id not in self.user_data.keys():
            self.user_data[group_id] = {
                "today_count": {
                    "morning": 0,
                    "night": 0
                }
            }

            self.save_data()

    '''
        查看当前设置
    '''
    def get_current_config(self) -> str:
        msg = '早安晚安设置如下：'
        # morning_config
        get_up_intime = self.config['morning']['get_up_intime']['enable']
        if get_up_intime:
            msg = msg + '\n是否要求规定时间内起床：是\n - 最早允许起床时间：' + str(self.config['morning']['get_up_intime']['early_time']) + '点\n - 最晚允许起床时间：' + str(self.config['morning']['get_up_intime']['late_time']) + '点'
        else:
            msg = msg + '\n是否要求规定时间内起床：否'
        multi_get_up = self.config['morning']['multi_get_up']['enable']
        if multi_get_up:
            msg = msg + '\n是否允许连续多次起床：是'
        else:
            msg = msg + '\n是否允许连续多次起床：否\n - 允许的最短起床间隔：' + str(self.config['morning']['multi_get_up']['interval']) + '小时'
        super_get_up = self.config['morning']['super_get_up']['enable']
        if super_get_up:
            msg = msg + '\n是否允许超级亢奋(即睡眠时长很短)：是'
        else:
            msg = msg + '\n是否允许超级亢奋(即睡眠时长很短)：否\n - 允许的最短睡觉时长：' + str(self.config['morning']['super_get_up']['interval']) + '小时'
        # night_config
        sleep_intime = self.config['night']['sleep_intime']['enable']
        if sleep_intime:
            msg = msg + '\n是否要求规定时间内睡觉：是\n - 最早允许睡觉时间：' + str(self.config['night']['sleep_intime']['early_time']) + '点\n - 最晚允许睡觉时间：第二天早上' + str(self.config['night']['sleep_intime']['late_time']) + '点'
        else:
            msg = msg + '\n是否要求规定时间内睡觉：否'
        good_sleep = self.config['night']['good_sleep']['enable']
        if good_sleep:
            msg = msg + '\n是否开启优质睡眠：是'
        else:
            msg = msg + '\n是否开启优质睡眠：否\n - 允许的最短优质睡眠：' + str(self.config['night']['good_sleep']['interval']) + '小时'
        deep_sleep = self.config['night']['deep_sleep']['enable']
        if deep_sleep:
            msg = msg + '\n是否允许深度睡眠(即清醒时长很短)：是 '
        else:
            msg = msg + '\n是否允许深度睡眠(即清醒时长很短)：否\n - 允许的最短清醒时长：' + str(self.config['night']['deep_sleep']['interval']) + '小时'
        return msg + add_target(60)

# ------------------------------ config ------------------------------ #

    # 开启或关闭
    def change_config(self, day_or_night: str, server: str, enable: bool) -> str:
        try:
            self.config[day_or_night][server]["enable"] = enable
            self.save_config()
            msg = "配置更新成功！"
        except Exception as e:
            msg = f"配置更新失败！错误原因{e}"

        return msg

    # 更改时间或间隔
    def change_set_time(self, *args) -> str:
        try:
            day_or_night = args[0]
            server = args[1]
            if server == "get_up_intime" or server == "sleep_intime":
                early_time = args[2]
                late_time = args[3]
                self.config[day_or_night][server]["early_time"] = early_time
                self.config[day_or_night][server]["late_time"] = late_time
            else:
                interval = args[2]
                self.config[day_or_night][server]["interval"] = interval
            
            self.save_config()
            msg = "配置更新成功！"

        except Exception as e:
            msg = f"配置更新失败！错误原因{e}"
        
        return msg

    def save_config(self) -> None:
        '''
            保存配置数据
        '''
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)
    
    def save_data(self) -> None:
        '''
            保存用户数据
        '''
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.user_data, f, ensure_ascii=False, indent=4)
    
    def reset_data(self) -> None:
        '''
            刷新群一天早晚安数据
        '''
        for group_id in self.user_data.keys():
            self.user_data[group_id]['today_count']['morning'] = 0
            self.user_data[group_id]['today_count']['night'] = 0
        
        self.save_data()

    def morning_config(self, args: List) -> str:
        if args[0] not in mor_switcher.keys():
            msg = f'在早安设置中未找到"{args[0]}"，请确保输入正确，目前可选值有:'
            for key in mor_switcher.keys():
                msg += " " + key
            return msg
        
        server = mor_switcher[args[0]]
        if server == "get_up_intime":
            try:
                early_time = int(args[1])
                late_time = int(args[2])
            except:
                msg = "获取参数错误，请确保你输入了正确的命令，样例参考：\n[早安设置 时限 1 18] 即1点到18点期间可以起床，数字会自动强制取整"
                return msg
            
            if early_time < 0 or early_time > 24 or late_time < 0 or late_time > 24:
                msg = "错误！您设置的时间未在0-24之间，要求：0 <= 时间 <= 24"
                return msg

            msg = self.change_set_time("morning", server, early_time, late_time)
        else:
            try:
                interval = int(args[1])
            except:
                msg = "获取参数错误，请确保你输入了正确的命令，样例参考：\n[早安设置 多重起床 6] 即最小间隔6小时，数字会自动强制取整"
                return msg
            if interval < 0 or interval > 24:
                msg = "错误！您设置的时间间隔未在0-24之间，要求：0 <= 时间 <= 24"
                return msg

            msg = self.change_set_time("morning", server, interval)
        
        return msg

    def morning_switch(self, mor_server: str, enable: bool) -> str:
        if mor_server not in mor_switcher.keys():
            msg = f'在早安设置中未找到"{mor_server}"，请确保输入正确，目前可选值有:'
            for key in mor_switcher.keys():
                msg += " " + key
        else:   
            server = mor_switcher[mor_server]
            msg = self.change_config("morning", server, enable)
        
        return msg

    def night_config(self, args: List) -> str:
        if args[0] not in nig_switcher.keys():
            msg = f'在晚安设置中未找到"{args[0]}"，请确保输入正确，目前可选值有:'
            for key in nig_switcher.keys():
                msg += " " + key
            return msg
        
        server = nig_switcher[args[0]]
        if server == "sleep_intime":
            try:
                early_time = int(args[1])
                late_time = int(args[2])
            except:
                msg = "获取参数错误，请确保你输入了正确的命令，样例参考：\n[晚安设置 时限 18 6] 即18点到第二天6点期间可以晚安，数字会自动强制取整，注意第二个数字一定是第二天的时间"
                return msg
            
            if early_time < 0 or early_time > 24 or late_time < 0 or late_time > 24:
                msg = "错误！您设置的时间未在0-24之间，要求：0 <= 时间 <= 24"
                return msg

            msg = self.change_set_time("night", server, early_time, late_time)
        else:
            try:
                interval = int(args[1])
            except:
                msg = "获取参数错误，请确保你输入了正确的命令，样例参考：\n[晚安设置 深度睡眠 6] 即最小间隔6小时，数字会自动强制取整"
                return msg
            if interval < 0 or interval > 24:
                msg = "错误！您设置的时间间隔未在0-24之间，要求：0 <= 时间 <= 24"
                return msg

            msg = self.change_set_time("night", server, interval)
        
        return msg

    def night_switch(self, nig_server: str, enable: bool) -> str:
        if nig_server not in nig_switcher.keys():
            msg = f'在晚安设置中未找到"{nig_server}"，请确保输入正确，目前可选值有:'
            for key in nig_switcher.keys():
                msg += " " + key
        else:   
            server = nig_switcher[nig_server]
            msg = self.change_config("night", server, enable)
        
        return msg

# ------------------------------ morning judgement------------------------------ #

    # 判断早安时间
    @staticmethod
    def judge_mor_time(early_time_tmp: str, late_time_tmp: str, now_time: datetime.datetime) -> bool:
        early_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + f' {early_time_tmp}:00:00', '%Y-%m-%d %H:%M:%S')
        late_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + f' {late_time_tmp}:00:00', '%Y-%m-%d %H:%M:%S')
        if not now_time >= early_time or not now_time <= late_time:
            return False
        return True

    # 判断多次早安
    def judge_have_mor(self, group_id: str, user_id: str, now_time: datetime.datetime, interval: str) -> bool:
        get_up_time = datetime.datetime.strptime(self.user_data[group_id][user_id]['get_up_time'], '%Y-%m-%d %H:%M:%S')
        # 上次起床时间和现在时间相差不超过f'{interval}'小时
        if get_up_time + datetime.timedelta(hours = int(interval)) > now_time:
            return True
        return False

    # 判断超级亢奋
    def judge_super_get_up(self, group_id: str, user_id: str, now_time: datetime.datetime, interval: str) -> bool:
        sleep_time = datetime.datetime.strptime(self.user_data[group_id][user_id]['sleep_time'], '%Y-%m-%d %H:%M:%S')
        # 上次睡觉时间和现在时间相差不超过f'{interval}'小时
        if sleep_time + datetime.timedelta(hours = int(interval)) > now_time:
            return True
        return False

    # 进行早安并更新数据
    def morning_and_update(self, now_time: datetime.datetime, group_id: str, user_id: str) -> Tuple[str, Union[int, str]]:
        # 起床并写数据
        sleep_time = datetime.datetime.strptime(self.user_data[group_id][user_id]['sleep_time'], '%Y-%m-%d %H:%M:%S')
        in_sleep = now_time - sleep_time
        secs = in_sleep.total_seconds()
        day = secs // (3600 * 24)
        hour = (secs - day * 3600 * 24) // 3600
        minute = (secs - day * 3600 * 24 - hour * 3600) // 60
        second = secs - day * 3600 * 24 - hour * 3600 - minute * 60
        # 睡觉时间小于24小时就同时给出睡眠时长
        in_sleep_tmp = 0
        if day == 0:
            in_sleep_tmp = str(int(hour)) + '时' + str(int(minute)) + '分' + str(int(second)) + '秒'
        self.user_data[group_id][user_id]['get_up_time'] = now_time.strftime("%Y-%m-%d %H:%M:%S")
        self.user_data[group_id][user_id]['morning_count'] = int(self.user_data[group_id][user_id]['morning_count']) + 1
        # 判断是今天第几个起床的
        self.user_data[group_id]['today_count']['morning'] = int(self.user_data[group_id]['today_count']['morning']) + 1
        self.save_data()

        return self.user_data[group_id]['today_count']['morning'], in_sleep_tmp

    # 返回早安信息
    def get_morning_msg(self, sex_str: str, event: GroupMessageEvent) -> str:
        user_id = str(event.user_id)
        group_id = str(event.group_id)
        
        # 若开启规定时间早安，则判断该时间是否允许早安
        now_time = datetime.datetime.now()
        if self.config['morning']['get_up_intime']['enable']:
            early_time_tmp = self.config['morning']['get_up_intime']['early_time']
            late_time_tmp = self.config['morning']['get_up_intime']['late_time']
            if not MorningManager.judge_mor_time(early_time_tmp, late_time_tmp, now_time):
                msg = f'现在不能早安哦，可以早安的时间为{early_time_tmp}时到{late_time_tmp}时~'
                return msg

        self._init_data(group_id)
        
        # 当数据里有过这个人的信息就判断:
        if user_id in self.user_data[group_id].keys():
            
            # 若关闭连续多次早安，则判断在设定时间内是否多次早安
            if not self.config['morning']['multi_get_up']['enable'] and self.user_data[group_id][user_id]['get_up_time'] != 0:
                interval = self.config['morning']['multi_get_up']['interval']
                if self.judge_have_mor(group_id, user_id, now_time, interval):
                    msg = f'{interval}小时内你已经早安过了哦~'
                    return msg
            
            # 若关闭超级亢奋，则判断睡眠时长是否小于设定时间
            if not self.config['morning']['super_get_up']['enable']:
                interval = self.config['morning']['super_get_up']['interval']
                if self.judge_super_get_up(group_id, user_id, now_time, interval):
                    msg = f'你可猝死算了吧？现在不能早安哦~'
                    return msg
            # 若没有说明他还没睡过觉呢
        else:
            msg = '你还没睡过觉呢！不能早安哦~'
            return msg

        # 当前面条件均符合的时候，允许早安
        num, in_sleep = self.morning_and_update(now_time, group_id, user_id)
        if in_sleep == 0:
            msg = f'早安成功！你是今天第{num}个起床的{sex_str}！'
        else:
            msg = f'早安成功！你的睡眠时长为{in_sleep}，\n你是今天第{num}个起床的{sex_str}！'
        return msg

# ------------------------------ night judgement ------------------------------ #

    # 判断晚安时间
    @staticmethod
    def judge_sle_time(early_time_tmp: str, late_time_tmp: str, now_time: datetime.datetime) -> bool:
        early_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + f' {early_time_tmp}:00:00', '%Y-%m-%d %H:%M:%S')
        late_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + f' {late_time_tmp}:00:00', '%Y-%m-%d %H:%M:%S')
        if now_time < early_time and now_time > late_time:
            return False
        return True

    # 判断多次晚安
    def judge_have_sle(self, group_id: str, user_id: str, now_time: datetime.datetime, interval: str) -> bool:
        sleep_time = datetime.datetime.strptime(self.user_data[group_id][user_id]['sleep_time'], '%Y-%m-%d %H:%M:%S')
        # 上次晚安时间和现在时间相差不超过f'{interval}'小时
        if sleep_time + datetime.timedelta(hours = int(interval)) > now_time:
            return True
        return False

    # 判断深度睡眠
    def judge_deep_sleep(self, group_id: str, user_id: str, now_time: datetime.datetime, interval: str) -> bool:
        get_up_time = datetime.datetime.strptime(self.user_data[group_id][user_id]['get_up_time'], '%Y-%m-%d %H:%M:%S')
        # 上次起床时间和现在时间相差不超过f'{interval}'小时
        if get_up_time + datetime.timedelta(hours = int(interval)) > now_time:
            return True
        return False

    # 进行晚安并更新数据
    def night_and_update(self, now_time: datetime.datetime, group_id: str, user_id: str) -> Tuple[str, Union[int, str]]:
        # 若之前没有数据就直接创建一个
        if user_id not in self.user_data[group_id].keys():
            self.user_data[group_id][user_id] = {
                "morning_count": 0,
                "get_up_time": 0,
                "night_count": 1,
                "sleep_time": now_time.strftime("%Y-%m-%d %H:%M:%S")
            }
        # 若有就更新数据
        else:
            self.user_data[group_id][user_id]['sleep_time'] = now_time.strftime("%Y-%m-%d %H:%M:%S")
            self.user_data[group_id][user_id]['night_count'] = int(self.user_data[group_id][user_id]['night_count']) + 1
        # 当上次起床时间不是初始值0,就计算清醒的时长
        in_day_tmp = 0
        if self.user_data[group_id][user_id]['get_up_time'] != 0:
            get_up_time = datetime.datetime.strptime(self.user_data[group_id][user_id]['get_up_time'], '%Y-%m-%d %H:%M:%S')
            in_day = now_time - get_up_time
            secs = in_day.total_seconds()
            day = secs // (3600 * 24)
            hour = (secs - day * 3600 * 24) // 3600
            minute = (secs - day * 3600 * 24 - hour * 3600) // 60
            second = secs - day * 3600 * 24 - hour * 3600 - minute * 60
            if day == 0:
                in_day_tmp = str(int(hour)) + '时' + str(int(minute)) + '分' + str(int(second)) + '秒'
        # 判断是今天第几个睡觉的
        self.user_data[group_id]['today_count']['night'] = int(self.user_data[group_id]['today_count']['night']) + 1
        self.save_data()

        return self.user_data[group_id]['today_count']['night'], in_day_tmp

    # 返回晚安信息
    def get_night_msg(self, sex_str: str, event: GroupMessageEvent) -> str:
        user_id = str(event.user_id)
        group_id = str(event.group_id)

        # 若开启规定时间晚安，则判断该时间是否允许晚安
        now_time = datetime.datetime.now()
        if self.config['night']['sleep_intime']['enable']:
            early_time_tmp = self.config['night']['sleep_intime']['early_time']
            late_time_tmp = self.config['night']['sleep_intime']['late_time']
            if not MorningManager.judge_sle_time(early_time_tmp, late_time_tmp, now_time):
                msg = f'现在不能晚安哦，可以晚安的时间为{early_time_tmp}时到第二天早上{late_time_tmp}时~'
                return msg

        self._init_data(group_id)

        # 当数据里有过这个人的信息就判断:
        if user_id in self.user_data[group_id].keys():

            # 若开启优质睡眠，则判断在设定时间内是否多次晚安
            if self.config['night']['good_sleep']['enable']:
                interval = self.config['night']['good_sleep']['interval']
                if self.judge_have_sle(group_id, user_id, now_time, interval):
                    msg = f'{interval}小时内你已经晚安过了哦~'
                    return msg
            
            # 若关闭深度睡眠，则判断不在睡觉的时长是否小于设定时长
            if not self.config['night']['deep_sleep']['enable'] and self.user_data[group_id][user_id]['get_up_time'] != 0:
                interval = self.config['night']['deep_sleep']['interval']
                if self.judge_deep_sleep(group_id, user_id, now_time, interval):
                    msg = f'睡这么久还不够？现在不能晚安哦~'
                    return msg

        # 当数据里没有这个人或者前面条件均符合的时候，允许晚安
        num, in_day = self.night_and_update(now_time, group_id, user_id)
        if in_day == 0:
            msg = f'晚安成功！你是今天第{num}个睡觉的{sex_str}！'
        else:
            msg = f'晚安成功！你今天的清醒时长为{in_day}，\n你是今天第{num}个睡觉的{sex_str}！'
        return msg
    
# ------------------------------ routine ------------------------------ #

    def get_routine(self, event: GroupMessageEvent) -> str:
        group_id = str(event.group_id)
        user_id = str(event.user_id)

        self._init_data(group_id)
        if user_id in self.user_data[group_id].keys():
            get_up_time = self.user_data[group_id][user_id]['get_up_time']
            sleep_time = self.user_data[group_id][user_id]['sleep_time']
            morning_count = self.user_data[group_id][user_id]['morning_count']
            night_count = self.user_data[group_id][user_id]['night_count']
            msg = f'您的作息数据如下：'
            msg += f'\n最近一次起床时间为{get_up_time}'
            msg += f'\n最近一次睡觉时间为{sleep_time}'
            msg += f'\n一共起床了{morning_count}次'
            msg += f'\n一共睡觉了{night_count}次'
        else:
            msg = '您还没有睡觉起床过呢！暂无数据~'
        
        return msg

    def get_group_routine(self, event: GroupMessageEvent) -> str:
        group_id = str(event.group_id)

        self._init_data(group_id)
        moring_count = self.user_data[group_id]['today_count']['morning']
        night_count = self.user_data[group_id]['today_count']['night']
        msg = f'今天已经有{moring_count}位群友起床了，{night_count}位群友睡觉了~'

        return msg


morning_manager = MorningManager()
