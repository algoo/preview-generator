from os.path import dirname, basename, isfile
import glob
modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f)]



for file in __all__:
    if file == '__init__':
        continue
    imp = 'import test_lib.{file}'.format(
        file=file
    )
    exec(imp)