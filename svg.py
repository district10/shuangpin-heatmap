import numpy as np
from itertools import chain
from typing import Union, Set, Dict, List, Any, Tuple, Optional
# based on https://github.com/cubao/naive-svg/blob/master/naive_svg.py


Pixel = Tuple[float, float]
Pixels = List[Pixel]
Color = Union[Tuple[int, int, int], Tuple[int, int, int, float], None]


class Object(object):

    def __init__(
            self,
            points: Optional[Pixels] = None,
            stroke: Color = None,
            stroke_width: float = 1,
            fill: Color = None,
    ):
        if points is None:
            points = []
        self.points: Pixels = np.array(points)
        self.stroke: Color = stroke or [0, 0, 0]
        self.stroke_width: float = stroke_width
        self.fill: Color = fill or list(self.stroke)

    @property
    def x(self) -> float:
        return self.points[0][0]

    @property
    def y(self) -> float:
        return self.points[0][1]

    def __repr__(self) -> str:
        raise NotImplementedError


def rgb(color: Color) -> str:
    if color is None:
        return 'none'
    if len(color) == 3:
        r, g, b = color
        return 'rgb({},{},{})'.format(r, g, b)
    else:
        r, g, b, a = color
        return 'rgba({},{},{},{})'.format(r, g, b, a)


class SVG(Object):

    def __init__(self, width: float, height: float):
        self.width: float = width
        self.height: float = height
        self.polygons: List[Polygon] = []
        self.polylines: List[Polyline] = []
        self.circles: List[Circle] = []
        self.texts: List[Text] = []

        self.grid_step: float = -1
        self.grid_color: Color = [155, 155, 155]
        self.background: Color = None

    class Polyline(Object):

        def __init__(
                self,
                points: Pixels,
                stroke: Color = None,
                stroke_width: float = 1,
                fill: Color = None,
        ):
            super().__init__(points, stroke, stroke_width, fill)
            self.fill: Color = None
            self.tag: str = 'polyline'

        def __repr__(self) -> str:
            points = ' '.join([f'{pt[0]},{pt[1]}' for pt in self.points])
            return f"<{self.tag} style='stroke:{rgb(self.stroke)};stroke-width:{self.stroke_width};fill:{rgb(self.fill)}' points='{points}' />"

    class Polygon(Polyline):

        def __init__(
                self,
                points: Pixels,
                fill: Color = None,
                stroke: Color = None,
                stroke_width: float = 1,
        ):
            super().__init__(points, stroke, stroke_width, fill)
            self.fill: Color = fill
            self.stroke: Color = stroke
            self.tag: str = 'polygon'

    class Circle(Object):

        def __init__(
                self,
                x: float,
                y: float,
                r: float = 1,
                stroke: Color = None,
                fill: Color = None,
                stroke_width: float = 1,
        ):
            super().__init__(np.array([[x, y]]), stroke, stroke_width, fill)
            self.r: float = r

        def __repr__(self):
            return f"<circle r='{self.r}' cx='{self.x}' cy='{self.y}' style='stroke:{rgb(self.stroke)};stroke-width:{self.stroke_width};fill:{rgb(self.fill)}' />"

    class Text(Object):

        def __init__(
                self,
                x: float,
                y: float,
                text: str,
                fill: Color = None,
                fontsize: float = 10,
        ):
            super().__init__(np.array([[x, y]]), fill, 1, fill)
            self.text: str = text
            self.fontsize: float = fontsize

        def __repr__(self):
            return f"<text x='{self.x}' y='{self.y}' fill='{rgb(self.fill)}' font-size='{self.fontsize}' font-family='monospace'>{self.text}</text>"

    def __repr__(self):
        lines = []
        lines.append(
            f"<svg width='{self.width}' height='{self.height}' xmlns='http://www.w3.org/2000/svg'>"
        )
        if self.background:
            lines.append(
                f"\t<rect width='100%' height='100%' fill='{rgb(self.background)}' />"
            )
        if self.grid_step > 0:
            grid_color = self.grid_color or [155, 155, 155]
            for i in np.arange(0, self.height, self.grid_step):
                lines.append('\t{}'.format(
                    SVG.Polyline([[0, i], [self.width, i]], grid_color)))
            for j in np.arange(0, self.width, self.grid_step):
                lines.append('\t{}'.format(
                    SVG.Polyline([[j, 0], [j, self.height]], grid_color)))
        lines.extend(['\t{}'.format(p) for p in self.polygons])
        lines.extend(['\t{}'.format(p) for p in self.polylines])
        lines.extend(['\t{}'.format(c) for c in self.circles])
        lines.extend(['\t{}'.format(t) for t in self.texts])
        lines.append('</svg>')
        return '\n'.join(lines)

    def fit_to_bbox(self, xmin, xmax, ymin, ymax):
        for poi in chain(self.polygons, self.polylines, self.circles,
                         self.texts):
            poi.points[:, 0] = np.interp(poi.points[:, 0], [xmin, xmax],
                                         [0, self.width])
            poi.points[:, 1] = np.interp(poi.points[:, 1], [ymin, ymax],
                                         [0, self.height])

    def save(self, path):
        with open(path, 'w') as f:
            f.write(str(self))


if __name__ == '__main__':
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
