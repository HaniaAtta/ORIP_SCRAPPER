
import os
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
import json

def check_grant_status(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    try:
        
        r = requests.get(url, headers=headers)
        r.raise_for_status()  

       
        soup = BeautifulSoup(r.text, 'html.parser')

       #KEYWORDS
        open_keywords = ['submit a grant', 'accepting proposals']

     
        body_text = soup.get_text().lower()

        
        for keyword in open_keywords:
            if keyword in body_text:
                return 'OPEN'
        
        return 'CLOSED'

    except requests.exceptions.RequestException:
        return 'ERROR'

@csrf_exempt
def check_url_ajax(request):
    if request.method == 'POST':
        try:
            # Get URL from the request body
            data = json.loads(request.body)
            url = data.get('url')

            if not url:
                return JsonResponse({'status': 'error', 'error': 'No URL provided'})

            # Check the grant status
            status = check_grant_status(url)

            # Save the URL to the websites.txt file if not already present
            websites = load_websites_from_file()
            if url not in websites:
                save_website_to_file(url)

            # Respond with the status of the grant
            if status == 'OPEN':
                return JsonResponse({'status': 'open'})
            elif status == 'CLOSED':
                return JsonResponse({'status': 'closed'})
            else:
                return JsonResponse({'status': 'error', 'error': 'Failed to retrieve grant status'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)})

    return JsonResponse({'status': 'error', 'error': 'Invalid request'})


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

def check_grant_status(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')

        open_keywords = ['submit a grant', 'accepting proposals']
        body_text = soup.get_text().lower()

        for keyword in open_keywords:
            if keyword in body_text:
                return 'OPEN'
        return 'CLOSED'

    except requests.exceptions.RequestException as e:
        return 'ERROR'


def load_websites_from_file():
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scraper', 'websites.txt')
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def save_website_to_file(url):
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scraper', 'websites.txt')
    with open(file_path, 'a') as file:
        file.write(url + "\n")

def home(request):
    websites = load_websites_from_file()
    sites_status = []

    open_grants = []

    for site in websites:
        status = check_grant_status(site)
        sites_status.append({'url': site, 'status': status})
        if status == 'OPEN':
            open_grants.append(site)

    if open_grants:
        grant_links = "\n".join(open_grants)
        email_body = f"The following grants are OPEN:\n\n{grant_links}"
        send_email("Grant Open Notification", email_body, "attahania193@gmail.com")

    return render(request, 'home.html', {'websites': sites_status})

@csrf_exempt
def check_grant(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if url:
            # Check if the URL is already in the file before adding it
            websites = load_websites_from_file()
            if url not in websites:
                save_website_to_file(url)  # Save the new website URL to the file

        status = check_grant_status(url)
        return render(request, 'home.html', {
            'result': status,
            'url': url,
            'websites': []
        })
    else:
        return render(request, 'home.html')


