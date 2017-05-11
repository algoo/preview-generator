from PyPreviewGenerator.factory import PreviewBuilderFactory


class PreviewManager(object):

    cache_path = ''
    factory = PreviewBuilderFactory()

    def __init__(self, path: str):
        if path[-1] != '/':
            path = path + '/'
        self.cache_path = path

    def get_nb_page(self, file_path, cache_path):
        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)

        page_nb = builder.get_page_number(file_path, cache_path)
        return page_nb

    def get_jpeg_preview(self, file_path: str, page=None, height=256, width=None, force: bool=False):

        if width == None:
            width = height

        size = (height, width)

        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)
        extension = '.jpeg'
        return builder.get_jpeg_preview(
            file_path=file_path,
            page_id=page,
            cache_path=self.cache_path,
            extension=extension,
            force=force,
            size=size
        )

    def get_pdf_preview(self, file_path: str, force: bool=False, page='full'):

        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)
        extension = '.pdf'
        return builder.get_pdf_preview(
            file_path=file_path,
            cache_path=self.cache_path,
            force=force,
            extension=extension,
            page=page,
        )

    def get_text_preview(self, file_path: str, page=0, force: bool=False):

        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)
        extension = '.txt'
        return builder.get_text_preview(
            file_path=file_path,
            page_id=page,
            cache_path=self.cache_path,
            force=force,
            extension=extension
        )

    def get_html_preview(self, file_path: str, page=0, force: bool=False):
        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)
        extension = '.html'
        return builder.get_html_preview(
            file_path=file_path,
            page_id=page,
            cache_path=self.cache_path,
            extension=extension
        )

    def get_json_preview(self, file_path: str, page=0, force: bool=False):
        mimetype = self.factory.get_document_mimetype(file_path)
        builder = self.factory.get_preview_builder(mimetype)
        extension = '.json'
        return builder.get_json_preview(
            file_path=file_path,
            page_id=page,
            cache_path=self.cache_path,
            force=force,
            extension=extension
        )