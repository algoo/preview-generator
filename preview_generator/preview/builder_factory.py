# -*- coding: utf-8 -*-

import glob
import logging
import os
from os.path import basename
from os.path import dirname
from os.path import isfile
from subprocess import PIPE
from subprocess import Popen
from threading import RLock
import typing

import magic

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import BuilderNotLoaded
from preview_generator.exception import UnsupportedMimeType
from preview_generator.extension import mimetypes_storage
from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.utils import LOGGER_NAME
from preview_generator.utils import get_subclasses_recursively

PB = typing.TypeVar("PB", bound=PreviewBuilder)

AMBIGUOUS_MIMES = [
    "text/xml",
    "text/plain",
    "application/xml",
    "application/octet-stream",
    "image/tiff",
    "audio/ogg",
]


class PreviewBuilderFactory(object):

    _instance = None  # type: PreviewBuilderFactory
    _singleton_lock = RLock()  # type: RLock

    def __init__(self) -> None:
        self.builders_loaded = False
        self.builders_classes = []  # type: typing.List[typing.Any]
        self._builder_classes = {}  # type: typing.Dict[str, type]
        self.logger = logging.getLogger(LOGGER_NAME)

    def get_preview_builder(self, mimetype: str) -> PreviewBuilder:

        if not self.builders_loaded:
            raise BuilderNotLoaded()

        try:
            return self._builder_classes[mimetype]()  # nopep8 get class and instantiate it
        except KeyError:
            raise UnsupportedMimeType("Unsupported mimetype: {}".format(mimetype))

    def get_file_mimetype(self, file_path: str, file_ext: str = "") -> str:
        """
        return the mimetype of the file. see python module mimetype
        """

        assert file_ext == "" or file_ext.startswith("."), 'File extension must starts with ".""'
        # INFO - B.L - 2018/10/11 - If user force the file extension we do.
        first_path = file_path + file_ext if file_ext else file_path
        str_, encoding = mimetypes_storage.guess_type(first_path, strict=False)

        if not str_ or str_ == "application/octet-stream":
            mime = magic.Magic(mime=True)
            str_ = mime.from_file(file_path)

        if str_ and (str_ in AMBIGUOUS_MIMES):
            raw_mime = Popen(
                ["mimetype", "--output-format", "%m", file_path],
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
            ).communicate()[0]
            str_ = raw_mime.decode("utf-8").replace("\n", "")

        if not str_:
            # Should never happen.
            raise ValueError("Cannot determine the type of " + file_path)

        return str_

    def load_builders(self, force: bool = False) -> None:
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
                if cls.__name__ == "ImagePreviewBuilderWand":
                    self.logger.info(
                        "ImagePreviewBuilderWand builder is deprecated and is not registered by default. Consider using ImagePreviewBuilderIMConvert instead"
                    )
                else:
                    self.register_builder(cls)

            self.builders_loaded = True

    @classmethod
    def get_instance(cls) -> "PreviewBuilderFactory":
        # INFO - G.M - 2018-11-07 - lock to prevent case when
        # PreviewBuilderFactory exist but builder aren't yet loaded
        with cls._singleton_lock:
            if not cls._instance:
                cls._instance = PreviewBuilderFactory()
                cls._instance.load_builders()

        return cls._instance

    def register_builder(self, builder: typing.Type["PreviewBuilder"]) -> None:
        try:
            builder.check_dependencies()
            builder.update_mimetypes_mapping()
            self.builders_classes.append(builder)
            # FIXME - G.M - 2018-10-18 - Fix issue with application/octet-stream
            # and builder which happened in some conditions
            # like automatic travis test with Ubuntu 14.04.5 LTS,
            # where ImagePreviewBuilderIMConvert pretend to
            # be able to deal with application/octet-stream mimetype
            for mimetype in builder.get_supported_mimetypes():
                if mimetype == "application/octet-stream":
                    self.logger.critical(
                        "register builder for {}: {} - SKIPPED".format(mimetype, builder.__name__)
                    )
                else:
                    self._builder_classes[mimetype] = builder
                    self.logger.debug(
                        "register builder for {}: {}".format(mimetype, builder.__name__)
                    )
        except BuilderDependencyNotFound as e:
            self.logger.error("Builder {} is missing a dependency: {}".format(builder, e.__str__()))
        except NotImplementedError:
            self.logger.info(
                "Skipping builder class [{}]: method get_supported_mimetypes "
                "is not implemented".format(builder)
            )

    def get_supported_mimetypes(self) -> typing.List[str]:
        """
        Return the list of supported mimetypes.
        :return:
        """
        return [mime for mime in self._builder_classes.keys()]

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
    return os.path.join(dirname(__file__), "builder")


def get_builder_modules(builder_folder: str) -> typing.List[str]:
    files = glob.glob(builder_folder + "/*.py")
    module_names = []
    for builder_file in files:
        if isfile(builder_file):
            module_name = basename(builder_file)[:-3]  # nopep8 remove path and extension
            if module_name != "__init__":
                module_names.append(module_name)
    return module_names


def import_builder_module(name: str) -> None:
    logger = logging.getLogger(LOGGER_NAME)
    logger.debug("Builder module loading: {}".format(name))
    _import = "from preview_generator.preview.builder.{module} import *".format(
        module=name
    )  # nopep8
    exec(_import)
    logger.info("Builder module loaded: {}".format(name))
