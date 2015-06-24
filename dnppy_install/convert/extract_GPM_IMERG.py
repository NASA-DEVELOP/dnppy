__author__ = 'jwely'

from _extract_HDF_layer_data import _extract_HDF_layer_data

__all__ = ["extract_GPM_IMERG"]

def extract_GPM_IMERG(afile, layer_indexs = None, outpath = None):


    #
    if layer_indexs is None:
        layer_indexs = range(0,8)

    gpm_data = _extract_HDF_layer_data(afile, layer_indexs)

    for layer_index in layer_indexs:
        layer = gpm_data[layer_index]
        print layer




if __name__ == "__main__":
    rasterpath = r"C:\Users\jwely\Desktop\troubleshooting\3B-HHR-L.MS.MRG.3IMERG.20150401-S233000-E235959.1410.V03E.RT-H5"
    extract_GPM_IMERG(rasterpath)