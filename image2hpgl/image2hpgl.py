"""image2hpgl

Usage:
  image2hpgl.py <image> <shape> [--spacing=<spacing>] [--offset=<offset>] [--size=<size>] [--of=<output_file>]
  image2hpgl.py (-h | --help)
  image2hpgl.py --version

Options:
  -h --help            Show this screen
  --version            Show version
  --spacing=<spacing>  Spacing of shape in mm [default: 1]
  --offset=<offset>    Offset of image in mm [default: (0,0)]
  --size=<size>        Size of shape [default: 2]
  --of=<output_file>   Output filename, defaults to image name with .hpgl as extension
"""

from docopt import docopt
from PIL import Image


class Placer:
    STEPS_PER_MM = 40
    def __init__(self, spacing=1, offset=(0, 0), size=1):
        self.spacing = int(spacing * Placer.STEPS_PER_MM)
        self.x_offset = int(offset[0] * Placer.STEPS_PER_MM)
        self.y_offset = int(offset[1]* Placer.STEPS_PER_MM)
        self.radius = int(size * 0.5 * Placer.STEPS_PER_MM)
        
    def _point(self, x, y):
        return (x * self.spacing + self.x_offset, y * self.spacing + self.y_offset)
        
    def dot(self, x, y):
        x, y = self._point(x, y)
        return 'PU{x},{y};PD{x},{y};PU;\n'.format(x=x, y=y)

    def circle(self, x, y):
        x, y = self._point(x, y)
        return 'PU{x},{y};CI{r},6;PU;\n'.format(x=x, y=y, r=self.radius)

    def plus(self, x, y):
        x, y = self._point(x, y)
        output = 'PU{x},{y};'.format(x=x-self.radius, y=y)
        output += 'PD{x},{y};'.format(x=x+self.radius, y=y)
        output += 'PU{x},{y};'.format(x=x, y=y-self.radius)
        output += 'PD{x},{y};'.format(x=x, y=y+self.radius)
        return output + 'PU;\n'

    def square(self, x, y):
        x, y = self._point(x, y)
        
        

if __name__ == "__main__":

    args = docopt(__doc__, version=0.1)
    
    img = Image.open(args["<image>"])

    if img.mode == 'L':
        black_pixel_value = 0
    elif img.mode == 'P':
        black_pixel_value = 1
    else:
        raise Exception('image not ({}) not supported'.format(img.mode))
        exit()

    
    pixels = list(img.getdata())

    spacing = eval(args['--spacing'])
    offset = eval(args['--offset'])
    size = eval(args['--size'])
    placer = Placer(spacing, offset, size)
    
    try:
        placer_func = getattr(placer, args['<shape>'])
    except AttributeError:
        print(args['<shape>'], 'is not a valid shape')
        exit()

    
    nfn = args['<image>'].replace('.png', '_{}.hpgl'.format(args['<shape>']))
    hpgl_filename = args['--of'] or nfn
    
    with open(hpgl_filename, 'w') as f:
        f.write('SP1;\n')
        for y in range(img.height):
            for x in range(img.width):
                if pixels[y * img.width + x] == black_pixel_value:
                    # plotter has origin bottom left
                    f.write(placer_func(x, img.height - y - 1))

                    

                    

    

                    
