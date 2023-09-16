# pip3 install requests
import requests
import codecs

f=codecs.open("/workspaces/73254689/_project/smtp/test/mail_repository_test/Váš_Astratex/f6a2d8f92e7723bfe692d66b3ac5e0af.html", 'r')
HCTI_API_ENDPOINT = "https://hcti.io/v1/image?width=600"
# Retrieve these from https://htmlcsstoimage.com/dashboard
HCTI_API_USER_ID = '3f50b9a4-f9b9-4dbd-9d9c-986738eb4578'
HCTI_API_KEY = '636ffba5-2588-4ef2-9079-43773676ae38'

data = { 'html': f.read() }

image = requests.post(url = HCTI_API_ENDPOINT, data = data, auth=(HCTI_API_USER_ID, HCTI_API_KEY))

print("Your image URL is: %s"%image.json()['url'])
# https://hcti.io/v1/image/7ed741b8-f012-431e-8282-7eedb9910b32