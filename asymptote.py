"""
An IPython extension for generating asymptote figures from within ipython notebook.
"""
import os
from IPython.core.magic import magics_class, cell_magic, Magics
from IPython.display import Image, SVG

@magics_class
class Asymptote(Magics):

    @cell_magic
    def asymptote(self, line, cell):
        """Generate and display a figure using asymptote.
        
        Usage:
        
            %asymptote filname

        """
        self.filename = line
        self.code = cell

        with open(self.filename + ".asy", "w") as file:
            file.write(self.code)
    
        os.system("asy -f svg %s.asy" % self.filename)
        return SVG(filename=self.filename+".svg")


def load_ipython_extension(ipython):
    ipython.register_magics(Asymptote)
