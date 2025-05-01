
import logging
import os
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import concurrent.futures
from fake_useragent import UserAgent  
from django.http import JsonResponse
import json


#     return JsonResponse({'status': 'error', 'error': 'Invalid request'})
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("grant_status.log"),
        logging.StreamHandler()  # Also logs to console
    ]
)
logger = logging.getLogger(__name__)

# ----------------------------
# Global Variables
# ----------------------------
session = requests.Session()  # Reuse session for performance

open_keywords = [
    'submit a grant', 'accepting proposals', 'open', 'now open', 'currently open', 
    'applications open', 'accepting applications', 'application window open', 'available', 
    'apply now', 'submissions open', 'call for proposals', 'funding available', 'enrollment open', 
    'opportunity open', 'accepting submissions', 'now accepting applications', 'call open', 
    'rfa open', 'cfp open', 'solicitation open', 'registration open', 'live', 'active', 'ongoing',
    'deadline', 'closing date'
]

# ----------------------------
# Grant Status Checker
# ----------------------------
def check_grant_status(url):
    try:
        # Safe user-agent generation
        try:
            ua = UserAgent()
            user_agent = ua.random
        except Exception:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

        headers = {'User-Agent': user_agent}
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        body_text = soup.get_text().lower()

        for keyword in open_keywords:
            if keyword.lower() in body_text:
                logger.info(f"✅ Keyword matched: '{keyword}' in {url}")
                return 'open'
        logger.info(f"❌ No matching keywords found in {url}")
        return 'closed'

    except Exception as e:
        logger.error(f"❗ Error fetching {url}: {str(e)}")
        return 'error'

# ----------------------------
# Django View for AJAX Handling
# ----------------------------
@csrf_exempt
def check_url_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url')

            if not url:
                return JsonResponse({'status': 'error', 'error': 'No URL provided'})

            status = check_grant_status(url)

            # Store only unique URLs
            websites = load_websites_from_file()
            if url not in websites:
                save_website_to_file(url)

            return JsonResponse({
                'status': status if status in ['open', 'closed'] else 'error',
                'error': None if status in ['open', 'closed'] else 'Failed to retrieve grant status'
            })

        except Exception as e:
            logger.error(f"❗ Error in check_url_ajax: {str(e)}")
            return JsonResponse({'status': 'error', 'error': str(e)})

    return JsonResponse({'status': 'error', 'error': 'Invalid request'})

def load_websites_from_file():
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scraper', 'websites.txt')
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]


def save_website_to_file(url):
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scraper', 'websites.txt')
    with open(file_path, 'a') as file:
        file.write(url + "\n")


def send_email(subject, body, to_email):
    from_email = "attahania193@gmail.com"
    password = "sfki ewxj zjxa eskz"  # Keep this as it is for now

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


def check_all_websites(websites):
    sites_status = [] 
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:  
        results = list(executor.map(check_grant_status, websites))  

    for site, status in zip(websites, results):
        sites_status.append({'url': site, 'status': status})

    return sites_status  


def home(request):
    websites = load_websites_from_file() 
    sites_status = check_all_websites(websites) 

    open_grants = []

    for site_status in sites_status:
        if site_status['status'] == 'OPEN':
            open_grants.append(site_status['url'])

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
            websites = load_websites_from_file()
            if url not in websites:
                save_website_to_file(url)  

        status = check_grant_status(url)
        return render(request, 'home.html', {
            'result': status,
            'url': url,
            'websites': []
        })
    else:
        return render(request, 'home.html')
