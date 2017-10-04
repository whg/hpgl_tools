"""svg2hpgl

Usage:
  svg2hpgl.py <file> [-c] [--offset=<offset>] [--scale=<scale>][--of=<output_file>]
  svg2hpgl.py (-h | --help)
  svg2hpgl.py --version

Options:
  -h --help            Show this screen
  --version            Show version
  -c --pen-colour      Group number is pen colour
  --scale=<scale>      Scale svg [default: 1.0]
  --offset=<offset>    Offset of image in mm [default: (0,0)]
  --of=<output_file>   Output filename, defaults to image name with .hpgl as extension
"""

import xml.etree.ElementTree as ET
import re
from collections import defaultdict
from pprint import pprint

from docopt import docopt

def get_tag(element):
    return re.search(r'^{[^}]*}([a-z]+)', element.tag).groups()[0]

class Point:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def tuple(self):
        return (self.x, self.y)
        
    def __repr__(self):
        return '({}, {})'.format(self.x, self.y)

def make_point(x, y):
    return (float(x), float(y))

    
class Line:

    def swapped(self):
        o = Line()
        o.start = self.end
        o.end = self.start
        return o
    
    def __repr__(self):
        return '[{start}, {end}]'.format(**self.__dict__)
        
class LineSet(set):
        
    def add(self, element):
        a = element.attrib
        line = Line()
        line.start = make_point(a['x1'], a['y1'])
        line.end = make_point(a['x2'], a['y2'])

        super().add(line)


    def find_paths(self):
        destinations = defaultdict(dict)
        for line in self:
            destinations[line.start][line.end] = line
            destinations[line.end][line.start] = line.swapped()

            
        line = self.pop()
        path = [[line]]
        destinations[line.start].pop(line.end)
        if not destinations[line.start]:
            destinations.pop(line.start)
        destinations[line.end].pop(line.start)
        if not destinations[line.end]:
            destinations.pop(line.end)
            
        current_path_index = 0

        def _next_line(path, destinations):
            nonlocal current_path_index
            
            line = path[current_path_index][-1]
            
            if line.end in destinations:
                _, next_line = destinations[line.end].popitem()
            else:
                try:
                    start, endings = destinations.popitem()
                except KeyError:
                    return False

                end, next_line = endings.popitem()
                if endings:
                    destinations[start] = endings
                current_path_index += 1
                path.append([])

            path[current_path_index].append(next_line)
            
            destinations[next_line.end].pop(next_line.start)

            if not destinations[next_line.end]:
                destinations.pop(next_line.end)
            if not destinations[next_line.start]:
                destinations.pop(next_line.start)

            return True

        
        while _next_line(path, destinations):
            pass



        return path
            

def get_path(path):
    o = ''
    
    s = 10
    for strip in path:
        o += 'PU{},{};'.format(strip[0].start[0] * s, 7000 - strip[0].start[1] * s)
        for bit in strip:
            o += 'PD{},{};'.format(bit.end[0] * s, 7000- bit.end[1] * s)
        o += '\n'
    return o

def transform_paths(paths, scale=1.0, offset=(0, 0)):
    x_offset, y_offset = offset

    for path in paths:
        for line in path:
            line.start = (line.start[0] * scale + x_offset, line.start[1] * scale + y_offset)
            line.end = (line.end[0] * scale + x_offset, line.end[1] * scale + y_offset)

def offset_paths_for_y(paths):
    maxy = 0
    for path in paths:
        for line in path:
            maxy = max(maxy, max(line.start[1], line.end[1]))

    for path in paths:
        for line in path:
            line.start = (line.start[0], maxy - line.start[1])
            line.end = (line.end[0], maxy - line.end[1])

    
if __name__ == "__main__":

    args = docopt(__doc__, version=0.1)
    print(args)
    tree = ET.parse(args['<file>'])
    root = tree.getroot()
    group_counter = 1

    POINTS_IN_MM = 2.83465
    STEPS_PER_MM = 40
    scale = float(args['--scale']) * STEPS_PER_MM / POINTS_IN_MM
    offset = eval(args['--offset'])

    hpgl = args['<file>'].replace('.svg', '.hpgl')

    with open(hpgl, 'w') as f:
        f.write('SP1;\n')
        for child in root.getchildren():
            tag = get_tag(child)
            if tag == 'g':
                line_set = LineSet()
                for item in child.getchildren():
                    if get_tag(item) == 'line':
                        line_set.add(item)
                        
                paths = line_set.find_paths()

                if args['--pen-colour']:
                    f.write('SP{};'.format(group_counter))

                print(paths[0][0])
                offset_paths_for_y(paths)
                transform_paths(paths, scale, offset)
                print(paths[0][0])

                print(paths[0][0])

                print()
                    
                for path in paths:
                    f.write('PU{},{};\n'.format(int(path[0].start[0]), int(path[0].start[1])))
                    for line in path:
                        f.write('PD{},{};\n'.format(int(line.end[0]), int(line.end[1])))
                
                group_counter += 1

        f.write('SP0;')
                
