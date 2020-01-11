from pypinyin import pinyin, lazy_pinyin, Style
from pyhanlp import *

if __name__ == '__main__':
    print(pinyin('这是中文', style=Style.NORMAL))
    print(HanLP.segment('上海自来水来自海上'))
