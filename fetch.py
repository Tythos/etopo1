"""
Grabs the latest ETOPO1 dataset from the official NOAA address. Uses the
bedrock-based (e.g., does not include icecaps) data, grid-registered. The
result is extracted from the .ZIP file and written to the "store/" folder::

  > python fetch.py
  Topography written to "./store/ETOPO1_Bed_g_geotiff.tif"
  >
"""

import os
import zipfile
import requests

MOD_PATH, _ = os.path.split(os.path.abspath(__file__))
URL = "https://ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/bedrock/grid_registered/georeferenced_tiff/ETOPO1_Bed_g_geotiff.zip"

def getArchive(zipFile):
    """
    Performs an HTTP GET request against the NOAA URL and writes the resulting
    binary contents to the (untracked) store as a .ZIP file.
    """
    res = requests.get(URL)
    with open(MOD_PATH + "/store/%s" % zipFile, 'wb') as f:
        f.write(res.content)

def extractData(zipFile, tifFile):
    """
    Based on the .ZIP file name (downloaded in *getArchive()*), extracts a
    matching GeoTIFF from the archive and writes it to the same store.
    """
    with zipfile.ZipFile(MOD_PATH + "/store/%s" % zipFile, 'r') as zf:
        with zf.open(tifFile, 'r') as f:
            tif = f.read()
    with open(MOD_PATH + "/store/%s" % tifFile, 'wb') as f:
        f.write(tif)

def main():
    """
    Primary entry point for command-line invocation. Fetches the NOAA relief
    data, writes it to an untracked datastore, then extracts the GeoTIFF from
    that archive and deletes the downloaded .ZIP file. Also prints a basic
    one-line report message to STDOUT when finished.
    """
    _, zipFile = os.path.split(URL)
    tifFile = zipFile.replace(".zip", ".tif")
    getArchive(zipFile)
    extractData(zipFile, tifFile)
    os.unlink(MOD_PATH + "/store/%s" % zipFile)
    print("Topography written to %s" % tifFile)

if __name__ == "__main__":
    main()
