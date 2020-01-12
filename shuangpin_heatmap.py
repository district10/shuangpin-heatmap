from pypinyin import pinyin, lazy_pinyin, Style
from pyhanlp import *
from typing import Union, Set, Dict, List, Any, Tuple, Optional
from svg import SVG
import os
import sys
import json
from collections import defaultdict

PWD = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = f'{PWD}/data'
KEYBOARD_LAYOUT_SVG_HEAD: Optional[str] = None
KEYBOARD_LAYOUT_SVG_TAIL: str = '</svg>'
SHUANGPIN_SCHEMAS: Optional[Dict[str, Dict]] = None


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
    '~': [7, 4],
    '`': [7, 4 + 10],
    'q': [88, 58],
    'a': [101.5, 112],
    'z': [128.5, 166],
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
        prev_x, prev_y = key2pos[keys[i - 1]]
        key2pos[k] = [prev_x + 54, prev_y]  # move rightwards 54 pixels
for k in key2pos:
    key2pos[k][0] += 22  # tweak a little bit
    key2pos[k][1] += 26


def get_schema(schema: Optional[str] = None) -> Union[Dict, List[str]]:
    global SHUANGPIN_SCHEMAS
    if not SHUANGPIN_SCHEMAS:
        with open(f'{DATA_DIR}/shuangpin.json') as f:
            shuangpin = json.load(f)
            SHUANGPIN_SCHEMAS = {s['id']: s for s in shuangpin['schemas']}
    if not schema:
        return SHUANGPIN_SCHEMAS.keys()
    return SHUANGPIN_SCHEMAS[schema]


def write_svg_heatmap(svg: SVG, path: str) -> str:
    global KEYBOARD_LAYOUT_SVG_HEAD
    if not KEYBOARD_LAYOUT_SVG_HEAD:
        with open(f'{DATA_DIR}/keyboard-layout.svg') as f:
            KEYBOARD_LAYOUT_SVG_HEAD = f.read().split(KEYBOARD_LAYOUT_SVG_TAIL)[0]
    BODY = '\n'.join(str(svg).split('\n')[1:-1])
    with open(path, 'w') as f:
        f.write(KEYBOARD_LAYOUT_SVG_HEAD)
        f.write(BODY)
        f.write(KEYBOARD_LAYOUT_SVG_TAIL)


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
    shuangpin_schema_name = 'ziranma'
    is_qwerty = False
    if not is_qwerty:
        d2q = {kd: kq for kq, kd in zip(QWERTY, DVORAK)}
        q2d = {kq: kd for kq, kd in zip(QWERTY, DVORAK)}

    svg = SVG(400, 300)
    # letters
    for kq, kd in zip(QWERTY, DVORAK):
        x, y = key2pos[kq]
        k = kq if is_qwerty else kd
        svg.children.append(SVG.Text(x, y, f'{k.upper()}'))
    # numbers, punctuations
    for i, k in enumerate(OTHER_KEYS):
        x, y = key2pos[k]
        fill = gray if i < len(OTHER_KEYS) // 2 else black
        svg.children.append(SVG.Text(x, y, f'{k}', fill))
    # modifier keys, etc
    for k in [k for k in key2pos if len(k) > 1]:
        x, y = key2pos[k]
        svg.children.append(SVG.Text(x, y, f'{k}', gray))
    # shuangpin
    shuangpin_schema = get_schema(shuangpin_schema_name)
    sheng_yun_x_offset = 25
    sheng_yun_y_offset = 12
    for sheng, k in shuangpin_schema['detail']['sheng'].items():
        x, y = key2pos[k if is_qwerty else d2q[k]]
        text = SVG.Text(x + sheng_yun_x_offset, y, f'{sheng}', green)
        text.text_anchor = 'end'
        svg.children.append(text)
    yun_counter = defaultdict(int)
    for yun, k in shuangpin_schema['detail']['yun'].items():
        x, y = key2pos[k if is_qwerty else d2q[k]]
        yun_counter[k] += sheng_yun_y_offset
        text = SVG.Text(x + sheng_yun_x_offset, y + yun_counter[k], f'{yun}', gray)
        text.text_anchor = 'end'
        svg.children.append(text)

    path = 'debug.svg'
    write_svg_heatmap(svg, path)