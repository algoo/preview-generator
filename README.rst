==================================
Preview-generator Documentation
==================================

.. image:: https://travis-ci.org/algoo/preview-generator.svg?branch=master
    :target: https://travis-ci.org/algoo/preview-generator

------------
Presentation
------------

preview-generator is a library for generating preview - thumbnails, pdf, text and json overview
for all your file-based content. This module gives you access to jpeg, pdf, text, html and json
preview of virtually any kind of file. It also includes a cache mechanism so you do not have to
care about preview storage.

By creating this module, the goal was to delegate the responsibility of building preview
of files managed by `tracim <https://github.com/tracim/tracim/.>`_.

The changelog is available `in a separate file <CHANGELOG.rst>`_.

----------------------
Supported file formats
----------------------

Supported mimetypes depends on builders and dependencies installed.

full supported list file format here: `supported mimetypes list`_ .

Preview-generator has builders for:

Images
~~~~~~

- Raster graphic image formats : png, jpeg, bmp, tiff, gif, …
- Vectorial graphic format: svg
- Camera raw format: dng, arw, …

Office/Text Document
~~~~~~~~~~~~~~~~~~~~

- simple text file : txt, json, …
- office document: odt, doc, docx
- pdf document

Those file formats are generated using libreoffice.
The preview generation has a default timeout of 60 seconds.
It is possible to change this timeout by setting the `LIBREOFFICE_PROCESS_TIMEOUT` environment variable to a number of seconds.
Setting a zero or negative value for this variable will disable the timeout.

Archive file
~~~~~~~~~~~~

- zip, tar, …

3D File
~~~~~~~

- support for geometric file: .ply, .obj, .stl

Video format
~~~~~~~~~~~~

- support for multiples image preview of video : .mp4, .flv, .webm, .ogv, .wmv, etc.

.. _`Supported mimetypes list`: doc/supported_mimetypes.rst

------------
Installation
------------


Mandatory Dependencies:
~~~~~~~~~~~~~~~~~~~~~~~

On debian :

.. code:: console

  apt-get install poppler-utils qpdf libfile-mimeinfo-perl libimage-exiftool-perl ghostscript libsecret-1-0 zlib1g-dev libjpeg-dev


install preview_generator without external addons:

.. code:: console

  pip install preview-generator


To install all previews builders dependencies:

.. code:: console

  pip install preview-generator[all]
  sudo apt-get install libreoffice inkscape ufraw-batch ffmpeg xvfb
  DRAWIO_VERSION="12.6.5" && curl -LO https://github.com/jgraph/drawio-desktop/releases/download/v${DRAWIO_VERSION}/draw.io-amd64-${DRAWIO_VERSION}.deb && sudo dpkg -i draw.io-amd64-${DRAWIO_VERSION}.deb


To check dependencies, you can run:

.. code:: console

  preview --check-dependencies

Office Files (LibreOffice)
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: console

  apt-get install libreoffice


DTP(Scribus)
~~~~~~~~~~~~
If you need to preview scribus `.sla` files you will need scribus >= 1.5.

On debian :

.. code:: console

  apt-get install scribus xvfb
  pip install preview-generator[scribus]



If scribus >=1.5 is not available in your distribution you can use an AppImage.

Download the last AppImage from the official website https://www.scribus.net/downloads/unstable-branch/

.. code:: console

  mv /path/to/image/scribus-x.y.appimage /usr/local/bin/scribus
  chmod +x /usr/local/bin/scribus


Vector Images (Inkscape)
~~~~~~~~~~~~~~~~~~~~~~~~

on debian:

.. code:: console

  apt-get install inkscape



Vector Images (cairosvg)
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: console

  pip install preview-generator[cairosvg]


Video(ffmpeg)
~~~~~~~~~~~~~

On debian :

.. code:: console

  apt-get install ffmpeg
  pip install preview-generator[video]


RAW Images(ufraw-batch)
~~~~~~~~~~~~~~~~~~~~~~~

On debian :

.. code:: console

  apt-get install ufraw-batch


Diagram(DrawIO)
~~~~~~~~~~~~~~~

1. install xvfb
2. install `draw-io package`_:
3. install python specific dependencies:

.. _draw-io package: https://github.com/jgraph/drawio-desktop/releases

on debian:

.. code:: console

  apt install xvfb
  DRAWIO_VERSION="12.6.5" && curl -LO https://github.com/jgraph/drawio-desktop/releases/download/v${DRAWIO_VERSION}/draw.io-amd64-${DRAWIO_VERSION}.deb && sudo dpkg -i draw.io-amd64-${DRAWIO_VERSION}.deb
  pip install preview-generator[drawio]



3D files (VTK)
~~~~~~~~~~~~~~

:warning: VTK lib provided from pypi may not be builded for latest python version. You can either decide to downgrade python version or build VTK yourself to make things work as expected.


On debian :

.. code:: console

  pip install preview-generator[3D]


HEIC support
~~~~~~~~~~~~

Building ImageMagick with heic support: `Building ImageMagick with heic support`_ .

.. _`Building ImageMagick with heic support`: doc/build_im_with_heic_support.rst


-----
Usage
-----

Here are some examples of code

-----------
Basic Usage
-----------

Most basic usage, create a jpeg from a png, default size 256x256

.. code:: python

  from preview_generator.manager import PreviewManager

  cache_path = '/tmp/preview_cache'
  file_to_preview_path = '/tmp/an_image.png'

  manager = PreviewManager(cache_path, create_folder= True)
  path_to_preview_image = manager.get_jpeg_preview(file_to_preview_path)

-------------------------------------
Preview an image with a specific size
-------------------------------------

You can choose the size of your image using params width and height.

.. code:: python

  from preview_generator.manager import PreviewManager

  cache_path = '/tmp/preview_cache'
  file_to_preview_path = '/tmp/an_image.png'

  manager = PreviewManager(cache_path, create_folder= True)
  path_to_preview_image = manager.get_jpeg_preview(file_to_preview_path, width=1000, height=500)

---------------------------------------------
Preview a pdf or an office document as a jpeg
---------------------------------------------

.. code:: python

  from preview_generator.manager import PreviewManager

  cache_path = '/tmp/preview_cache'
  pdf_or_odt_to_preview_path = '/tmp/a_pdf.pdf'

  manager = PreviewManager(cache_path, create_folder= True)
  path_to_preview_image = manager.get_jpeg_preview(pdf_or_odt_to_preview_path)

By default it will generate the preview of the first page of the document.
Using params `page`, you can you pick the page you want to preview.

**page number starts at 0, if you want to preview the second page of your document then the argument will be 1 `page=1`**

.. code:: python

  from preview_generator.manager import PreviewManager

  cache_path = '/tmp/preview_cache'
  pdf_or_odt_to_preview_path = '/tmp/a_pdf.pdf'

  manager = PreviewManager(cache_path, create_folder= True)
  path_to_preview_image = manager.get_jpeg_preview(pdf_or_odt_to_preview_path, page=1)

-----------------------------------------------------
Generate a pdf preview of a libreoffice text document
-----------------------------------------------------

.. code:: python

  from preview_generator.manager import PreviewManager
  manager = PreviewManager('/tmp/cache/', create_folder= True)
  pdf_file_path = manager.get_pdf_preview('/home/user/Documents/report.odt', page=2)
  print('Preview created at path : ', thumbnail_file_path)



For Office types into PDF :
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

  cache_path = '/tmp/previews'
  preview_manager = PreviewManager(cache_path, create_folder= True)
  path_to_preview = preview_manager.get_pdf_preview(file_path,page=page_id)

-> Will create a preview from an office file into a pdf file

*args :*

  *file_path : the String of the path where is the file you want to get the preview*

  *page : the int of the page you want to get. If not mentioned all the pages will be returned. First page is page 0*

*returns :*

  *str: path to the preview file*

For images(GIF, BMP, PNG, JPEG, PDF) into jpeg :
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

  cache_path = '/tmp/previews'
  preview_manager = PreviewManager(cache_path, create_folder= True)
  path_to_preview = preview_manager.get_jpeg_preview(file_path,height=1024,width=526)

-> Will create a preview from an image file into a jpeg file of size 1024 * 526

*args :*

  *file_path : the String of the path where is the file you want to get the preview*

  *height : height of the preview in pixels*

  *width : width of the preview in pixels. If not mentioned, width will be the same as height*

*returns :*

  *str: path to the preview file*

Other conversions :
~~~~~~~~~~~~~~~~~~~

The principle is the same as above

**Zip to text or html :** will build a list of files into text/html inside the json

**Office to jpeg :** will build the pdf out of the office file and then build the jpeg.

**Text to text :** mainly just a copy stored in the cache

Command Line
~~~~~~~~~~~~

For test purposes, you can use ``preview`` from the command line,
giving the file to preview as a parameter::

  preview demo.pdf

Or multiple files::

  preview *.pdf

---------------
Cache mechanism
---------------

--------
Naming :
--------

The name of the preview generated in the cache directory will be :

{file_name}-[{size}-]{file_md5sum}[({page})]{extension}
  file_name = the name of the file you asked for a preview without the extension.

  size = the size you asked for the preview. In case of a Jpeg preview.

  file_md5sum = the md5sum of the entire path of the file. To avoid conflicts like files that have the same name but are in different directory.

  page = the page asked in case of pdf or office document preview.

  extensions = the extension of the preview (.jpeg for a jpeg, .txt for a text, etc)

---------
Example :
---------

These scripts :

GIF to JPEG :
~~~~~~~~~~~~~


.. code:: python

  import os
  from preview_generator.manager import PreviewManager
  current_dir = os.path.dirname(os.path.abspath(__file__)) +'/'

  manager = PreviewManager(path=current_dir + 'cache')
  path_to_preview = manager.get_jpeg_preview(
      file_path=current_dir + 'the_gif.gif',
      height=512,
      width=512,
  )

  print('Preview created at path : ', path_to_preview)

will print

  Preview created at path : the_gif-512x512-60dc9ef46936cc4fff2fe60bb07d4260.jpeg

ODT to JPEG :
~~~~~~~~~~~~~

.. code:: python

  import os
  from preview_generator.manager import PreviewManager
  current_dir = os.path.dirname(os.path.abspath(__file__)) +'/'

  manager = PreviewManager(path=current_dir + 'cache')
  path_to_file = manager.get_jpeg_preview(
      file_path=current_dir + 'the_odt.odt',
      page=1,
      height=1024,
      width=1024,
  )

  print('Preview created at path : ', path_to_preview)

will print

  Preview created at path : the_odt-1024x1024-c8b37debbc45fa96466e5e1382f6bd2e-page1.jpeg

ZIP to Text :
~~~~~~~~~~~~~
.. code:: python

  import os
  from preview_generator.manager import PreviewManager
  current_dir = os.path.dirname(os.path.abspath(__file__)) +'/'

  manager = PreviewManager(path=current_dir + 'cache')
  path_to_file = manager.get_text_preview(
      file_path=current_dir + 'the_zip.zip',
  )

  print('Preview created at path : ', path_to_file)

will print

  Preview created at path : the_zip-a733739af8006558720be26c4dc5569a.txt



------------
Known Issues
------------


Support for 3D file on headless server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Standard vtk library require an X server to run properly.
To make 3D file preview work on a headless server, you have two option:

1. Untested: Compile/find a vtk version correctly compiled with flags to disable x requirement (with OSMesa support)
2. Use an x framebuffer like xvfb

For the last one, this configuration is known to work:

1. install package ``xvfb``.
2. launch ``Xvfb :99 -screen 0 1x1x16 > /dev/null 2>&1 &`` (note: this use a very small x framebuffer 1x1 pixel in 16 color depth to limit video usage).
3. run python code with env var ``DISPLAY=:99.0``

------------------------------
Contribute and Developer’s Kit
------------------------------

see `here`_ .


.. _`here`: contribute.rst



-------
License
-------

MIT licensed. https://opensource.org/licenses/MIT
