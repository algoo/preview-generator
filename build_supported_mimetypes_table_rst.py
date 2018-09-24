import mimetypes

from preview_generator.manager import PreviewManager
pm = PreviewManager('/tmp/cache')

print('+-{}-+-{}-+'.format(''.ljust(80, '-'), ''.ljust(11, '-')))
print('+ {} + {} +'.format('MIME type'.ljust(80, ' '), 'Extension'.ljust(11, ' ')))
print('+={}=+={}=+'.format(''.ljust(80, '='), ''.ljust(11, '=')))

for builder in pm._factory.builders_classes:
    try:
        builder.get_supported_mimetypes()

        print('| {} |'.format('**{}**'.format(builder.get_label()).ljust(94)))
        print('+-{}-+-{}-+'.format(''.ljust(80, '-'), ''.ljust(11, '-')))

        for mime in builder.get_supported_mimetypes():
            ext = pm.get_file_extensions(mime) or ' - '
            print('| {} | {} |'.format(mime.ljust(80), ext.ljust(11)))
            print('+-{}-+-{}-+'.format(''.ljust(80, '-'), ''.ljust(11, '-')))
    except NotImplementedError:
        pass  # probably abstract class, so ignore it

