from pypinyin import pinyin, lazy_pinyin, Style
from pyhanlp import *
from typing import Union, Set, Dict, List, Any, Tuple, Optional
from svg import SVG
import os
import sys
import json
import argparse
import tempfile
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


RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
YELLOW = 255, 0, 0
WHITE = 255, 255, 255
BLACK = 0, 0, 0
GRAY = 155, 155, 155


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError(
            'Boolean value expected. e.g. "true", "false"')


def mkdir_p(path: str) -> str:
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def get_schema(schema: Optional[str] = None) -> Union[Dict, List[str]]:
    global SHUANGPIN_SCHEMAS
    if not SHUANGPIN_SCHEMAS:
        with open(f'{DATA_DIR}/shuangpin.json') as f:
            shuangpin = json.load(f)
            SHUANGPIN_SCHEMAS = {s['id']: s for s in shuangpin['schemas']}
    if not schema:
        return list(SHUANGPIN_SCHEMAS.keys())
    return SHUANGPIN_SCHEMAS[schema]


def write_svg_heatmap(svg: SVG, path: str,
        *,
        log_saving: bool = False,
) -> str:
    global KEYBOARD_LAYOUT_SVG_HEAD
    if not KEYBOARD_LAYOUT_SVG_HEAD:
        with open(f'{PWD}/svgs/keyboard-layout.svg') as f:
            KEYBOARD_LAYOUT_SVG_HEAD = f.read().split(KEYBOARD_LAYOUT_SVG_TAIL)[0]
    BODY = '\n'.join(str(svg).split('\n')[1:-1])
    with open(path, 'w') as f:
        f.write(KEYBOARD_LAYOUT_SVG_HEAD)
        f.write(BODY)
        f.write(KEYBOARD_LAYOUT_SVG_TAIL)
    if log_saving:
        print(f'wrote svg to {path}')


def generate_keyboard_svg(
        *,
        is_qwerty: bool = True,
        shuangpin_schema_name: str = 'ziranma',
        title: Optional[str] = None,
) -> SVG:
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
        fill = GRAY if i < len(OTHER_KEYS) // 2 else BLACK
        svg.children.append(SVG.Text(x, y, f'{k}', fill))
    # modifier keys, etc
    for k in [k for k in key2pos if len(k) > 1]:
        x, y = key2pos[k]
        svg.children.append(SVG.Text(x, y, f'{k}', GRAY))
    # shuangpin
    shuangpin_schema = get_schema(shuangpin_schema_name)
    sheng_yun_x_offset = 25
    sheng_yun_y_offset = 12
    for sheng, k in shuangpin_schema['detail']['sheng'].items():
        x, y = key2pos[k if is_qwerty else d2q[k]]
        text = SVG.Text(x + sheng_yun_x_offset, y, f'{sheng}', GREEN)
        text.text_anchor = 'end'
        svg.children.append(text)
    yun_counter = defaultdict(int)
    for yun, k in shuangpin_schema['detail']['yun'].items():
        if isinstance(k, list):
            # should be special case in weiyuan & zhinengabc
            assert k[1] == 'v'
            k = k[0]
        x, y = key2pos[k if is_qwerty else d2q[k]]
        yun_counter[k] += 1
        text = SVG.Text(x + sheng_yun_x_offset, y + yun_counter[k] * sheng_yun_y_offset, f'{yun}', GRAY)
        text.text_anchor = 'end'
        svg.children.append(text)
    if title is None or title:
        x, y = 385, 255  # put at space bar
        text = SVG.Text(x, y, title or shuangpin_schema['name'])
        text.alignment_baseline = 'middle'
        text.text_anchor = 'middle'
        svg.children.append(text)
    return svg


if __name__ == '__main__':
    prog = f'python3 {sys.argv[0]}'
    description = ('Command line interface for shuangpin_heatmap')
    parser = argparse.ArgumentParser(prog=prog, description=description)

    shuangpin_schema_name = 'ziranma'
    output_svg_path = 'debug.svg'
    parser.add_argument(
        '--shuangpin-schema-name',
        type=str,
        default=shuangpin_schema_name,
        help=f'shuangpin schema name, default: {shuangpin_schema_name} (use --list-all-shuangpin-schemas 1 see all candidates)',
    )
    parser.add_argument(
        '--list-all-shuangpin-schemas',
        type=bool,
        default=False,
        help=f'list all shuangpin schemas (and exit)',
    )
    parser.add_argument(
        '--dump-all-shuangpin-layout',
        type=str2bool,
        default=False,
        help='default to use QWERTY keyboard layout, you can turn on dvorak explicitly',
    )
    parser.add_argument(
        '--use-dvorak',
        type=str2bool,
        default=False,
        help='default to use QWERTY keyboard layout, you can turn on dvorak explicitly',
    )
    parser.add_argument(
        '--output-directory',
        type=str,
        default=None,
        help='output directory (for batch dumpping svgs, etc)',
    )
    parser.add_argument(
        '--output-svg',
        type=str,
        default=output_svg_path,
        help=f'output svg path, default: {output_svg_path}',
    )
    args = parser.parse_args()
    shuangpin_schema_name = args.shuangpin_schema_name
    list_all_shuangpin_schemas: bool = args.list_all_shuangpin_schemas
    dump_all_shuangpin_layout: bool = args.dump_all_shuangpin_layout
    use_dvorak: bool = args.use_dvorak
    is_qwerty: bool = not use_dvorak
    output_directory: Optional[str] = args.output_directory
    output_svg_path: str = output_svg_path

    if list_all_shuangpin_schemas:
        print(f'available shuangpin schemas:\n{json.dumps(get_schema(), indent=4)}')
        exit(0)

    if dump_all_shuangpin_layout:
        if not output_directory:
            output_directory = tempfile.mkdtemp(prefix='shuangpin_heatmap_')
        mkdir_p(output_directory)
        for schema_name in get_schema():
            svg = generate_keyboard_svg(
                is_qwerty=is_qwerty,
                shuangpin_schema_name=schema_name,
            )
            write_svg_heatmap(svg, f'{output_directory}/{schema_name}.svg', log_saving=True)
        exit(0)

    # print(pinyin('这是中文', style=Style.NORMAL))
    # print(HanLP.segment('上海自来水来自海上'))
    svg = generate_keyboard_svg(
        is_qwerty=is_qwerty,
        shuangpin_schema_name=shuangpin_schema_name,
    )
    write_svg_heatmap(svg, output_svg_path, log_saving=True)
