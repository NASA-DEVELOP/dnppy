# standard imports
import os, shutil, time
import matplotlib.pyplot as plt


__all__=['update_fig',      # complete
         'make_fig',        # complete
         'close_fig']       # complete


def update_fig(numpy_rast, fig , im, title = False):
    """ Function to update a figure that already exists """

    if title:
        fig.suptitle(title, fontsize = 20)
        
    im.set_data(numpy_rast)
    fig.canvas.draw()
    return


def make_fig(numpy_rast, title = False):
    """ function to set up an initial figure """

    fig, ax = plt.subplots()
    fig.show()

    im = ax.imshow(numpy_rast)

    if title:
        fig.suptitle(title, fontsize = 20)
        
    im.set_data(numpy_rast)
    fig.canvas.draw()
    return fig, im


def close_fig(fig, im):
    """closes an active figure"""

    plt.close(fig)
    return
