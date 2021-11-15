# This image should be built from the root of tracim repository, e.g.:
# docker build -f containers/concourse/Dockerfile -t algooci/preview-generator:latest .
FROM debian:bullseye AS base_install

# HOME, used by pyenv scripts
ENV HOME=/root
# Tracim needs UTF-8 to properly work
ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8
ENV LC_ALL C.UTF-8

COPY . preview_generator
WORKDIR /preview_generator
RUN ./concourse/scripts/install_os_packages && \
    # needed to install different python versions \
    ./concourse/scripts/install_pyenv

FROM base_install AS main
    # tested python versions
RUN ./concourse/scripts/install_python_packages 3.6.14 3.7.11 3.8.11 3.9.6
