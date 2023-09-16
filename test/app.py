from flask import Flask, render_template, jsonify
from flask_apscheduler import APScheduler
from test import Mail  # The name of your email processing module
import os, random

app = Flask(__name__)
scheduler = APScheduler()

def repository(folder):
    # Create dictionary
    repository = {}
    # Get all folders from repository
    directories = os.listdir(folder)
    # For each folder get number of files
    for directory in directories:
        files = os.listdir(os.path.join(folder, directory))
        repository[directory] = len(files)

    return repository


def run_email_processor():
    mail_instance = Mail()
    num_unseen, num_saved_as_html = mail_instance.search_and_save_emails()
    print(f"{num_unseen} unseen emails found.")
    print(f"{num_saved_as_html} emails saved as HTML.")

def update_brands():
    mail_instance = Mail()
    mail_instance.check_missing_brand()

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/brands")
def brands():
    return render_template("brands.html")

@app.route("/categories")
def categories():
    return render_template("categories.html")

@app.route("/emails")
def emails():
    return render_template("emails.html")

@app.route("/preview")
def preview():
    return render_template("preview.html")

@app.route('/randomFile')
def showStatus():
    # Use the specified template folder for this route
    random_folder = random.choice(os.listdir("templates/mail_repository_test"))
    random_file = random.choice(os.listdir(f"templates/mail_repository_test/{random_folder}"))
    return render_template(f'/mail_repository_test/{random_folder}/{random_file}')

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/status")
def status():
    structure = repository("mail_repository_test")
    return render_template("status.html", repository=structure)


@app.route("/check_status")
def check_status():
    # Add any status checking you want here
    return jsonify({"status": "running"})


if __name__ == "__main__":
    scheduler.add_job(id="email_processor", func=run_email_processor, trigger="cron", day_of_week="mon-sun", hour=11, minute=25, second=10)  # Run email processor every 30 minutes

    scheduler.start()
    # update_brands()
    app.run(debug=True, use_reloader=False)  # Set debug to False for production use