# -*- coding: utf-8 -*-

import json
from shutil import which
from subprocess import check_output
import typing

from preview_generator import utils
from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import PreviewGeneratorException
from preview_generator.preview.generic_preview import PreviewBuilder

ffmpeg_installed = True
try:
    import ffmpeg
except ImportError:
    ffmpeg_installed = False


class NoVideoStream(PreviewGeneratorException):
    pass


class VideoPreviewBuilderFFMPEG(PreviewBuilder):
    page_nb = 10

    @classmethod
    def get_label(cls) -> str:
        return "Video files - based on ffmpeg"

    @classmethod
    def check_dependencies(cls) -> None:
        if not ffmpeg_installed:
            raise BuilderDependencyNotFound("this builder requires ffmpeg to be available")

    @classmethod
    def dependencies_versions(cls) -> typing.Optional[str]:
        return "{} from {}".format(
            check_output(["ffmpeg", "-version"], universal_newlines=True).strip().split("\n")[0],
            which("ffmpeg"),
        )

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return [
            "application/x-videolan",
            "video/3gpp",
            "video/annodex",
            "video/dl",
            "video/dv",
            "video/fli",
            "video/gl",
            "video/mpeg",
            "video/mp2t",
            "video/mp4",
            "video/quicktime",
            "video/mp4v-es",
            "video/ogg",
            "video/parityfec",
            "video/pointer",
            "video/webm",
            "video/vnd.fvt",
            "video/vnd.motorola.video",
            "video/vnd.motorola.videop",
            "video/vnd.mpegurl",
            "video/vnd.mts",
            "video/vnd.nokia.interleaved-multimedia",
            "video/vnd.vivo",
            "video/x-flv",
            "video/x-la-asf",
            "video/x-mng",
            "video/x-ms-asf",
            "video/x-ms-wm",
            "video/x-ms-wmv",
            "video/x-ms-wmx",
            "video/x-ms-wvx",
            "video/x-msvideo",
            "video/x-sgi-movie",
            "video/x-matroska",
            "video/x-theora+ogg",
            "video/x-m4v",
        ]

    def get_dims_from_ffmpeg_probe(
        self, probe_result: typing.Dict[str, typing.Any]
    ) -> utils.ImgDims:
        """
        Extract the width and height of the video stream from probe dict and return it
        """
        video_stream_data = {}  # type:typing.Dict[str,typing.Any]
        for stream_data in probe_result["streams"]:
            if stream_data["codec_type"] == "video":
                video_stream_data = stream_data

        if not video_stream_data:
            raise NoVideoStream

        return utils.ImgDims(width=video_stream_data["width"], height=video_stream_data["height"])

    def _get_frame_time(self, page_id: int, page_nb: int, video_duration: float) -> float:
        """
        Compute time of frame #page_id
        The algorithm is:
        - first frame is at 2%
        - last frame is at 98%
        - time is plitted between 2% and 98% according to the number of requested frames
        - if 1 frame only, then return 2%

        :param page_id: id of the page, value must be between 0 and page_nb-1. If -1, return the first frame
        :param page_nb: total number of frames
        :param video_duration: duration of the full video (float)
        :return: the time of the requested frame
        """
        if page_nb > 1:
            # 100 - 4 is:
            # - we take first frame at 2% of full duration
            # - we take last frame at 2% of end of movie
            # - we split the 96% remaining for all frames
            delta_between_two_frames_in_percent = (100 - 4) / (page_nb - 1)
        else:
            delta_between_two_frames_in_percent = 0

        return video_duration * (2 + delta_between_two_frames_in_percent * page_id) / 100

    def _get_extraction_size(
        self, video_dims: utils.ImgDims, preview_dims: utils.ImgDims
    ) -> utils.ImgDims:
        """
        Compute extraction dimensions.

        The extract size in order to directly get the right height or width according
        to what is expected for preview

        :param video_dims: ImgDims object representing width and height of the video stream
        :param preview_dims: ImgDims object representing width and height of the preview to generate
        :return: ImgDims to use for ffmpeg video frame extraction
        """
        extract_size = utils.ImgDims(-1, -1)
        if video_dims.ratio() > preview_dims.ratio():
            extract_size.width = preview_dims.width
        else:
            extract_size.height = preview_dims.height

        return extract_size

    def build_jpeg_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        page_id: int,
        extension: str = ".jpg",
        size: utils.ImgDims = None,
        mimetype: str = "",
    ) -> None:
        """
        generate the jpeg preview
        """
        if not size:
            size = self.default_size

        preview_path = "{path}{file_name}{extension}".format(
            file_name=preview_name, path=cache_path, extension=extension
        )

        video_probe_data = ffmpeg.probe(file_path)
        video_size = self.get_dims_from_ffmpeg_probe(video_probe_data)
        extraction_size = self._get_extraction_size(video_size, size)

        video_duration = float(video_probe_data["format"]["duration"])
        page_nb = self.get_page_number(file_path, preview_name, cache_path)
        frame_time = self._get_frame_time(page_id, page_nb, video_duration)

        (
            ffmpeg.input(file_path, ss=frame_time)
            .filter("scale", extraction_size.width, extraction_size.height)
            .output(preview_path, vframes=1)
            # INFO - G.M - 2020-07-03 we do allow overwrite to allow forcing the refresh of
            # the preview.
            .overwrite_output()
            .run()
        )

    def build_json_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        page_id: int = 0,
        extension: str = ".json",
    ) -> None:
        """
        generate the json preview. Default implementation is based on ExifTool
        """
        metadata = ffmpeg.probe(file_path)

        with open(cache_path + preview_name + extension, "w") as jsonfile:
            json.dump(metadata, jsonfile)

    def set_page_nb(self, page_nb: int) -> int:
        """
        Allow to override default page_nb (10 by default)
        """
        self.page_nb = page_nb
        return self.page_nb

    def get_page_number(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        mimetype: typing.Optional[str] = None,
    ) -> int:
        return self.page_nb

    def has_jpeg_preview(self) -> bool:
        return True
