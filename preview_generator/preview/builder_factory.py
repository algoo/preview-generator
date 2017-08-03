# -*- coding: utf-8 -*-

import glob
import logging
import magic
import mimetypes
import os
from os.path import dirname, basename, isfile
import typing

from preview_generator.exception import UnsupportedMimeType
from preview_generator.exception import BuilderNotLoaded
from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import ExecutableNotFound
from preview_generator.utils import get_subclasses_recursively
from preview_generator.preview.generic_preview import PreviewBuilder


PB = typing.TypeVar('PB', bound=PreviewBuilder)

class PreviewBuilderFactory(object):

    _instance = None  # type: PreviewBuilderFactory

    def __init__(self) -> None:
        self.builders_loaded = False
        self.builders_classes = []  # type: typing.List[typing.Any]
        self._builder_classes = {}  # type: typing.Dict[typing.Any]

    def get_preview_builder(
            self,
            mimetype: str
    ) -> PB:

        if not self.builders_loaded:
            raise BuilderNotLoaded()

        try:
            return self._builder_classes[mimetype]()  # nopep8 get class and instantiate it
        except KeyError:
            raise UnsupportedMimeType('Unsupported mimetype: {}'.format(mimetype))

    def get_file_mimetype(self, file_path: str) -> str:
        """
        return the mimetype of the file. see python module mimetype
        """
        str, encoding = mimetypes.guess_type(file_path)
        if not str:
            mime = magic.Magic(mime=True)
            str = mime.from_file(file_path)
        return str

    def load_builders(self, force: bool=False) -> None:
        """
        Loads all builders found in preview_generator.preview.builder module
        :return: None
        """
        if force or not self.builders_loaded:
            builder_folder = get_builder_folder_name()
            builder_modules = get_builder_modules(builder_folder)

            for module_name in builder_modules:
                import_builder_module(module_name)

            from preview_generator.preview.generic_preview import PreviewBuilder  # nopep8
            for cls in get_subclasses_recursively(PreviewBuilder):
                self.register_builder(cls)

            self.builders_loaded = True

    @classmethod
    def get_instance(cls) -> 'PreviewBuilderFactory':
        if not cls._instance:
            cls._instance = PreviewBuilderFactory()
            cls._instance.load_builders()

        return cls._instance

    def register_builder(self, builder: typing.Type['PreviewBuilder']) -> None:
        try:
            builder.check_dependencies()
            self.builders_classes.append(builder)
            for mimetype in builder.get_supported_mimetypes():
                self._builder_classes[mimetype] = builder
        except (BuilderDependencyNotFound, ExecutableNotFound ) as e:
            print('Builder {} is missing a dependency: {}'.format(
                builder,
                e.__str__()
            ))
        except NotImplementedError:
            print(
                'Skipping builder class [{}]: method get_supported_mimetypes '
                'is not implemented'.format(builder)
            )



###############################################################################
#
# utility functions for automatic builder modules loading.
#
###############################################################################

def get_builder_folder_name() -> str:
    return os.path.join(dirname(__file__), 'builder')


def get_builder_modules(builder_folder: str) -> typing.List[str]:
    files = glob.glob(builder_folder + '/*.py')
    module_names = []
    for builder_file in files:
        if isfile(builder_file):
            module_name = basename(builder_file)[:-3]  # nopep8 remove path and extension
            if module_name != '__init__':
                module_names.append(module_name)
    return module_names


def import_builder_module(name: str) -> None:
    logging.debug('Builder module loading: {}'.format(name))
    _import = 'from preview_generator.preview.builder.{module} import *'.format(module=name)  # nopep8
    exec(_import)
    logging.info('Builder module loaded: {}'.format(name))
