"""
An IPython extension for generating and displaying asymptote figures within
an IPython notebook. Refer to examples directory for usage examples.
"""
import os
import shutil
import subprocess
import tempfile
from IPython.core.magic import (
    magics_class, line_magic, line_cell_magic, Magics)
from IPython.core.magic_arguments import (
    argument, magic_arguments, parse_argstring)
from IPython.display import Image, SVG

class AsymptoteException(RuntimeError):
    """
    Simple wrapper class for wrapping Asymptote
    interpreter error messages in a stack trace.
    """
    
    def __init__(self, asy_err_msg):
        self.asy_err_msg = asy_err_msg
        
    def __str__(self):
        return str(self.asy_err_msg)

class TemporaryAsymptoteFile(object):
    """
    Temporary locations to write asymptote code files
    compatible with python's "with" construct.
    """
    
    def __init__(self, asy_codes):
        """
        Parameters
        ----------
        asy_code : list(str) - list of strings, each string
            corresponding to code for an Asymptote file
            (including newlines, etc).
        """
        self.tmp_dir = tempfile.mkdtemp()
        self.asy_files = []
        if not isinstance(asy_codes, list):
            asy_codes = [asy_codes]
        for asy_code in asy_codes:
            asy_fd, asy_file = tempfile.mkstemp(
                suffix=".asy", dir=self.tmp_dir)
            with os.fdopen(asy_fd, "w") as asy_fh:
                asy_fh.write(asy_code)
            self.asy_files.append(asy_file)
        
    def __enter__(self):
        return self
        
    def __exit__(self, type, value, tb):
        shutil.rmtree(self.tmp_dir)
            
@magics_class
class AsymptoteMagic(Magics):
    """
    Define a line/cell IPython magic %asy which takes
    a pre-existing asy code file and additional asy code
    entered into the IPython cell, and outputs image
    rendered by Asymptote.
    
	TODO: retain asymptote interpreter history between
	multiple asymptote code cells. For example, can define
	common setup (diagram size, pens) in this manner.
    TODO: implement way to communicate between python and
    asymptote, similar to Rpush/Rpull IPython magics. Should
    be easy with an api similar to http://emmett.ca/PyAsy/.
    """
    
    def __init__(self, shell, cache_display_data=False):
        super(AsymptoteMagic, self).__init__(shell)
        self.cache_display_data = cache_display_data
    
    @magic_arguments()
    @argument(
        'asy_file', nargs="?",
        help="Name of existing .asy file"
        )
    @argument(
        '-f', '--fmt', '--outformat', default="png",
        choices=["png", "jpg", "tiff", "gif", "xpm", "xbm", "pbm", "svg"],
        help="Convert each output image to specified format "
             "(compatible with IPython.display and asy,     "
             "possibly requires ImageMagick)                "
        )
    @argument(
        '-r', '--root',
        help="Save asymptote code and image to this root path"
        )
    @line_cell_magic
    def asy(self, line, cell=None):
        """Generate and display a figure using asymptote.
        
        To run an existing asymptote file, use the IPython magic:
        
            %asy filename.asy
            
        Asymptote code can also be entered into an IPython cell:
        
            %%asy
            size(100); draw(unitsquare);
            
        This writes the cell's contents to a temporary .asy file and
        outputs a temporary image for IPython to display. By default,
        the image is a png, since this requires the least setup. This
        can be changed using the -f argument, although Asymptote may
        require other third-party programs like ImageMagick for other
        formats. The asy file and image can be saved to a non-temporary
        location using the -r argument (asy code will be saved to
        root.asy and image to root.image_extension).
        """
        args = parse_argstring(self.asy, line)
        
        if cell is not None:
            # If any asymptote code is provided in cell,
            # write code to an intermediate .asy file.
            if args.asy_file:
                with open(args.asy_file) as asy_fh:
                    cell = asy_fh.read() + "\n" + cell
                    
            if args.root:
                # If root is specified, retain intermediate .asy file.
                asy_file = args.root + ".asy"
                with open(asy_file, "w") as asy_fh:
                    asy_fh.write(cell)
                return self.run_asy(asy_file, fmt=args.fmt)
            else:
                # If a filename is not specified (most use cases),
                # intermediate asymptote file and image are written
                # in a temporary directory and then cleaned up.
                # This avoids over-cluttering files.
                with TemporaryAsymptoteFile(cell) as tmp_asy:
                    return self.run_asy(tmp_asy.asy_files[0], fmt=args.fmt)
                    
        elif args.asy_file:
            return self.run_asy(args.asy_file, fmt=args.fmt)
        
    def run_asy(self, asy_file, img_file=None, fmt="png"):
        """Runs asy code in asy_file and returns IPython image"""
        asy_img, asy_stdout = run_asy_file(asy_file, img_file, fmt)
        print(asy_stdout)
        return asy_img
        
def run_asy_file(asy_file, img_file=None, fmt="png"):
    """Runs asymptote code located in asy_file and writes to
    img_file if specified, otherwise use's asymptote's default
    output location. Returns tuple (IPython.display, stdout).
    """
    if not os.path.exists(asy_file):
        raise IOError("File not found: " + asy_file)
    if img_file is None:
        img_file = asy_file[:-3] + fmt
          
    asy_proc = subprocess.Popen(["asy", "-noView", "-f", fmt,
                                 "-o", img_file, asy_file],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    asy_ret_code = asy_proc.wait()
    if asy_ret_code != 0:
        raise AsymptoteException(asy_proc.stderr.read())
        
    asy_stdout = asy_proc.stdout.read()
    
    if fmt == "svg":
        return SVG(filename=img_file), asy_stdout
    return Image(filename=img_file), asy_stdout

def load_ipython_extension(ipython):
    ipython.register_magics(AsymptoteMagic)