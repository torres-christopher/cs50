import pdfcrowd
import sys

try:
    # create the API client instance
    client = pdfcrowd.HtmlToImageClient('demo', 'ce544b6ea52a5621fb9d55f8b542d14d')

    # configure the conversion
    client.setOutputFormat('png')

    # run the conversion and write the result to a file
    client.convertFileToFile('/workspaces/73254689/_project/smtp/test/mail_repository_test/Váš_Astratex/f6a2d8f92e7723bfe692d66b3ac5e0af.html', 'MyLayout.png')

except pdfcrowd.Error as why:
    sys.stderr.write('Pdfcrowd Error: {}\n'.format(why))
    raise