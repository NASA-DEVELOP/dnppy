__author__ = 'jwely'

import h5py
import os

def HDF5_to_numpy(hdfpath, layers = None):
    """
    Extracts one or more layers from an HDF5 file and returns a dict of numpy arrays

    :param hdfpath:         filepath to an HDF5 file
    :param layers:          a list of integer values or layer names to extract
                            leave "None" to return numpy arrays for ALL layers

    :return:                dict with band names as keys and numpy arrays as values
    """

    with h5py.File(hdfpath, "r", driver = "core") as hdf:
        group  = hdf[list(hdf)[0]]
        bands  = list(group)

        # print info about each dataset
        print("Contents of {0}".format(os.path.basename(hdfpath)))
        for i,x in enumerate(group.values()):
            print i,x

        if layers is None:
            layers = bands

        elif isinstance(layers, str) or isinstance(layers, int):
            layers = [layers]

        # verify that the desired layer can be extracted
        for i, layer in enumerate(layers):
            if isinstance(layer, int) and layer <= len(bands):
                layers[i] = bands[layer]
            elif isinstance(layer, str) and layer in bands:
                layers[i] = layer

        layer_dict ={}
        for layer in layers:
            try:
                layer_dict[layer] = group[layer][()]
            except:
                print("Failed to read layer '{0}'".format(layer))

    return layer_dict


if __name__ == "__main__":
    rasterpath = r"C:\Users\jwely\Desktop\troubleshooting\3B-HHR-L.MS.MRG.3IMERG.20150401-S233000-E235959.1410.V03E.RT-H5"
    output = HDF5_to_numpy(rasterpath, [2,3,5])

    print output.keys()