__all__ = ["raster_fig"]

# standard imports
import matplotlib.pyplot as plt

class raster_fig:

    def __init__(self, numpy_rast, title = False):
        """ initializes the raster figure """

        self.numpy_rast = numpy_rast
        self.title      = title

        self.make_fig()
        return


    def make_fig(self):
        """ function to set up an initial figure """

        self.fig, ax = plt.subplots()
        self.fig.show()

        self.im = ax.imshow(self.numpy_rast)

        if self.title:
            self.fig.suptitle(self.title, fontsize = 20)

        self.im.set_data(self.numpy_rast)
        self.fig.canvas.draw()
        return


    def update_fig(self, numpy_rast, title = False):
        """ Function to update a figure that already exists """

        if title:
            self.fig.suptitle(title, fontsize = 20)

        self.im.set_data(numpy_rast)
        self.fig.canvas.draw()
        return


    def close_fig(self):
        """closes an active figure"""

        plt.close(self.fig)
        return
