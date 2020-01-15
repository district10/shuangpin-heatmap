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


def write_svg_heatmap(
        svg: SVG,
        path: str,
        *,
        log_saving: bool = False,
) -> str:
    global KEYBOARD_LAYOUT_SVG_HEAD
    if not KEYBOARD_LAYOUT_SVG_HEAD:
        with open(f'{PWD}/svgs/keyboard-layout.svg') as f:
            KEYBOARD_LAYOUT_SVG_HEAD = f.read().split(
                KEYBOARD_LAYOUT_SVG_TAIL)[0]
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
        key2count: Optional[Dict[str, int]] = None,
) -> SVG:
    d2q = {kd: kq for kq, kd in zip(QWERTY, DVORAK)}
    q2d = {kq: kd for kq, kd in zip(QWERTY, DVORAK)}
    svg = SVG(400, 300)
    # letters
    for kq, kd in zip(QWERTY, DVORAK):
        x, y = key2pos[kq]
        k = kq if is_qwerty else kd
        svg.children.append(SVG.Text(x, y, f'{k.upper()}'))
        if key2count and k in key2count:
            c = key2count[k]
            text = SVG.Text(x+15, y+35, f'{c}', [0, 0, 0, 0.4], 4)
            text.text_anchor = 'middle'
            svg.children.append(text)
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
        text = SVG.Text(x + sheng_yun_x_offset,
                        y + yun_counter[k] * sheng_yun_y_offset, f'{yun}', GRAY)
        text.text_anchor = 'end'
        svg.children.append(text)
    if title is None or title:
        x, y = 385, 255  # put at space bar
        text = SVG.Text(x, y, title or shuangpin_schema['name'])
        text.alignment_baseline = 'middle'
        text.text_anchor = 'middle'
        svg.children.append(text)
    return svg


PINYIN2SHUANGPIN_CACHE = defaultdict(dict)


def pinyin2shuangpin(
        pinyin: str,
        *,
        shuangpin_schema_name: str = 'ziranma',
) -> str:
    cache = PINYIN2SHUANGPIN_CACHE[shuangpin_schema_name]
    shuangpin_schema = get_schema(shuangpin_schema_name)
    if pinyin in cache:
        return cache[pinyin]
    try:
        shengs = shuangpin_schema['detail']['sheng']
        yuns = shuangpin_schema['detail']['yun']
        others = shuangpin_schema['detail']['other']
        if pinyin in others:
            cache[pinyin] = others[pinyin]
        else:
            for yun in yuns:
                if not pinyin.endswith(yun):
                    continue
                idx = len(pinyin) - len(yun)
                sheng = pinyin[:idx]
                if sheng not in shengs:
                    continue
                sp_sheng = shengs[sheng]
                sp_yun = yuns[yun]
                if len(sp_yun) != 1:
                    sp_yun = sp_yun[0]
                cache[pinyin] = f'{sp_sheng}{sp_yun}'
    except Exception as e:
        raise e
    cache.setdefault(pinyin, pinyin)
    return cache[pinyin]


def text2key_strokes(
        text: str,
        *,
        shuangpin_schema_name: Optional[str] = None,
) -> str:
    if shuangpin_schema_name is None:
        to_key_strokes = lambda pinyin: pinyin
    else:
        to_key_strokes = lambda pinyin: pinyin2shuangpin(
            pinyin, shuangpin_schema_name=shuangpin_schema_name)
    strokes = []
    for pinyin in pypinyin.pinyin(text, style=pypinyin.Style.NORMAL, errors='ignore'):
        try:
            ss = to_key_strokes(pinyin[0])
            strokes.append(ss)
        except Exception as e:
            print(repr(e))
    return ''.join(strokes)


def annotate(
        line: str,
        *,
        shuangpin_schema_name: str = 'ziranma',
        line_column_max: int = 80,
        word_sep: str = '',
        line_sep: Optional[str] = None,
) -> List[str]:
    segments = HanLP.segment(line.strip())
    to_shuangpin = lambda pinyin: pinyin2shuangpin(pinyin, shuangpin_schema_name=shuangpin_schema_name)
    lines = []
    line_hz = []
    line_zy = []
    length = 0
    for seg_idx, seg in enumerate(segments):
        seg = str(seg)
        idx = seg.rfind('/')
        hanzi = seg[:idx]
        annotations = []
        for pinyin in pypinyin.pinyin(hanzi, style=pypinyin.Style.NORMAL):
            pinyin = pinyin[0]
            shuangpin = to_shuangpin(pinyin)
            annotations.append(shuangpin)
        zhuyin = ''.join(annotations)
        line_hz.append(hanzi)
        line_zy.append(zhuyin)
        length += len(zhuyin)
        if length > line_column_max or seg_idx == len(segments) - 1:
            lines.append(word_sep.join(line_zy))
            lines.append(word_sep.join(line_hz))
            if line_sep:
                lines.append(line_sep)
            line_hz.clear()
            line_zy.clear()
            length = 0
    return lines


def lines_of_text(paths: Optional[List[str]]) -> Optional[List[str]]:
    if not paths:
        return None
    lines = []
    for path in paths:
        with open(path) as f:
            lines.extend(f.readlines())
    return lines


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
    parser.add_argument(
        '--line-column-max',
        type=int,
        default=80,
        help=f'line column max value (for line wrap), default: 80',
    )
    parser.add_argument(
        '--input-text-files',
        type=str,
        nargs='+',
        help=f"input text files (if specified, won't read from these files instead of stdin)",
    )
    parser.add_argument(
        '--interactive-mode',
        type=str2bool,
        default=False,
        help=f'interactive (tutorial) mode',
    )
    parser.add_argument(
        '--heatmap-mode',
        type=str2bool,
        default=False,
        help=f'heatmap mode',
    )
    args = parser.parse_args()
    shuangpin_schema_name = args.shuangpin_schema_name
    list_all_shuangpin_schemas: bool = args.list_all_shuangpin_schemas
    dump_all_shuangpin_layout: bool = args.dump_all_shuangpin_layout
    use_dvorak: bool = args.use_dvorak
    is_qwerty: bool = not use_dvorak
    output_directory: Optional[str] = args.output_directory
    output_svg_path: str = output_svg_path
    line_column_max: int = args.line_column_max
    input_text_files: Optional[List[str]] = args.input_text_files
    interactive_mode: bool = args.interactive_mode
    heatmap_mode: bool = args.heatmap_mode

    if list_all_shuangpin_schemas:
        print(
            f'available shuangpin schemas:\n{json.dumps(get_schema(), indent=4)}'
        )
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
            write_svg_heatmap(
                svg, f'{output_directory}/{schema_name}.svg', log_saving=True)
        exit(0)

    if not heatmap_mode and (interactive_mode or input_text_files):
        lines = lines_of_text(input_text_files)
        if not lines:
            print('reading from stdin (control-d to close)...')
        for line in lines or sys.stdin:
            annotated = annotate(
                line,
                shuangpin_schema_name=shuangpin_schema_name,
                line_column_max=line_column_max,
            )
            print('\n'.join(annotated))
            if interactive_mode and lines:
                # for your practice
                try:
                    sys.stdin.readline()
                except Exception as e:
                    pass
        exit(0)

    if heatmap_mode:
        lines = lines_of_text(input_text_files) or []
        if not lines:
            print('reading from stdin (control-d to close)...')
            for line in sys.stdin:
                lines.append(line)
        strokes = text2key_strokes(
            ''.join(lines),
            shuangpin_schema_name='ziranma',
        )
        key2count = defaultdict(int)
        for key in strokes:
            key2count[key] += 1
        svg = generate_keyboard_svg(
            is_qwerty=is_qwerty,
            shuangpin_schema_name=shuangpin_schema_name,
            key2count=key2count,
        )
        write_svg_heatmap(svg, output_svg_path, log_saving=True)
        exit(0)

    print("""
    You are not in any of these modes:
        --heatmap-mode 1                # let's do some statistics
        --interactive-mode 1            # works like your shuangpin tutorial 

    I'll generate a shuangpin keyboard layout now
    """)
    svg = generate_keyboard_svg(
        is_qwerty=is_qwerty,
        shuangpin_schema_name=shuangpin_schema_name,
    )
    write_svg_heatmap(svg, output_svg_path, log_saving=True)
