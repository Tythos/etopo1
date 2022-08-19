"""
Samples a subset of the relief GeoTIFF (global reference) stored in the
untracked folder "store", based on a KML-defined polygon, then writes the
result to a new .TIF file (based on the .KML file path and name)::

  > python sample.py
  Sampling for quad between lat [33.250000,33.787000] and lon [-118.661000,-117.572000]
  Result sampled at 10 points-per-degree for a final resolution of 128 [px] x 128 [px]
  >
"""

import os
import sys
import math
import bs4
import numpy
from scipy import interpolate
from imageio import v3 as imageio

MOD_PATH, _ = os.path.split(os.path.abspath(__file__))
GEOTIFF_PATH = MOD_PATH + "/store/ETOPO1_Bed_g_geotiff.tif"

def getQuad(kmlPath):
    """
    Extracts quad boundaries based on the coordinates from the first polygon
    found in the given .KML file. Returns a four-element list defining min/max
    lat and min/max lon, respectively.
    """
    with open(kmlPath, 'r') as f:
        kml = f.read()
    soup = bs4.BeautifulSoup(kml, features="xml")
    poly = soup.find("Polygon")
    coords = poly.find("coordinates")
    parts = coords.text.split()
    lats = []
    lons = []
    for part in parts:
        values = [float(v) for v in part.split(",")]
        lats.append(values[1])
        lons.append(values[0])
    latMin = min(lats)
    latMax = max(lats)
    lonMin = min(lons)
    lonMax = max(lons)
    print("Sampling for quad between lat [%f,%f] [deg] and lon [%f,%f] [deg]" % (latMin, latMax, lonMin, lonMax))
    return [latMin, latMax, lonMin, lonMax]

def interp1(xx, yy, x):
    """
    Basic 1d linear interpolation.
    """
    pct = (x - xx[0]) / (xx[1] - xx[0])
    return yy[0] + pct * (yy[1] - yy[0])

def main(kmlPath, ppd=50):
    """
    Entry point for command-line invocation. Derives quad definition from the
    given KML, then resamples global relief data for that quad with the given
    resolution (points-per-degree), defaulting to 100 px/deg. The result is
    written to a .TIF file whose path and name are determined from the .KML
    file (adjacent, and with the same filename, but a different extension).
    """
    quad = getQuad(kmlPath)
    topo = imageio.imread(GEOTIFF_PATH)
    J, I = topo.shape
    y0 = interp1([90, -90], [0, J], quad[1])
    yF = interp1([90, -90], [0, J], quad[0])
    x0 = interp1([-180, 180], [0, I], quad[2])
    xF = interp1([-180, 180], [0, I], quad[3])
    j0 = math.floor(y0)
    jF = math.ceil(yF)
    i0 = math.floor(x0)
    iF = math.ceil(xF)
    jj = [j for j in range(j0, jF)]
    ii = [i for i in range(i0, iF)]
    alt = numpy.take(numpy.take(topo, jj, 0), ii, 1)
    rbs = interpolate.RectBivariateSpline(jj, ii, alt)
    yy = numpy.arange(y0, yF, 1.0 / ppd)
    xx = numpy.arange(x0, xF, 1.0 / ppd)
    alt = rbs(yy, xx)
    tifPath = kmlPath.replace(".kml", ".tif")
    imageio.imwrite(tifPath, alt)
    print("Result sampled at %f [points/degree] for a final resolution of %u [px] x %u [px]" % (ppd, len(yy), len(xx)))

if __name__ == "__main__":
    main(*sys.argv[1:])
