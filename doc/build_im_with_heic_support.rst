*************************************
Building ImageMagick for HEIC support
*************************************


libde265
--------

.. code-block:: bash

    LIBDE265_VERSION="1.1.1" \
        && curl -L https://github.com/strukturag/libde265/releases/download/v${LIBDE265_VERSION}/libde265-${LIBDE265_VERSION}.tar.gz | tar zx \
        && cd libde265-${LIBDE265_VERSION} \
        && mkdir build \
        && cd build \
        && cmake .. \
        && make \
        && make install \

libheif
-------

.. code-block:: bash

    LIBHEIF_VERSION="1.23.1" \
        && curl -L https://github.com/strukturag/libheif/releases/download/v${LIBHEIF_VERSION}/libheif-${LIBHEIF_VERSION}.tar.gz | tar zx \
        && cd libheif-${LIBHEIF_VERSION} \
        && export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig \
        && export LDFLAGS=-L/usr/local/lib \
        && export CPPFLAGS=-I/usr/local/include/libde265 \
        && mkdir build \
        && cd build \
        && cmake --preset=release .. \
        && make \
        && make install \

imagemagick
-----------

.. code-block:: bash

    IMAGEMAGICK_VERSION="7.1.2-26" \
        && curl -sL -o ImageMagick-${IMAGEMAGICK_VERSION}.7z https://github.com/ImageMagick/ImageMagick/releases/download/${IMAGEMAGICK_VERSION}/ImageMagick-${IMAGEMAGICK_VERSION}.7z \
        && 7z x ImageMagick-${IMAGEMAGICK_VERSION}.7z \
        && cd ImageMagick-${IMAGEMAGICK_VERSION} \
        && export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig \
        && export LDFLAGS=-L/usr/local/lib \
        && export CPPFLAGS=-I/usr/local/include/libheif \
        && ./configure --enable-shared --enable-static=yes --enable-symbol-prefix --with-heic --with-raw --with-gslib \
        && make -j4 \
        && make install \
        && ldconfig
