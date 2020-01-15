import sys
import os


PWD = os.path.abspath(os.path.dirname(__file__))

if __name__ == '__main__':
    input_path = f'{PWD}/data/3000.txt'
    output_path = f'{PWD}/data/sample3000.txt'
    with open(output_path, 'w') as fo:
        with open(input_path) as f:
            for idx, line in enumerate(f):
                if '\t' not in line:
                    continue
                if idx > 1000:
                    continue
                hanzi, count = line.split('\t')[1:3]
                fo.write(''.join([hanzi] * int(count)))
