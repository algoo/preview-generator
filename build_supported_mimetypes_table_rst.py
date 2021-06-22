import pytablewriter

from preview_generator.manager import PreviewManager

pm = PreviewManager("/tmp/cache")

writer = pytablewriter.RstGridTableWriter()
writer.table_name = "Supported mimetypes table"
writer.headers = ["MIME type/Builder Name", "Extension/Weight"]
matrix = []


for builder in pm._factory.builders_classes:
    try:
        mimetypes = builder.get_supported_mimetypes()
        if not mimetypes:
            continue
        matrix.append(["**{}**".format(builder.get_label()), builder.weight])
        for mimetype in mimetypes:
            extensions = ", ".join(pm.get_file_extensions(mimetype)) or " - "
            matrix.append([mimetype, extensions])
    except NotImplementedError:
        pass  # probably abstract class, so ignore it

writer.value_matrix = matrix
writer.write_table()
