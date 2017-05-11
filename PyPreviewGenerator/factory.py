import magic


class PreviewBuilderFactory(object):

    _instance = None
    builders_classes = []

    def __init__(self):
        pass

    def get_preview_builder(self, mimetype: str):

        for builder_class in self.builders_classes:
            for mimetype_supported in builder_class.get_mimetypes_supported():
                if mimetype == mimetype_supported:
                    return builder_class()

        return None


    def get_document_mimetype(self, file_path) -> str:
        """ 
        return the mimetype of the file. see python module mimetype
        """
        mime = magic.Magic(mime=True)
        str = mime.from_file(file_path)
        return str

    @classmethod
    def get_instance(cls):
        if not PreviewBuilderFactory._instance:
            cls._instance = PreviewBuilderFactory()

        return cls._instance

    def register_builder(self, builder):
        self.builders_classes.append(builder)

from PyPreviewGenerator.preview.generic_preview import PreviewBuilder

for cls in PreviewBuilder.__subclasses__():
    cls.register()