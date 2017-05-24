import magic
import typing


class PreviewBuilderFactory(object):
    _instance = None  # type: PreviewBuilderFactory
    builders_classes = []  # type: typing.List[PreviewBuilder]

    def __init__(self) -> None:
        pass

    def get_preview_builder(self, mimetype: str) -> typing.Type[
        'PreviewBuilder']:

        for builder_class in self.builders_classes:
            for mimetype_supported in builder_class.get_mimetypes_supported():
                if mimetype == mimetype_supported:
                    return builder_class()

        raise Exception('Mimetype not supported')

    def get_document_mimetype(self, file_path: str) -> str:
        """ 
        return the mimetype of the file. see python module mimetype
        """
        mime = magic.Magic(mime=True)
        str = mime.from_file(file_path)
        return str

    @classmethod
    def get_instance(cls) -> 'PreviewBuilderFactory':
        if not PreviewBuilderFactory._instance:
            cls._instance = PreviewBuilderFactory()

        return cls._instance

    def register_builder(self, builder: typing.Type['PreviewBuilder']) -> None:
        self.builders_classes.append(builder)


from preview_generator.preview.generic_preview import PreviewBuilder

for cls in PreviewBuilder.__subclasses__():
    cls.register()
