****************************
Building ImageMagick for HEIC support
****************************


libde265
--------

.. code-block:: bash

    LIBDE265_VERSION="1.0.5" \
        && curl -L https://github.com/strukturag/libde265/releases/download/v${LIBDE265_VERSION}/libde265-${LIBDE265_VERSION}.tar.gz | tar zx \
        && cd libde265-${LIBDE265_VERSION} \
        && ./autogen.sh \
        && ./configure \
        && make -j4 \
        && make install


libheif
--------

.. code-block:: bash

    LIBHEIF_VERSION="1.6.1" \
        && curl -L https://github.com/strukturag/libheif/releases/download/v${LIBHEIF_VERSION}/libheif-${LIBHEIF_VERSION}.tar.gz | tar zx \
        && cd libheif-${LIBHEIF_VERSION} \
        && export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig \
        && export LDFLAGS=-L/usr/local/lib \
        && export CPPFLAGS=-I/usr/local/include/libde265 \
        && ./autogen.sh \
        && ./configure \
        && make -j4 \
        && make install

imagemagick
--------

.. code-block:: bash

    IMAGEMAGICK_VERSION="7.0.9-19" \
        && curl -L https://imagemagick.org/download/ImageMagick-${IMAGEMAGICK_VERSION}.tar.gz | tar zx \
        && cd ImageMagick-${IMAGEMAGICK_VERSION} \
        && export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig \
        && export LDFLAGS=-L/usr/local/lib \
        && export CPPFLAGS=-I/usr/local/include/libheif \
        && ./configure --enable-shared --enable-static=yes --enable-symbol-prefix --with-heic --with-raw --with-gslib \
        && make -j4 \
        && make install \
        && ldconfig
