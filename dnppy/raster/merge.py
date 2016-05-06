# ----------------------------------------------------------------------------------------------------------------------
# Merge.py
# Created:5/2/16 by Teresa Fenn
# Takes Sentinel-2 data in its original filepath (scene, granule, tile, bands),
# shortens the filepath, and merges bands 02, 03, 04, 08, and 11 (that is: RGB, NIR, and SWIR).
# The user only needs to change the indir, which is the location of the Sentinel-2 folders, and the outdir
# ----------------------------------------------------------------------------------------------------------------------

# import sys
import os
import arcpy


def get_sub(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

# Define directories
indir = r"C:\Users\tefenn\Documents\Fellow\Pelican\S2a"
outdir = r"E:\tiffs"

# Create lists of existing scene and tile names to avoid duplicates
scenes = get_sub(indir)
snames = []
tnames = []
for path, folders, files in os.walk(outdir):
    for item in files:
        tnames.append(item[0:23])

# Locate all scenes
for scene in scenes:
    snames.append(scene[0:12])
    # Shorten scene folder name
    if len(scene) > 20:
        sname = scene[0:4] + scene[47:55]
        # If name is a duplicate, this section will append a number to the end of the folder (2, 3, 4, etc.)
        if sname in snames:
            snames.append(sname)
            x = str(snames.count(sname))
            sname = scene[0:4] + scene[47:55] + '_' + x
            os.rename(os.path.join(indir, scene), os.path.join(indir, sname))
        else:
            snames.append(sname)
            os.rename(os.path.join(indir, scene), os.path.join(indir, sname))
    # If a scene name is already shortened, the script assumes that folder has already been processed, and skips it.
    # Before skipping, the script finds the tile names and appends them to tnames to avoid duplicate tile names.
    else:
        try:
            gdir = get_sub(os.path.join(indir, scene))
            tnames.append(get_sub(os.path.join(indir, scene, gdir[2])))
        except IndexError:
            pass
        continue
    # Locates all granules
    sdir = get_sub(os.path.join(indir, sname))
    granules = get_sub(os.path.join(indir, sname, sdir[2]))
    print 'Processing files for:', sname

    for granule in granules:
        # Shortens granule name
        if len(granule) > 20:
            tname = scene[0:4] + scene[47:55] + granule[-14:-7]
            filename = tname + '.tif'
            # Appends a number to duplicate granule names, and creates the output filename.
            if filename in tnames:
                tnames.append(filename)
                x = str(tnames.count(filename) - 3)
                tname = scene[0:4] + scene[47:55] + granule[-14:-7] + '_' + x
                filename = tname + '.tif'
                os.rename(os.path.join(indir, sname, sdir[2], granule), os.path.join(indir, sname, sdir[2], tname))
            else:
                tnames.append(filename)
                os.rename(os.path.join(indir, sname, sdir[2], granule), os.path.join(indir, sname, sdir[2], tname))
        else:
            tname = granule
            filename = tname + '.tif'
        # Finds tiles
        tdir = get_sub(os.path.join(indir, sname, sdir[2], tname))
        # Next two lines create the output file path and name
        outname = os.path.join(outdir, filename)

        # Locates bands and merges them.
        for root, dirs, tiles in os.walk(os.path.join(indir, sname, sdir[2], tname, tdir[1])):
            b2 = os.path.join(indir, sname, sdir[2], tname, tdir[1], tiles[1])
            b3 = os.path.join(indir, sname, sdir[2], tname, tdir[1], tiles[2])
            b4 = os.path.join(indir, sname, sdir[2], tname, tdir[1], tiles[3])
            b8 = os.path.join(indir, sname, sdir[2], tname, tdir[1], tiles[7])
            b11 = os.path.join(indir, sname, sdir[2], tname, tdir[1], tiles[10])
            arcpy.CompositeBands_management([b2, b3, b4, b8, b11], outname)
            print filename, 'done!'
