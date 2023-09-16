import email    # Email data
import email.header
import imaplib  # IMAP email download
import os       # Work with files
import hashlib  # Hash file names
import sqlite3  # Database
from dotenv import load_dotenv # Hash login details
import random # Random for testing

# Load environment variables from .env file
load_dotenv()

# Retrieve the values from environment variables
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
SERVER = os.getenv('SERVER')


class Mail():
    # Initialize class
    def __init__(self):
        # Encrypted connect to the server and go to its inbox - Usually 993 port
        self.user = EMAIL
        self.password = PASSWORD
        self.M = imaplib.IMAP4_SSL(SERVER, '993')
        self.M.login(self.user, self.password)
        # Select which inbox to get e-mails from
        self.M.select('inbox')

    # Decode encoded emails UTF-8
    def header_decode(self, header):
        hdr = ""
        for text, encoding in email.header.decode_header(header):
            if isinstance(text, bytes):
                text = text.decode(encoding or "us-ascii")
            hdr += text
        return hdr

    # Processes email messages and returns sender, subject, date and HTML code
    def process_email(self, message):
        mail_from = message['from']
        mail_subject = message['subject']
        mail_date = message['date']

        # Clean sender email address
        if '"' in mail_from or "'" in mail_from:
            mail_from = mail_from.replace('"', '').replace("'", "")

        # Split on start of email address
        sender = mail_from.split('<')

        if len(sender) > 1:
            # Strip trailing whitespaces
            mail_from_name = sender[0].strip().replace('.cz', '').replace('www.', '')
            mail_from_address = sender[1].replace('>', '').strip()
        else:
            # Strip trailing whitespaces
            mail_from_address = sender[0].replace('>', '').strip()
            mail_from_name = sender[0].strip().replace('.cz', '').replace('www.', '')
            mail_from_name = mail_from_name.split('@')[1].rsplit(',', 1)[0]

        if "utf" in mail_from_name or "UTF" in mail_from_name:
            mail_from_name = self.header_decode(mail_from_name)

        if "utf" in mail_subject or "UTF" in mail_subject:
            mail_subject = self.header_decode(mail_subject)

        # Clean data for folder structure
        mail_from_name = mail_from_name.replace('/', '').replace(':', '').replace('*', '').replace('|', '').replace('\\', '').replace('?', '')

        mail_html = ''
        # Check for plain text vs multipart (needs to be separated)
        if message.is_multipart():
            # Multipart has text, annex, and HTML
            for part in message.get_payload():
                # Extract HTML code
                if part.get_content_type() == 'text/html':
                    payload = part.get_payload(decode=True)
                    try:
                        # Attempt to decode the payload as UTF-8
                        payload = payload.decode('utf-8')
                    except UnicodeDecodeError:
                        # If decoding as UTF-8 fails, fallback to 'latin1'
                        payload = payload.decode('latin1')
                    mail_html += payload
        else:
            if message.get_content_type() == 'text/html':
                payload = message.get_payload(decode=True)
                try:
                    # Attempt to decode the payload as UTF-8
                    payload = payload.decode('utf-8')
                except UnicodeDecodeError:
                    # If decoding as UTF-8 fails, fallback to 'latin1'
                    payload = payload.decode('latin1')
                mail_html += payload

        return mail_from_name, mail_from_address, mail_subject, mail_date, mail_html

    # Cleans HTML of personal information
    def clean_html(self, html_code):
        clean_code = html_code.replace("christopher.torres.crm@gmail.com", "#####@gmail.com")

        return clean_code

    # Create hash name for files
    def get_hash(self, subject):
        hash_md5 = hashlib.md5(subject.encode('utf-8')).hexdigest()
        return hash_md5

    # Get new or existing directory to save files
    def create_directory(self, sender):
        directory_path = "mail_repository_test"
        sender = sender.replace(" ","_")
        # Check if the general mail repository exists
        if os.path.exists(directory_path):
            # Create the expected path of the repository
            directory_path = os.path.join(directory_path, sender)

            # Create if not exists
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

        return directory_path

    # Saves html file to directory and returns full path
    def save_as_html(self, directory_path, content_hash, html_code):
        file_name = f"{content_hash}.html"
        file_path = os.path.join(directory_path, file_name)

        # Check for duplicates
        counter = 1
        while os.path.exists(file_path):
            unique_name = f"{content_hash}_{counter}.html"
            file_path = os.path.join(directory_path, unique_name)
            counter += 1

        # Create a new file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(html_code)

        # Return its path
        print(file_path)
        return file_path

    # Saves data about email into a database
    def save_metadata(self, mail_from_name, mail_from_address, mail_subject, mail_date, file_path):
        # Call a connection to the database
        con = sqlite3.connect("emails_test.db")

        # Connect cursor for SQL queries execution
        cur = con.cursor()

        # Check for a familiar sender
        cur.execute("SELECT sender_id FROM senders WHERE sender_name = ?", (mail_from_name,))
        sender_tup = cur.fetchone()

        # Insert a new sender into the table
        if sender_tup is None:
            cur.execute("""
                INSERT INTO senders (sender_name, sender_address) VALUES (?, ?)
            """, (mail_from_name, mail_from_address))
            con.commit()
            cur.execute("SELECT sender_id FROM senders WHERE sender_name = ?", (mail_from_name,))
            sender_tup = cur.fetchone()
            sender_id = sender_tup[0]
        # Get the sender ID
        elif len(sender_tup) > 1:
            raise ValueError("Senders are duplicated")
        else:
            sender_id = sender_tup[0]

        # Insert data into the database
        cur.execute("""
            INSERT INTO emails (subject, date, file_path, sender_id) VALUES (?, ?, ?, ?)
        """, (mail_subject, mail_date, file_path, sender_id))
        con.commit()

        # Close connection
        con.close()

    # Saves information about unsaved emails to database
    def save_unsaved(self, mail_from_name, mail_from_address, mail_subject, mail_date):
        # Check default values
        if not mail_from_name:
            mail_from_name = "Empty"
        if not mail_from_address:
            mail_from_address = "Empty"
        if not mail_subject:
            mail_subject = "Empty"
        if not mail_date:
            mail_date = "Empty"

        # Call a connection to the database
        con = sqlite3.connect("emails_test.db")

        # Connect cursor for SQL queries execution
        cur = con.cursor()

        # Check for a familiar sender
        cur.execute("SELECT sender_id FROM senders WHERE sender_name = ?", (mail_from_name,))
        sender_tup = cur.fetchone()

        # Insert a new sender into the table
        if sender_tup is None:
            cur.execute("""
                INSERT INTO senders (sender_name, sender_address) VALUES (?, ?)
            """, (mail_from_name, mail_from_address))
            con.commit()
            cur.execute("SELECT sender_id FROM senders WHERE sender_name = ?", (mail_from_name,))
            sender_tup = cur.fetchone()
            sender_id = sender_tup[0]
        # Get the sender ID
        elif len(sender_tup) > 1:
            raise ValueError("Senders are duplicated")
        else:
            sender_id = sender_tup[0]

        # Insert data into the database
        cur.execute("""
            INSERT INTO unsaved (subject, date, sender_id) VALUES (?, ?, ?)
        """, (mail_subject, mail_date, sender_id))
        con.commit()

        # Close connection
        con.close()

    # Connects senders to brands in database
    def check_missing_brand(self):
        # Call a connection to the database
        con = sqlite3.connect("emails_test.db")

        # Connect cursor for SQL queries execution
        cur = con.cursor()

        # Check for empty brands in emails
        cur.execute("SELECT email_id, sender_id FROM emails WHERE brand_id IS NULL")
        sender_tup = cur.fetchall()

        for email_id, sender_id in sender_tup:
            # Check for brand in sender_brands
            cur.execute("SELECT brand_id FROM senders_brands WHERE sender_id = ?", (sender_id,))
            result = cur.fetchone()

            if result:
                brand_id = result[0]
                # Update the emails table with the correct brand_id
                cur.execute("UPDATE emails SET brand_id = ? WHERE email_id = ?", (brand_id, email_id))
                con.commit()

        # Check for empty brands in unsaved
        cur.execute("SELECT email_id, sender_id FROM unsaved WHERE brand_id IS NULL")
        sender_tup = cur.fetchall()

        for email_id, sender_id in sender_tup:
            # Check for brand in sender_brands
            cur.execute("SELECT brand_id FROM senders_brands WHERE sender_id = ?", (sender_id,))
            result = cur.fetchone()

            if result:
                brand_id = result[0]
                # Update the emails table with the correct brand_id
                cur.execute("UPDATE unsaved SET brand_id = ? WHERE email_id = ?", (brand_id, email_id))
                con.commit()


        # Close connection
        con.close()

    """
    # Takes screenshots of html emails and saves them to the same folder as emails
    def take_screenshot(self, url, screenshot_path):
        # Set up Firefox options
        firefox_options = Options()
        firefox_options.headless = True  # Run Firefox in headless mode

        # Initialize the Firefox WebDriver
        driver = webdriver.Firefox(executable_path='geckodriver', options=firefox_options)

        driver.get(url)
        driver.save_screenshot(screenshot_path)

        driver.quit()
    """

    # Main function
    def search_and_save_emails(self):
        with self.M as inbox:
            # Search for ALL messages with None charset parameter. Returns Status and ID of message
            status, data = inbox.search(None, 'UNSEEN')

            # Get the number of unseen emails if any
            num_unseen_emails = len(data[0].split()) if data[0] else 0

            # the list returned is a list of bytes separated by white spaces on this format: [b'1 2 3', b'4 5 6'] so, to separate it first we create an empty list
            mail_ids = []

            # then we go through the list splitting its blocks of bytes and appending to the mail_ids list
            for block in data:
                # the split function called without parameter transforms the text or bytes into a list using the white spaces as separator:
                # b'1 2 3'.split() => [b'1', b'2', b'3']
                mail_ids += block.split()

            num_saved_as_html = 0  # Initialize the count of emails saved as HTML

            # now for every id we'll fetch the email to extract its content
            for i in mail_ids:
                # the fetch function fetch the email given its id and format that you want the message to be
                status, data = inbox.fetch(i, '(RFC822)')
                # Check for unsaved e-mails
                saved = False

                # Data se per RFC822 format comes on a list with a tuple with header, content, and the closing byte b')'
                for response_part in data:
                    # Tuple check
                    if isinstance(response_part, tuple):
                        # we go for the content at its second element skipping the header at the first and the closing at the third
                        message = email.message_from_bytes(response_part[1])

                        # Get data from message
                        mail_from_name, mail_from_address, mail_subject, mail_date, mail_html = self.process_email(message)

                        # Skip if no HTML file detected
                        if not mail_html:
                            continue

                        # Clean html of contact info
                        mail_html = self.clean_html(mail_html)

                        # Create file name
                        content_hash = self.get_hash(mail_subject)

                        # Check file directory or create a new one
                        directory_path = self.create_directory(mail_from_name)

                        # Save email as HTML
                        file_path = self.save_as_html(directory_path, content_hash, mail_html)

                        """
                        # Take a screenshot of the email's HTML content
                        screenshot_path = os.path.join(directory_path, f"{content_hash}.png")
                        self.take_screenshot(f"file://{file_path}", screenshot_path)
                        """

                        # Save email metadata to the database
                        self.save_metadata(mail_from_name, mail_from_address, mail_subject, mail_date, file_path)

                        # Increment the count of emails saved as HTML
                        num_saved_as_html += 1
                        saved = True
                if saved == False:
                    self.save_unsaved(mail_from_name, mail_from_address, mail_subject, mail_date)

            return num_unseen_emails, num_saved_as_html


if __name__ == "__main__":
    """
    print("------------------")
    mail_instance = Mail()
    # path = mail_instance.save_as_html("mail_repository_test/Isobar (MASTER)", "32fca84e687740feb720ca7657c70cf8", "<html></html>")
    num_unseen, num_saved_as_html = mail_instance.search_and_save_emails()
    print(f"{num_unseen} unseen emails found.")
    print(f"{num_saved_as_html} emails saved as HTML.")
    """

    random_folder = random.choice(os.listdir("templates/mail_repository_test"))
    random_file = random.choice(os.listdir(f"templates/mail_repository_test/{random_folder}"))
    print(random_folder)
    print(random_file)