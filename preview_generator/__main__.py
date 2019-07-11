import argparse
import sys

from preview_generator.infos import __version__
from preview_generator.utils import get_subclasses_recursively
from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.manager import PreviewManager
from preview_generator.exception import BuilderDependencyNotFound, ExecutableNotFound
from preview_generator.preview.builder_factory import (
    get_builder_folder_name,
    get_builder_modules,
    import_builder_module,
)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="preview_generator", description="Generates previews of files"
    )
    parser.add_argument("input_files", nargs="*", help="File to preview")
    parser.add_argument("--check-dependencies", action="store_true")
    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )
    args = parser.parse_args()
    if not args.input_files and not args.check_dependencies:
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
            print(
                "Builder {} is missing a dependency: {}".format(
                    builder.__name__, e.__str__()
                )
            )
        except NotImplementedError:
            print(
                "Skipping builder class [{}]: method get_supported_mimetypes "
                "is not implemented".format(builder.__name__)
            )


def main():
    args = parse_args()
    if args.check_dependencies:
        check_dependencies()
    if args.input_files:
        manager = PreviewManager("./")
        for input_file in args.input_files:
            path_to_preview_image = manager.get_jpeg_preview(input_file)
            print(input_file, "→", path_to_preview_image)


main()
