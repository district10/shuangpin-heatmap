from pypinyin import pinyin, lazy_pinyin, Style
from pyhanlp import *
from svg import SVG
import os
import sys


PWD = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = f'{PWD}/data'


if __name__ == '__main__':
    print(pinyin('这是中文', style=Style.NORMAL))
    print(HanLP.segment('上海自来水来自海上'))

    red = 255, 0, 0
    green = 0, 255, 0
    blue = 0, 0, 255
    yellow = 255, 0, 0
    white = 255, 255, 255
    black = 0, 0, 0

    svg = SVG(400, 300)
    svg.circles.append(SVG.Circle(50, 50, 1, red))
    svg.circles.append(SVG.Circle(100, 50, 5, red, yellow))
    svg.circles.append(SVG.Circle(150, 50, 10, blue, black, 5))
    svg.polylines.append(SVG.Polyline([[0, 0], [20, 20]]))
    svg.polylines.append(SVG.Polyline([[20, 20], [100, 100]], red, 2))
    svg.polylines.append(
        SVG.Polyline([[100, 100], [200, 200], [svg.width, svg.height]], red,
                     0.5))
    svg.polygons.append(
        SVG.Polygon([[100, 100], [200, 200], [svg.width, svg.height]], red))
    print(svg)