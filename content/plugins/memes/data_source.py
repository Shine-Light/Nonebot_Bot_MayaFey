from .utils import Meme, GifMeme
from .normal_memes import *
from .gif_subtitle_memes import *


memes: List[Meme] = [
    Meme("luxunsay", luxunsay, ("鲁迅说", "鲁迅说过"), r"鲁迅说过?"),
    Meme("nokia", nokia, ("诺基亚", "有内鬼")),
    Meme("goodnews", goodnews, ("喜报",)),
    Meme("holdgrudge", holdgrudge, ("记仇",)),
    Meme("fanatic", fanatic, ("狂爱", "狂粉")),
    Meme("murmur", murmur, ("低语",)),
    Meme("shutup", shutup, ("别说了",)),
    Meme("slap", slap, ("一巴掌",)),
    Meme("imprison", imprison, ("坐牢",)),
    Meme("scroll", scroll, ("滚屏",)),
    Meme("high_EQ", high_EQ, ("低情商xx高情商xx",), r"低情商(?P<left>.*?)\s+高情商(?P<right>.*)"),
    Meme("wujing", wujing, ("吴京xx中国xx",), r"吴京[\s:：]*(?P<left>.*?)中国(?P<right>.*)"),
    Meme("slogan", slogan, ("口号",)),
    Meme("wakeup", wakeup, ("xx起来了",), r"(?P<text>.*?)起来了"),
    Meme("raisesign", raisesign, ("举牌",)),
    Meme("psyduck", psyduck, ("可达鸭",)),
    Meme("scratchoff", scratchoff, ("刮刮乐",)),
    GifMeme("wangjingze", wangjingze, ("王境泽",)),
    GifMeme("weisuoyuwei", weisuoyuwei, ("为所欲为",)),
    GifMeme("chanshenzi", chanshenzi, ("馋身子",)),
    GifMeme("qiegewala", qiegewala, ("切格瓦拉",)),
    GifMeme("shuifandui", shuifandui, ("谁反对",)),
    GifMeme("zengxiaoxian", zengxiaoxian, ("曾小贤",)),
    GifMeme("yalidaye", yalidaye, ("压力大爷",)),
    GifMeme("nihaosaoa", nihaosaoa, ("你好骚啊",)),
    GifMeme("shishilani", shishilani, ("食屎啦你",)),
    GifMeme("wunian", wunian, ("五年怎么过的",)),
]

memes = [meme for meme in memes if meme.name not in memes_config.memes_disabled_list]
