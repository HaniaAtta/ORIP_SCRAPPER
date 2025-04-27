
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(subject, body, to_email):
    from_email = "attahania193@gmail.com"
    password = "sfki ewxj zjxa eskz"
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_grant_status(url, open_grants):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        open_keywords = [
           'submit a grant','Accepting Proposals'
        ]

        body_text = soup.get_text().lower()

        for keyword in open_keywords:
            if keyword in body_text:
                print(f"Grant is OPEN on {url}")
                open_grants.append(url)
                return True

        print(f"Grant is CLOSED on {url}")
        return False

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return False


def load_websites_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

if __name__ == '__main__':
    websites = load_websites_from_file('websites.txt')

    to_email = "attahania193@gmail.com"
    open_grants = []

    for website in websites:
        check_grant_status(website, open_grants)

    if open_grants:
        grant_links = "\n".join(open_grants)
        email_body = f"The following grants are OPEN:\n\n{grant_links}"
        send_email("Grant Open Notification", email_body, to_email)
    else:
        print("No open grants found.")
