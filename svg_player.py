import os
import sys
import json
import tempfile
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler, test
from typing import Union, List, Tuple, Optional
from multiprocessing import Process, Queue
import argparse
import webbrowser
import time
from uuid import uuid4


def uuid() -> str:
    return str(uuid4())[:8]


def myip() -> Optional[str]:
    try:
        """
        https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
        """
        ip = [
            l for l in ([
                ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
                if not ip.startswith("127.")
            ][:1], [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close())
                     for s in
                     [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]])
            if l
        ][0][0]
        if isinstance(ip, str):
            return ip
        return None
    except:
        return None


PORT = 7777
PORTS = Queue()
SALT = uuid()
INDEX_HTML = tempfile.mktemp(suffix=f'mocked_{SALT}_index.html')
CACHE = {}


def salty_path(path: str) -> str:
    return f'/{SALT}_{path}'


HEAD = """
<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv='content-type' content='text/html; charset=utf-8' />
        <meta name='viewport' content='width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no'>
        <meta http-equiv='X-UA-Compatible' content='IE=edge' >
        <title>semantic mapping svg viewer</title>
        <style type="text/css">
            body, html {
                position: fixed;
                width: 100%;
                height: 100%;
                padding: 0;
                margin: 0;
            }
            svg {
                width: 100%;
                height: 100%;
                position: absolute;
                top: 0;
                left: 0;
            }
            select {
                position: absolute;
                top: 0;
                left: 0;
            }
            p {
                position: absolute;
                bottom: 0;
                left: 0;
            }
        </style>
    </head>
    <body>
"""
TAIL = """
        <p>SPACE: NEXT IMAGE, SHIFT+SPACE: PREV IMAGE</p>
        <script src='https://anvaka.github.io/panzoom/dist/panzoom.js'></script>
        <!--script src='http://kozea.github.io/pygal.js/2.0.x/pygal-tooltips.min.js'></script>-->
        <script>
            var img = document.getElementById('zoomable')
            var select = document.getElementById("select");
            var num_candidates = select.options.length;

            window.pz = panzoom(img, {
                autocenter: true,
                bounds: true,
                filterKey: function(/* e, dx, dy, dz */) {
                    // don't let panzoom handle this event:
                    return true;
                }
            });
            function updateSelection() {
                img.src = select.value;
            }
            prev_index = 0;

            function switchToIndex(idx) {
                idx = idx % num_candidates;
                if (idx == select.selectedIndex) {
                    return;
                }
                prev_index = select.selectedIndex;
                select.selectedIndex = idx;
                img.src = select.options[select.selectedIndex].value;
            }

            document.getElementsByTagName("body")[0].onkeypress = evt => {
                var shiftKey = evt.shiftKey;
                evt = evt || window.event;
                var charCode = evt.keyCode || evt.which;
                if (48 <= charCode && charCode <= 48 + 9) { // 0 ~ 9 to switch to nth image
                    console.log('0~9');
                    switchToIndex(charCode - 48);
                } else if (charCode == 116) { // t
                    console.log('116, t');
                    switchToIndex(prev_index);
                } else if (charCode == 32) { // <space>
                    console.log('32, space');
                    var idx = select.selectedIndex
                    idx += shiftKey ? -1 : 1;
                    switchToIndex(idx);
                }
                console.log("charCode", charCode, "shiftKey", shiftKey);
            };
        </script>
    </body>
</html>
"""


class CORSRequestHandler(SimpleHTTPRequestHandler):

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

    def translate_path(self, path):
        if path.endswith('.html'):
            return CACHE[INDEX_HTML]
        elif path in CACHE:
            return CACHE[path]
        else:
            return super().translate_path(path)


def run(ports):
    global PORT
    while True:
        try:
            print('====================================')
            print(f'\thttp://{myip()}:{PORT}/index.html')
            print('====================================')
            ports.put(PORT)
            test(CORSRequestHandler, HTTPServer, port=PORT)
            break
        except OSError:
            pass
        PORT += 1
        ports.get()


def panzoom_svg(svgs):
    if not svgs:
        raise ValueError('no any svg image provided')
    # TODO
    """
    if len(svg) > 100:
        keep the list to the backend, the front end won't able to select at each frame
    """

    CACHE[INDEX_HTML] = INDEX_HTML
    for svg in svgs:
        CACHE[salty_path(svg)] = svg

    with open(INDEX_HTML, 'w') as f:
        f.write(HEAD)
        f.write('<select id="select" onchange="updateSelection()" >')
        OPTIONS = '\n\t'.join([
            f'<option value="{salty_path(svg)}">{svg}</option>' for svg in svgs
        ])
        f.write(OPTIONS)
        f.write('</select>')
        IMG = f'        <img id="zoomable" src="{salty_path(svgs[0])}" />'
        # for pygal, but not work with panzoom
        # IMG = f'        <figure><embed type="image/svg+xml" id="zoomable" src="{salty_path(svgs[0])}" /></figure>'
        f.write(IMG)
        f.write(TAIL)

    p = Process(target=run, args=(PORTS,))
    p.start()
    time.sleep(0.01)
    while PORTS.empty():
        time.sleep(0.01)
    port = PORTS.get()
    url = f'http://localhost:{port}/{uuid()}.html'  # avoids browser caching
    webbrowser.open_new_tab(url)
    p.join()


if __name__ == '__main__':
    prog = 'python3 svg_player.py'
    description = ('pan & zoom svg images')
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument(
        'input_path',
        nargs='+',
        type=str,
        help='input svg path (1. svg path; 2. txt with svg path (or dir) each line; 3. dir with svgs images)',
    )
    parser.add_argument(
        '--port',
        type=int,
        default=-1,
        help='port to open',
    )
    args = parser.parse_args()

    if args.port > 0:
        PORT = args.port

    def extract_images(path: str, svgs: List[str]) -> None:

        def is_image_file(path: str) -> bool:
            return os.path.isfile(path) and any([
                path.endswith('.svg'),
                path.endswith('.png'),
                path.endswith('.jpg'),
            ])

        def extract_dir_of_images(dir: str, svgs: List[str]) -> None:
            children = [f'{dir}/{file}' for file in os.listdir(dir)]
            children.sort()
            for child in children:
                if is_image_file(child):
                    extract_images(child, svgs)

        if os.path.isdir(path):
            extract_dir_of_images(path, svgs)
        elif path.endswith('.txt'):
            with open(path) as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    line = os.path.abspath(line)
                    if is_image_file(line):
                        extract_images(line, svgs)
                    elif os.path.isdir(line):
                        extract_dir_of_images(line, svgs)
                    else:
                        logger.warning(f'unable to process line: {line}')
        elif is_image_file(path):
            svgs.append(path)
        else:
            logger.warning(
                f'something went wrong, not able to extract images from: {path}'
            )

    svgs = []
    for path in args.input_path:
        path = os.path.abspath(path)
        extract_images(path, svgs)
    panzoom_svg(svgs)
