# -*- coding: utf-8 -*-

import glob
import logging
import mimetypes
import os
from os.path import dirname, basename, isfile
import typing

from preview_generator.exception import UnsupportedMimeType
from preview_generator.exception import BuilderNotLoaded
from preview_generator.utils import get_subclasses_recursively
from preview_generator.preview.generic_preview import PreviewBuilder

class PreviewBuilderFactory(object):

    _instance = None  # type: PreviewBuilderFactory
    builders_classes = []  # type: typing.List[typing.Any]

    def __init__(self) -> None:
        self.builders_loaded = False

    def get_preview_builder(
            self,
            mimetype: str
    ) -> 'PreviewBuilder':

        if not self.builders_loaded:
            raise BuilderNotLoaded()

        for builder_class in self.builders_classes:
            for mimetype_supported in builder_class.get_mimetypes_supported():
                if mimetype == mimetype_supported:
                    return builder_class()

        raise UnsupportedMimeType('Unsupported mimetype: {}'.format(mimetype))

    def get_document_mimetype(self, file_path: str) -> str:
        """
        return the mimetype of the file. see python module mimetype
        """
        # mime = magic.Magic(mime=True)
        # str = mime.from_file(file_path)
        str, encoding = mimetypes.guess_type(file_path)
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
                cls.register()

            self.builders_loaded = True

    @classmethod
    def get_instance(cls) -> 'PreviewBuilderFactory':
        if not cls._instance:
            cls._instance = PreviewBuilderFactory()
            cls._instance.load_builders()

        return cls._instance

    def register_builder(self, builder: typing.Type['PreviewBuilder']) -> None:
        self.builders_classes.append(builder)


"""
###################
#
# utility functions for automatic builder modules loading.
#
"""


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
