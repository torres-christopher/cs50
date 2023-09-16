import email
import imaplib

EMAIL = 'christopher.torres.crm@gmail.com'
PASSWORD = 'cyoepteidpazxomg' # Change password
SERVER = 'imap.gmail.com'

# Encrypted connect to the server and go to its inbox - Usually 993 port
mail = imaplib.IMAP4_SSL(SERVER)
mail.login(EMAIL, PASSWORD)
# Select which inbox to get e-mails from
mail.select('inbox')


# Search for ALL messages with None charset parameter. Returns Status and ID of message
status, data = mail.search(None, 'UNSEEN')

print(data)

# the list returned is a list of bytes separated by white spaces on this format: [b'1 2 3', b'4 5 6'] so, to separate it first we create an empty list
mail_ids = []

# then we go through the list splitting its blocks of bytes and appending to the mail_ids list
for block in data:
    # the split function called without parameter transforms the text or bytes into a list using the white spaces as separator:
    # b'1 2 3'.split() => [b'1', b'2', b'3']
    mail_ids += block.split()

# now for every id we'll fetch the email to extract its content
for i in mail_ids:
    # the fetch function fetch the email given its id and format that you want the message to be
    status, data = mail.fetch(i, '(RFC822)')

    # Data se per RFC822 format comes on a list with a tuple with header, content, and the closing byte b')'
    for response_part in data:
        # Tuple check
        if isinstance(response_part, tuple):
            # we go for the content at its second element skipping the header at the first and the closing at the third
            message = email.message_from_bytes(response_part[1])

            # Get from and subject of message
            mail_from = message['from']
            mail_subject = message['subject']

            # Check for plain text vs multipart (needs to be separated)
            if message.is_multipart():
                mail_content = ''
                mail_html = ''

                # Multipart has text, annex and HTML
                for part in message.get_payload():
                    # Extract plain text
                    mType = part.get_content_type()
                    print(mType)
                    if part.get_content_type() == 'text/plain':
                        mail_content += part.get_payload()
                    elif part.get_content_type() == 'text/html':
                        mail_html += part.get_payload()
                        file_html = open("test.html", "w")
                        file_html.write(mail_html)
                        file_html.close()

            else:
                # Plain text version
                mail_content = message.get_payload()

            # and then let's show its result
            print(f'From: {mail_from}')
            print(f'From: {mail_html}')
mail.close()