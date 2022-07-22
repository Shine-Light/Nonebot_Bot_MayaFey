"""
@Author: Shine_Light
@Version: 1.0
@Date: 2022/3/27 18:01
"""
from pathlib import Path

# 插件配置总目录
config_path = Path() / "config"
# 资源目录
res_path = Path() / "resource"
# 插件总目录
plugin_path = Path() / "content" / "plugins"
# 字体总目录
font_path = res_path / "font"
# 文本总目录
txt_path = res_path / "txt"
# 音频总目录
audio_path = res_path / "audio"
# 视频总目录
video_path = res_path / "video"
# 图片总目录
img_path = res_path / "img"
# 数据库总目录
database_path = res_path / "database"
# 运势资源目录
fortune_resource_path = res_path / "fortune"
# 版本文件
version_path = Path() / "__version__"

# 翻译文件
translate_path = config_path / "translate.json"
# 词云插件配置目录
admin_path = config_path / "word_cloud"
# 词云插件配置
word_path = config_path / "word_cloud" / "word_config.txt"
# 聊天记录目录
words_contents_path = txt_path / "words"
# 词云资源目录
re_wordcloud_path = img_path / "word_cloud"
# 词云图片目录
re_img_path = re_wordcloud_path / "img"
# 词云背景目录
wordcloud_bg_path = re_wordcloud_path / "background"
# 词云字体
ttf_name = font_path / "msyhblod.ttf"
group_message_data_path = config_path / "group_msg_data"
# 内置违禁词
limit_word_path = txt_path / "违禁词.txt"
limit_word_path_easy = txt_path / "违禁词_简单.txt"
# 自定义违禁词配置目录
word_list_urls = config_path / "ban_word"
# 违禁词等级文件
level_path = word_list_urls / "level.json"
# 插件控制配置目录
control_path = config_path / "control"
# 入群欢迎文本
welcome_path_base = config_path / "welcome"
# 回归欢迎文本
back_path_base = config_path / "back"
# 插件调用统计目录
total_base = config_path / "total"
# 插件调用统计_不录入
total_unable = config_path / "total" / "unable.txt"
# 自定义问答配置目录
question_base = config_path / "question"
# 权限控制配置目录
permission_base = config_path / "permission"
# 权限控制普通配置
permission_common_base = permission_base / "common"
# 权限控制特殊配置
permission_special_base = permission_base / "special"
# 表情包制作配置
memes_path = config_path / "memes"
# 更新插件目录
update_path = plugin_path / "update"
# 更新插件配置
update_cfg_path = config_path / "update"
# 更新检测文件
updating_path = update_cfg_path / "updating.json"
# 表结构SQL
sql_base = database_path / "bot.sql"
# 不可设置插件列表
unset_path = control_path / "unset.txt"
# Epic限免资讯目录
epicFree_path = config_path / "epic"
# 早安配置目录
morning_path = config_path / "morning"
# 早晚安配置文件
morning_config_path = config_path / "morning" / "config.json"
# 早晚安数据文件
morning_data_path = config_path / "morning" / "data.json"
# 每日运势配置目录
fortune_path = config_path / "fortune"
# 每日运势配置文件
fortune_config_path = fortune_path / "fortune_config.json"
# copywriting文件
fortune_copywriting_path = res_path / "fortune" / "copywriting.json"
# 每日运势输出命令
fortune_out_path = res_path / "fortune" / "out"
# 记过配置目录
demerit_path = config_path / "demerit"
# 机器人开启配置命令
enable_path = config_path / "enable"
# 机器人开启配置文件
enable_config_path = config_path / "enable" / "config.json"
# 折磨群友配置目录
torment_path = config_path / "torment"
# 折磨群友配置文件
torment_config_path = torment_path / "config.json"
# 重启配置目录
reboot_path = config_path / "reboot"
# 重启配置文件
reboot_config_path = reboot_path / "reboot.json"


# 俄罗斯轮盘游戏配置
russian_path = config_path / "russian"
