# local imports
from .grab_data_info import *
from .null_values import *
from .project_resample import *
from .raster_clipping import *
from .raster_enforcement import *
from .raster_numpy_inter import *
from .raster_overlap import *
from .raster_stack import *
from .raster_statistics import *
from .temporal_fill import *


__all__=['update_fig',      # complete
         'make_fig',        # complete
         'close_fig']       # complete


def update_fig(numpy_rast, fig , im, title = False):
    """Function to update a figure that already exists"""

    if title:
        fig.suptitle(title, fontsize = 20)
        
    im.set_data(numpy_rast)
    fig.canvas.draw()
    return


def make_fig(numpy_rast, title = False):
    """function to set up an initial figure"""

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
