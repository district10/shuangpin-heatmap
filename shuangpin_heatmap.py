from pypinyin import pinyin, lazy_pinyin, Style
from pyhanlp import *
from typing import Union, Set, Dict, List, Any, Tuple, Optional
from svg import SVG
import os
import sys

PWD = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = f'{PWD}/data'
KEYBOARD_LAYOUT_SVG_LINES: Optional[List[str]] = None

X_STEP = 142 - 88
X_OFFSET = 22
Y_OFFSET = 26


QWERTY = \
    "qwert" "yuiop[]\\" \
    "asdfg" "hjkl;'" \
    "zxcvb" "nm,./"
DVORAK = \
    ";,.ky" "fgclz[]\\" \
    "aoeiu" "drtsn'" \
    "pqjhx" "bmwv/"

OTHER_KEYS = \
    '~!@#$%^&*()_+' \
    '`1234567890-='

key2pos = {
    'q': [88, 58],
    'a': [101.5, 112],
    'z': [128.5, 166],
    '~': [7, 4],
    '`': [7, 4 + 10],
    'BACKSPACE': [709, 4],
    'TAB': [7, 58],
    'CAPS LOCK': [7, 112],
    'ENTER': [695.5, 112],
    'SHIFT (L)': [7, 166],
    'SHIFT (R)': [668.5, 166],
}
for keys in QWERTY, OTHER_KEYS:
    for i, k in enumerate(keys):
        if k in key2pos:
            continue
        prev_x, prev_y = key2pos.get(keys[i - 1])
        key2pos[k] = [prev_x + X_STEP, prev_y]
for k in key2pos:
    key2pos[k][0] += X_OFFSET
    key2pos[k][1] += Y_OFFSET


def write_svg_heatmap(svg: SVG, path: str) -> str:
    global KEYBOARD_LAYOUT_SVG_LINES
    if not KEYBOARD_LAYOUT_SVG_LINES:
        with open(f'{DATA_DIR}/keyboard-layout.svg') as f:
            KEYBOARD_LAYOUT_SVG_LINES = f.read()
    TAIL = '</svg>'
    HEAD = KEYBOARD_LAYOUT_SVG_LINES.split(TAIL)[0]
    BODY = '\n'.join(str(svg).split('\n')[1:-1])
    with open(path, 'w') as f:
        f.write(HEAD)
        f.write(BODY)
        f.write(TAIL)


if __name__ == '__main__':
    # print(pinyin('这是中文', style=Style.NORMAL))
    # print(HanLP.segment('上海自来水来自海上'))

    red = 255, 0, 0
    green = 0, 255, 0
    blue = 0, 0, 255
    yellow = 255, 0, 0
    white = 255, 255, 255
    black = 0, 0, 0
    gray = 155, 155, 155

    svg = SVG(400, 300)
    for k, k2 in zip(QWERTY, DVORAK):
        x, y = key2pos.get(k)
        svg.children.append(SVG.Text(x, y, f'{k2.upper()}'))
    for i, k in enumerate(OTHER_KEYS):
        x, y = key2pos.get(k)
        fill = gray if i < len(OTHER_KEYS) // 2 else black 
        svg.children.append(SVG.Text(x, y, f'{k}', fill))
    for k in key2pos:
        if len(k) == 1:
            continue
        x, y = key2pos.get(k)
        svg.children.append(SVG.Text(x, y, f'{k}', gray))
    path = 'debug.svg'
    write_svg_heatmap(svg, path)