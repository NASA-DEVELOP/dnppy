__author__ = 'jwely'

from dnppy import core
import matplotlib.pyplot as plt

import gdal

def extract_TRMM_HDF(filelist, layers, outdir = None):


    filelist = core.enf_filelist(filelist)
    layers   = core.enf_list(layers)

    for filename in filelist:
        dataset = gdal.Open(filename)
        subdata = [sd for sd, descr in dataset.GetSubDatasets()]
        for layer in layers:
            layerfile = gdal.Open(subdata[layer])
            layerdata = layerfile.ReadAsArray()
            layerfile = None

            fig,ax = plt.subplots(figsize = (6,6))
            ax.imshow(layerdata[:,:], cmap = plt.cm.Greys, vmin = 1000, vmax = 6000)
    return

if __name__ == "__main__":
    filelist = r"C:\Users\jwely\Desktop\dnppytest\raw\TRMM\3B42.20140101.00.7.HDF"

    extract_TRMM_HDF(filelist, [0])
