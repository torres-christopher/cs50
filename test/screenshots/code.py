import requests
import json

instructions = {
  'parts': [
    {
      'html': 'document'
    }
  ],
  'output': {
    'type': 'image',
    'format': 'jpg',
    'dpi': 500
  }
}

response = requests.request(
  'POST',
  'https://api.pspdfkit.com/build',
  headers = {
    'Authorization': 'Bearer pdf_live_aBSfNxw2rVJNhU7yN2byIYrs8wFuDSYZ8KyuOH3oEDK'
  },
  files = {
    'document': open('/workspaces/73254689/_project/smtp/test/mail_repository_test/Váš_Astratex/f6a2d8f92e7723bfe692d66b3ac5e0af.html', 'rb')
  },
  data = {
    'instructions': json.dumps(instructions)
  },
  stream = True
)

if response.ok:
  with open('image.jpg', 'wb') as fd:
    for chunk in response.iter_content(chunk_size=8096):
      fd.write(chunk)
else:
  print(response.text)
  exit()
