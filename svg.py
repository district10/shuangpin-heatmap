import numpy as np
from itertools import chain
# based on https://github.com/cubao/naive-svg/blob/master/naive_svg.py


class Object(object):

    def __init__(self, points=None, stroke=None, stroke_width=1, fill=None):
        if points is None:
            points = []
        self.points = np.array(points)
        self.stroke = stroke or [0, 0, 0]
        self.stroke_width = stroke_width
        self.fill = fill or list(self.stroke)

    @property
    def x(self):
        return self.points[0][0]

    @property
    def y(self):
        return self.points[0][1]

    def __repr__(self):
        raise NotImplementedError


def rgb(color):
    if color is None:
        return 'none'
    try:
        r, g, b = color
        return 'rgb({},{},{})'.format(r, g, b)
    except Exception:
        r, g, b, a = color
        return 'rgba({},{},{},{})'.format(r, g, b, a)


class SVG(Object):

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.polygons = []
        self.polylines = []
        self.circles = []
        self.texts = []

        self.grid_step = -1
        self.grid_color = [155, 155, 155]
        self.background = None

    class Polyline(Object):

        def __init__(self, points, stroke=None, stroke_width=1, fill=None):
            super().__init__(points, stroke, stroke_width, fill)
            self.fill = None
            self.tag = 'polyline'

        def __repr__(self):
            points = ' '.join(
                ['{},{}'.format(pt[0], pt[1]) for pt in self.points])
            return "<{} style='stroke:{};stroke-width:{};fill:{}' points='{}' />" \
                .format(self.tag, rgb(self.stroke), self.stroke_width, rgb(self.fill), points)

    class Polygon(Polyline):

        def __init__(self, points, fill=None, stroke=None, stroke_width=1):
            super().__init__(points, stroke, stroke_width, fill)
            self.fill = fill
            self.stroke = stroke
            self.tag = 'polygon'

    class Circle(Object):

        def __init__(self, x, y, r=1, stroke=None, fill=None, stroke_width=1):
            super().__init__(np.array([[x, y]]), stroke, stroke_width, fill)
            self.r = r

        def __repr__(self):
            return "<circle r='{}' cx='{}' cy='{}' style='stroke:{};stroke-width:{};fill:{}' />" \
                .format(self.r, self.x, self.y, rgb(self.stroke), self.stroke_width, rgb(self.fill))

    class Text(Object):

        def __init__(self, x, y, text, fill=None, fontsize=10):
            super().__init__(np.array([[x, y]]), fill, 1, fill)
            self.text = text
            self.fontsize = fontsize

        def __repr__(self):
            return "<text x='{}' y='{}' fill='{}' font-size='{}' font-family='monospace'>{}</text>" \
                .format(self.x, self.y, rgb(self.fill), self.fontsize, self.text)

    def __repr__(self):
        lines = []
        lines.append(
            "<svg width='{}' height='{}' xmlns='http://www.w3.org/2000/svg'>"
            .format(self.width, self.height))
        if self.background:
            lines.append(
                "\t<rect width='100%' height='100%' fill='{}' />".format(
                    rgb(self.background)))
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
