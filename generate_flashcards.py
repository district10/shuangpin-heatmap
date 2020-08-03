import pygal
import pypinyin
from typing import Union, Set, Dict, List, Any, Tuple, Optional
import os
import sys
import json
from collections import defaultdict
import numpy as np
import re
from pprint import pprint
from shuangpin_heatmap import pinyin2shuangpin, mkdir_p
import shutil


PWD = os.path.abspath(os.path.dirname(__file__))

if __name__ == '__main__':
    path = f'{PWD}/data/sample3.txt'
    output_directory = '/home/tzx/git/blog/notes/cards_shuangpin'
    mkdir_p(output_directory)

    with open(path) as f:
        lines = f.readlines()
    cards = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        pinyin = [k[0] for k in pypinyin.pinyin(line, style=pypinyin.Style.NORMAL, errors='ignore')]
        cache = {}
        trans = {}
        shuangpin = [
            pinyin2shuangpin(
                py,
                shuangpin_schema_name='ziranma',
                cache=cache,
                translated=trans,
            ) for py in pinyin
        ]
        py2sp = [[py, sp] for py, sp in trans.items() if py != sp]
        if not py2sp:
            continue
        cards.append(f'{output_directory}/card_{len(cards):08d}.md')
        with open(cards[-1], 'w') as f:
            if len(line) < 40:
                prefix = f'        '
                line = line.replace('\n', ';')
                f.write(f'-   "{line}" -<\n\n    :   ')
            else:
                prefix = ''
                f.write(f'{line}\n')
            if py2sp:
                f.write(f'| 拼音 | 双拼 |\n')
                f.write(f'{prefix}| :--- | :--: |\n')
                for (py, sp) in py2sp:
                    if py == sp:
                        continue
                    f.write(f'{prefix}| {py} | {sp} |\n')
            f.write(f'\n{prefix}```')
            f.write(f'\n{prefix}{"".join(shuangpin)}')
            f.write(f'\n{prefix}{line}')

            # ziranma = [
            #     pinyin2shuangpin(
            #         py,
            #         shuangpin_schema_name='ziranma',
            #         cache=cache,
            #         translated=trans,
            #     ) for py in pinyin
            # ]
            # f.write(f'\n\n\n\n{prefix}{"".join(ziranma)}')

            f.write(f'\n{prefix}```\n')

    with open(f'{output_directory}/index.md', 'w') as f:
        f.write('# Cards\n')
        for card in cards:
            basename = os.path.basename(card)
            f.write(f'\n-   [{basename}]({basename})')
    print(f'done, wrote #{len(cards)} cards to {output_directory}')
