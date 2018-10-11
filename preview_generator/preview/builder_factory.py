# -*- coding: utf-8 -*-

import glob
import logging
import magic
import mimetypes
import os
from os.path import dirname, basename, isfile
import typing

from subprocess import Popen
from subprocess import PIPE

from preview_generator.exception import UnsupportedMimeType
from preview_generator.exception import BuilderNotLoaded
from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import ExecutableNotFound
from preview_generator.utils import get_subclasses_recursively
from preview_generator.preview.generic_preview import PreviewBuilder


PB = typing.TypeVar('PB', bound=PreviewBuilder)

AMBIGUOUS_MIMES = [
    'text/xml', 'text/plain',
    'application/xml', 'application/octet-stream'
]


class PreviewBuilderFactory(object):

    _instance = None  # type: PreviewBuilderFactory

    def __init__(self) -> None:
        self.builders_loaded = False
        self.builders_classes = []  # type: typing.List[typing.Any]
        self._builder_classes = {}  # type: typing.Dict[str, type]

    def get_preview_builder(
            self,
            mimetype: str
    ) -> PB:

        if not self.builders_loaded:
            raise BuilderNotLoaded()

        try:
            return self._builder_classes[mimetype]()  # nopep8 get class and instantiate it
        except KeyError:
            raise UnsupportedMimeType(
                'Unsupported mimetype: {}'.format(mimetype)
            )

    def get_file_mimetype(self, file_path: str, file_ext: str='') -> str:
        """
        return the mimetype of the file. see python module mimetype
        """

        assert file_ext is '' or file_ext.startswith('.'), \
            'File extension must starts with ".""'
        # INFO - B.L - 2018/10/11 - If user force the file extension we do.
        first_path = file_path + file_ext if file_ext else file_path
        str_, encoding = mimetypes.guess_type(first_path, strict=False)

        if not str_ or str_ == 'application/octet-stream':
            mime = magic.Magic(mime=True)
            str_ = mime.from_file(file_path)

        if str_ and (str_ in AMBIGUOUS_MIMES):
            raw_mime = Popen(
                ['mimetype', '--output-format', '%m', file_path],
                stdin=PIPE, stdout=PIPE, stderr=PIPE
            ).communicate()[0]
            str_ = (
                raw_mime
                .decode("utf-8")
                .replace('\n', '')
            )

        return str_

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
                logging.debug(
                    'register builder for {}: {}'.format(
                        mimetype, builder.__name__
                    )
                )
        except (BuilderDependencyNotFound, ExecutableNotFound) as e:
            print('Builder {} is missing a dependency: {}'.format(
                builder,
                e.__str__()
            ))
        except NotImplementedError:
            print(
                'Skipping builder class [{}]: method get_supported_mimetypes '
                'is not implemented'.format(builder)
            )

    def get_supported_mimetypes(self) -> typing.List[str]:
        """
        Return the list of supported mimetypes.
        :return:
        """
        return [
            mime for mime in self._builder_classes.keys()
        ]

    def get_builder_class(self, mime: str) -> type:
        """
        Return builder class associated to given mime type
        :param mime: the mimetype. Eg image/jpeg
        :return:
        """
        return self._builder_classes[mime]


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
