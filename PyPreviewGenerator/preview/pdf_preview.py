from io import BytesIO

from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter

from PyPreviewGenerator import file_converter
from PyPreviewGenerator.preview.generic_preview import PreviewBuilder



class PdfPreviewBuilder(PreviewBuilder):

    mimetype = ['application/pdf']

    def build_jpeg_preview(self, file_path, preview_name, cache_path, page_id: int, extension='.jpg', size=(256,256)):
        """
        generate the pdf small preview
        """
        # try:
        #     os.mkdir(cache_path.format(d_id=document_id))
        # except OSError:
        #     pass

        with open(file_path, 'rb') as pdf:
            input_pdf = PdfFileReader(pdf)
            output_pdf = PdfFileWriter()
            output_pdf.addPage(input_pdf.getPage(int(page_id)))
            output_stream = BytesIO()
            output_pdf.write(output_stream)
            output_stream.seek(0, 0)
            result = file_converter.pdf_to_jpeg(output_stream, size)

            with open('{path}_{page_id}_{extension}'.format(
                            path=cache_path + preview_name,
                            page_id=page_id,
                            extension=extension
                    ), 'wb') as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)

    def get_page_number(self, file_path, preview_name, cache_path):

        # try:
        #     os.mkdir(cache_path.format(d_id=document_id)+'/')
        # except OSError:
        #     pass

        with open(cache_path + preview_name + '_page_nb', 'w') as count:
            count.seek(0, 0)

            with open(file_path, 'rb') as doc:
                inputpdf = PdfFileReader(doc)
                count.write(str(inputpdf.numPages))
        with open(cache_path + preview_name + '_page_nb', 'r') as count:
            count.seek(0, 0)
            return count.read()