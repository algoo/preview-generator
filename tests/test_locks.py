import concurrent.futures
import os
import shutil
import tempfile

from preview_generator.manager import PreviewManager
from tests.fixtures.coderunnerbuilder import CodeRunnerPreviewBuilder

# Here, we test for concurrency issues.
# This test is tricky to understand and debug. It is also not theoretically
# 100% reliable.
#
# To debug this test, don't use sys.stdout.write or print: it might fail in
# unexpected ways. It is better to use tricks like:
#
# with open("/tmp/out", 'a') as out: out.write("debug line\n")
# (don't forget to escape the escape character in the string containing the code below)
#
# We use CodeRunnerPreviewBuilder, which runs the code of the file it builds
# a preview for. In this test, we use the following code:

code = """
import sys
import time
with open('{0}', 'w', encoding='utf8') as fifo:
    sys.stdout.write('o')
    sys.stdout.flush()
    fifo.write('ready\\n')
    fifo.flush()
    time.sleep(1)
    sys.stdout.write('k\\n')
"""

# This code opens a named pipe for writing, writes "o" to the preview,
# "ready\n" in the named pipe, sleeps for a small amount of time, hopefully
# forcing the scheduler to pick up another thread to run, and then write
# "k\n" to stdout, which leads to the expected preview: "ok\n"

# In the following function, called twice, we check that the preview is
# correct. In one of the thread (tid = 2), we expect "ready\n" in the named
# pipe mentioned in the last paragraph, before requesting the preview.
# This guarantees that when we request the preview, another one has been
# requested by the other thread (tid = 1).
# A correct version of preview generator will not run the code above twice.
# Otherwise, hopefully, when we request the preview in thread 2, the other
# one is waiting for time.sleep to finish.
# When the preview file is opened a second time for writing with the 'w' file,
# the file is truncated to zero length (see the man page for fopen), removing
# the 'o' character written by the first thread, leading to the wrong content
# for the "first" preview.


def handlepreview(cache_path: str, preview_file_name: str, fifopath: str, tid: int) -> bool:
    manager = PreviewManager(cache_path)
    manager._factory.register_builder(CodeRunnerPreviewBuilder)
    if tid == 2:
        with open(fifopath, "r") as fifo:
            line = fifo.readline()
            assert line == "ready\n"

    with open(manager.get_text_preview(preview_file_name)) as previewfile:
        preview = previewfile.read()
        return preview == "ok\n"


def test_locks() -> None:
    cache_path = tempfile.mkdtemp()

    fifopath = os.path.join(cache_path, "fifo")

    try:
        os.mkfifo(fifopath)

        with tempfile.NamedTemporaryFile(suffix="1.runpy", mode="w", encoding="utf8") as codefile:
            codefile.write(code.format(fifopath))
            codefile.flush()

            with concurrent.futures.ThreadPoolExecutor() as executor:
                f1 = executor.submit(handlepreview, cache_path, codefile.name, fifopath, 1)
                f2 = executor.submit(handlepreview, cache_path, codefile.name, fifopath, 2)

                assert f1.result() is True
                assert f2.result() is True
    finally:
        shutil.rmtree(cache_path)
