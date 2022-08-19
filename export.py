"""
When invoked from the command line, converts a stored heightmap .TIF (assuming
it has been resampled to the desired area and resolution) to RGB using a
particular color map. While it can be customized, by default this colormap
interpolates from black to blue (for negative altitudes), and from green to
white (for positive altitudes). The results are written to a .PNG (casted to
uint8) file determined by replacing the input .TIF with the .PNG extension.

Command line invocation might look something like this::

  > python export.py ./example/Untitled Polygon.tif
  Exported 3223 [px] x 6535 [px] heightmap to Untitled Polygon.png
  >
"""

import sys
import numpy
from imageio import v3 as imageio

def interp1(xx, yy, x):
    """
    Basic 1d interpolation, but easy to extend if (for example) a uniform
    gradient is not desired.
    """
    pct = (x - xx[0]) / (xx[1] - xx[0])
    return yy[0] + pct * (yy[1] - yy[0])

def defaultColorMap(alt, range):
    """
    Maps a given altitude value (in meters) to a specific RGB triplet. Second
    argument is the range (min and max) of the heightmap from which this
    altitude was drawn. By default, this maps negative altitude values from
    black to blue, and positive altitude values from green to white.
    """
    if alt < 0:
        return [
            interp1([range[0], 0], [0.0, 0.0], alt),
            interp1([range[0], 0], [0.0, 0.0], alt),
            interp1([range[0], 0], [0.0, 1.0], alt)
        ]
    else:
        return [
            interp1([0, range[1]], [0.0, 1.0], alt),
            interp1([0, range[1]], [1.0, 1.0], alt),
            interp1([0, range[1]], [0.0, 1.0], alt)
        ]

def main(tifPath, colorMap=defaultColorMap):
    """
    Primary entry point for command-line invocation. Reads the given .TIF
    numerical data (e.g., altitude in meters) and converts it to a
    three-channel .PNG that is written to the same file (with an extension
    swap). Also reports a basic message when finished to STDOUT.
    """
    tif = imageio.imread(tifPath)
    J, I = tif.shape
    rgb = numpy.zeros((J, I, 3))
    lowest = tif.min()
    highest = tif.max()
    for j in range(J):
        for i in range(I):
            rgb[j,i,:] = colorMap(tif[j,i], [lowest, highest])
    pngPath = tifPath.replace(".tif", ".png")
    png = (rgb * 255).astype(numpy.uint8)
    imageio.imwrite(pngPath, png)
    print("Exported %u [px] x %u [px] heightmap to %s" % (J, I, pngPath))

if __name__ == "__main__":
    main(*sys.argv[1:])
