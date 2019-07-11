import argparse
import logging
import sys

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import ExecutableNotFound
from preview_generator.infos import __version__
from preview_generator.manager import PreviewManager
from preview_generator.preview.builder_factory import get_builder_folder_name
from preview_generator.preview.builder_factory import get_builder_modules
from preview_generator.preview.builder_factory import import_builder_module
from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.utils import LOGGER_NAME
from preview_generator.utils import get_subclasses_recursively


def parse_args():
    parser = argparse.ArgumentParser(
        prog="preview_generator", description="Generates previews of files"
    )
    parser.add_argument("input_files", nargs="*", help="File to preview")
    parser.add_argument("--check-dependencies", action="store_true")
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args()
    if not args.input_files and not args.check_dependencies and not args.version:
        parser.print_usage(file=sys.stderr)
        exit(1)
    return args


def check_dependencies():
    builder_folder = get_builder_folder_name()
    builder_modules = get_builder_modules(builder_folder)

    for module_name in builder_modules:
        import_builder_module(module_name)

    for builder in get_subclasses_recursively(PreviewBuilder):
        try:
            builder.check_dependencies()
        except (BuilderDependencyNotFound, ExecutableNotFound) as e:
            print("Builder {} is missing a dependency: {}".format(builder.__name__, e.__str__()))
        except NotImplementedError:
            print(
                "Skipping builder class [{}]: method get_supported_mimetypes "
                "is not implemented".format(builder.__name__)
            )


def main():
    args = parse_args()
    logging.getLogger(LOGGER_NAME).setLevel(logging.ERROR)
    if args.check_dependencies:
        check_dependencies()
    if args.version:
        print("preview_generator", __version__)
        for builder in get_subclasses_recursively(PreviewBuilder):
            try:
                if builder.check_dependencies():
                    version = builder.dependencies_versions()
                    if version:
                        print(version)
            except (BuilderDependencyNotFound, ExecutableNotFound, NotImplementedError):
                pass
    if args.input_files:
        manager = PreviewManager("./")
        for input_file in args.input_files:
            path_to_preview_image = manager.get_jpeg_preview(input_file)
            print(input_file, "→", path_to_preview_image)


if __name__ == "__main__":
    main()
