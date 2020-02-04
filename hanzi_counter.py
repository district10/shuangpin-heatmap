import pygal
import pypinyin
from pyhanlp import *
from typing import Union, Set, Dict, List, Any, Tuple, Optional
from svg import SVG
import os
import sys
import json
import argparse
import tempfile
from collections import defaultdict
import numpy as np
import re
from pprint import pprint

PWD = os.path.abspath(os.path.dirname(__file__))


def draw_svg(svg_path, title, counter):
    line_chart = pygal.Line()
    line_chart.add(title, [kv[1] for kv in counter])
    line_chart.render_to_file(svg_path)


pinyin2shengyun_cache = {
    'a': ['a', 'a'],
    'o': ['o', 'o'],
    'e': ['e', 'e'],
    'ai': ['a', 'i'],
    'an': ['a', 'n'],
    'ao': ['a', 'o'],
    'ei': ['e', 'i'],
    'en': ['e', 'n'],
    'er': ['e', 'r'],
    'ou': ['o', 'u'],
    'ang': ['a', 'h'],
    'eng': ['e', 'g'],
}
def pinyin2shengyun(pinyin):
    if pinyin in pinyin2shengyun_cache:
        return pinyin2shengyun_cache[pinyin]
    shengs = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'w', 'x', 'y', 'z', 'ch', 'sh', 'zh'] 
    yuns = ['a', 'ai', 'an', 'ang', 'ao', 'e', 'ei', 'en', 'eng', 'i', 'ia', 'ian', 'iang', 'iao', 'ie', 'iong', 'in', 'ing', 'iu', 'o', 'ong', 'ou', 'u', 'ua', 'uai', 'uan', 'uang', 'ue', 'ui', 'un', 'uo', 'v', 've']
    for yun in yuns:
        if not pinyin.endswith(yun):
            continue
        idx = len(pinyin) - len(yun)
        sheng = pinyin[:idx]
        if sheng not in shengs:
            continue
        print(f'{pinyin} -> {sheng},{yun}')
        pinyin2shengyun_cache[pinyin] = [sheng, yun]
    return pinyin2shengyun_cache[pinyin]


if __name__ == '__main__':
    path = '/home/tzx/git/feeder/dump/zhihu_2020-02-02_13-39-01.149.txt'
    # path = '/home/tzx/git/feeder/dump/zhihu_dump_1580381555.txt'
    with open(path) as f:
        lines = f.readlines()
    with open(f'{path}_strip.txt', 'w') as f:
        for line in lines:
            line = re.sub("[\u0000-\u007f]", "", line)
            # line = re.sub("阅读更多", "\n", line)
            f.write(line)
            f.write('\n')
    exit(0)

    char_counter = defaultdict(int)
    word_counter = defaultdict(int)
    shengyun_counter = defaultdict(int)
    sheng2yun_counter = {}

    for line in lines:
        # print('\n\n\n', line)
        line = re.sub("[\u0000-\u007f]", "", line)
        for c in line:
            char_counter[c] += 1
            try:
                pinyin = pypinyin.pinyin(c, style=pypinyin.Style.NORMAL, errors='ignore')[0][0]
                sheng, yun = pinyin2shengyun(pinyin)
                # print(f'{c} -> {pinyin} -> {sheng},{yun}')
                shengyun_counter[sheng] += 1
                shengyun_counter[yun] += 1
                if sheng not in sheng2yun_counter:
                    sheng2yun_counter[sheng] = defaultdict(int)
                sheng2yun_counter[sheng][yun] += 1
            except Exception as e:
                pass

        segments = HanLP.segment(line)
        for seg_idx, seg in enumerate(segments):
            seg = str(seg)
            idx = seg.rfind('/')
            hanzi = seg[:idx]
            word_counter[hanzi] += 1

    char2count = [[k, v] for k, v in char_counter.items()]
    char2count.sort(key=lambda kv: kv[1], reverse=True)
    # pprint(char2count[:20])
    with open('/tmp/char.txt', 'w') as f:
        for index, (char, count) in enumerate(char2count):
            f.write(f'{index}\t{char}\t{count}\n')
    draw_svg('/tmp/char.svg', '字', char2count[:100])

    shengyun2count = [[k, v] for k, v in shengyun_counter.items()]
    shengyun2count.sort(key=lambda kv: kv[1], reverse=True)
    with open('/tmp/shengyun.txt', 'w') as f:
        for index, (char, count) in enumerate(shengyun2count):
            f.write(f'{index}\t{char}\t{count}\n')
        f.write('### sheng -> yun -> count\n')
        f.write(json.dumps(sheng2yun_counter, indent=4))
    draw_svg('/tmp/shengyun.svg', '字', shengyun2count[:100])

    word2count = [[k, v] for k, v in word_counter.items()]
    word2count.sort(key=lambda kv: kv[1], reverse=True)
    # pprint(word2count[:20])
    with open('/tmp/word.txt', 'w') as f:
        for index, (word, count) in enumerate(word2count):
            f.write(f'{index}\t{word}\t{count}\n')
    draw_svg('/tmp/word.svg', '词', word2count[:100])