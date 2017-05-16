import os
import zipfile
from io import BytesIO
from PIL import Image
from wand.color import Color
from wand.image import Image as WImage
import json



def image_to_jpeg_pillow(png, preview_size=(256, 256)) -> BytesIO:
    print('Converting png to jpeg of size ', preview_size)
    temp = Image.new('RGB', (preview_size[1], preview_size[0]), (255, 255, 255))
    print(temp.size)
    with Image.open(png) as image:
        b, a = image.size
        x, y = preview_size
        size_rate = (a/b)/(x/y)
        if size_rate > 1:
            a = int(a * (y / b))
            b = int(b * (y / b))
        else:
            b = int(b * (x / a))
            a = int(a * (x / a))
        image = image.resize((b, a))
        left = int((b/2)-(y/2))
        top = int((a/2)-(x/2))
        width = left + y
        height = top + x
        box = (left, top, width, height)
        layer_copied = image.crop(box)
        try:
            temp.paste(layer_copied, (0, 0), layer_copied)
        except ValueError:
            temp.paste(layer_copied)
        output = BytesIO()
        temp.save(output, 'jpeg')
        output.seek(0, 0)
        return output


def image_to_jpeg_wand(jpeg, preview_size=(256, 256)):
    '''
    for jpeg, gif and bmp
    :param jpeg: 
    :param size: 
    :return: 
    '''
    print('Converting an image to jpeg of size ', preview_size)
    with WImage(file=jpeg) as image:
        b, a = image.size
        x, y = preview_size
        size_rate = (a / b) / (x / y)
        if size_rate > 1:
            a = int(a * (y / b))
            b = int(b * (y / b))
        else:
            b = int(b * (x / a))
            a = int(a * (x / a))
        image.resize(b, a)
        left = int((b / 2) - (y / 2))
        top = int((a / 2) - (x / 2))
        width = left + y
        height = top + x
        image.crop(left, top, width, height)
        content_as_bytes = image.make_blob('jpeg')
        output = BytesIO()
        output.write(content_as_bytes)
        output.seek(0, 0)
        return output

def pdf_to_jpeg(pdf, size=(256,256)):

    print('convert pdf to jpeg of size ', size)
    with WImage(file=pdf) as img:
        height, width = img.size
        if height < width:
            breadth = height
        else:
            breadth = width
        with WImage(
            width=breadth,
            height=breadth,
            background=Color('white')
        ) as image:
            image.composite(
                img,
                top=0,
                left=0
            )
            image.crop(0, 0, width=breadth, height=breadth)
            # image.resize(size[1], size[0])
            content_as_bytes = image.make_blob('jpeg')
            output = BytesIO()
            output.write(content_as_bytes)
            output.seek(0, 0)
            return output

def office_to_pdf(odt, cache_path: str, file_name):
    print('convert office document to pdf ')
    print(file_name)
    try:
        os.mkdir(cache_path + file_name + '_flag')
    except OSError:
        pass

    if not os.path.exists('{path}{file_name}'.format(
                        path=cache_path,
                        file_name=file_name)
    ):

        with open('{path}{file_name}'.format(
                        path=cache_path,
                        file_name=file_name), 'wb') \
        as odt_temp:
            odt.seek(0, 0)
            buffer = odt.read(1024)
            while buffer:
                odt_temp.write(buffer)
                buffer = odt.read(1024)

        try:
            os.makedirs(cache_path)
        except OSError:
            pass

        #TODO There's probably a cleaner way to convert to pdf
        os.system('libreoffice --headless --convert-to pdf:writer_pdf_Export '
                     + '{path}{extension}'.format(
                                                path=cache_path,
                                                extension=file_name
                                                 )
                     + ' --outdir ' + cache_path
                     + ' -env:UserInstallation='
                     + 'file:///tmp/LibreOffice_Conversion_${USER}')

    try:
        os.removedirs(cache_path + file_name + '_flag')
    except OSError:
        pass


    try:
        os.remove('{path}{file_name}'.format(
            path=cache_path,
            file_name=file_name
            )
        )
    except OSError:
        pass
    with open('{path}{file_name}.pdf'.format(
        path=cache_path,
        file_name=file_name
    ), 'rb') as pdf:
        pdf.seek(0, 0)
        content_as_bytes = pdf.read()
        output = BytesIO(content_as_bytes)
        output.seek(0, 0)

        return output

def txt_to_txt(text):
    return text

def zip_to_txt(zip):

    zz = zipfile.ZipFile(zip)
    output = BytesIO()
    for line, info in enumerate(zz.filelist):
        date = "%d-%02d-%02d %02d:%02d:%02d" % info.date_time[:6]
        # output.seek(0, 0)
        output.write(str.encode("%-46s %s %12d\n" % (info.filename, date, info.file_size)))
    output.seek(0, 0)
    return output

def zip_to_html(zip):
    zz = zipfile.ZipFile(zip)
    output = BytesIO()
    output.write(str.encode('<p><ul>'))
    for line, info in enumerate(zz.filelist):
        date = "%d-%02d-%02d %02d:%02d:%02d" % info.date_time[:6]
        # output.seek(0, 0)
        output.write(
            str.encode(
                "<li>%-46s %s %12d</li>\n" % (info.filename, date, info.file_size)
            )
        )
    output.write(str.encode('</ul></p>'))
    output.seek(0, 0)
    return output


def zip_to_json(zip)->BytesIO:
    zz = zipfile.ZipFile(zip)
    output = BytesIO()
    files = []
    dictionnary = {}
    for line, info in enumerate(zz.filelist):
        date = '%d-%02d-%02d %02d:%02d:%02d' % info.date_time[:6]
        files.append(['', '', ''])
        files[line][0] = info.filename
        files[line][1] = info.file_size
        files[line][2] = date
    dictionnary['file'] = files
    content = json.dumps(dictionnary)
    output.write(str.encode(content))
    output.seek(0, 0)
    return output

def html_to_html(html)->BytesIO:
    a = 1

def image_to_json(img):
    print('Converting image to json')
    info={}
    with Image.open(img) as image:
        info['height'] = image.size[0]
        info['width'] = image.size[1]
        output = BytesIO()
        try:
            image.save(output, 'JPEG')
        except OSError:
            image.save(output, 'GIF')
        contents = output.getvalue()
        output.close()
        info['size'] = len(contents)
    output = BytesIO()
    content = json.dumps(info)
    output.write(str.encode(content))
    output.seek(0, 0)
    return output