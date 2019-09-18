# -*- coding: utf-8 -*-


class PreviewGeneratorException(Exception):
    pass


class IntermediateFileBuildingFailed(PreviewGeneratorException):
    """
    Exception raised when building of intermediate file failed.
    """

    pass


class PreviewAbortedMaxAttempsExceeded(PreviewGeneratorException):
    """
    Exception raised when max attemps of preview generation are exceeded.
    """

    pass


class UnavailablePreviewType(PreviewGeneratorException):
    """
    Exception raised when a preview method is not implemented for the type of
    file you are processing
    """

    pass


class UnsupportedMimeType(PreviewGeneratorException):
    """
    Exception raised when a file mimetype is not found in supported mimetypes
    """

    pass


class InputExtensionNotFound(PreviewGeneratorException):
    """
    Exception raised if input extension is not found from mimetype.
    """

    pass


class BuilderNotLoaded(PreviewGeneratorException):
    """
    Exception raised when the factory is used but no builder has been loaded
    You must call factory.load_builders() before to use the factory
    """

    pass


class BuilderDependencyNotFound(PreviewGeneratorException):
    pass
