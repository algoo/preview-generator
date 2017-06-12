# If you could put only preview_[type].py files here,
# that would be great


from os.path import dirname, basename, isfile
import glob
modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f)]



for file in __all__:
    if file == '__init__':
        continue
    imp = 'from preview_generator.preview.{file} import *'.format(
        file=file
    )
    exec(imp)

