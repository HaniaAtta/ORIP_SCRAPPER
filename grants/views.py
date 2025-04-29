
# import os
# import requests
# from bs4 import BeautifulSoup
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# import smtplib
# from django.shortcuts import render
# from django.views.decorators.csrf import csrf_exempt
# import concurrent.futures
# from fake_useragent import UserAgent  
# from django.http import JsonResponse
# import json


# def check_grant_status(url):
#     ua = UserAgent() 
#     headers = {
#         'User-Agent': ua.random 
#     }

#     try:
#         r = requests.get(url, headers=headers, timeout=120)  
#         r.raise_for_status()  
#         soup = BeautifulSoup(r.text, 'html.parser')

       
#         open_keywords = [
#     'submit a grant',
#     'accepting proposals',
#     'open',
#     'now open',
#     'currently open',
#     'applications open',
#     'accepting applications',
#     'application window open',
#     'available',
#     'apply now',
#     'submissions open',
#     'call for proposals',
#     'accepting proposals',
#     'funding available',
#     'enrollment open',
#     'opportunity open',
#     'accepting submissions',
#     'now accepting applications',
#     'call open',
#     'rfa open',
#     'cfp open',
#     'solicitation open',
#     'registration open',
#     'live',
#     'active',
#     'ongoing'
# ]

#         body_text = soup.get_text().lower()

#         for keyword in open_keywords:
#             if keyword in body_text:
#                 return 'OPEN'
#         return 'CLOSED'

#     except requests.exceptions.RequestException as e:
#         return 'ERROR'


# @csrf_exempt
# def check_url_ajax(request):
#     if request.method == 'POST':
#         try:
           
#             data = json.loads(request.body)
#             url = data.get('url')

#             if not url:
#                 return JsonResponse({'status': 'error', 'error': 'No URL provided'})

          
#             status = check_grant_status(url)

          
#             websites = load_websites_from_file()
#             if url not in websites:
#                 save_website_to_file(url)

#             if status == 'OPEN':
#                 return JsonResponse({'status': 'open'})
#             elif status == 'CLOSED':
#                 return JsonResponse({'status': 'closed'})
#             else:
#                 return JsonResponse({'status': 'error', 'error': 'Failed to retrieve grant status'})

#         except Exception as e:
#             return JsonResponse({'status': 'error', 'error': str(e)})

#     return JsonResponse({'status': 'error', 'error': 'Invalid request'})

# def load_websites_from_file():
#     file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scraper', 'websites.txt')
#     if not os.path.exists(file_path):
#         return []
#     with open(file_path, 'r') as file:
#         return [line.strip() for line in file.readlines()]

# def save_website_to_file(url):
#     file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scraper', 'websites.txt')
#     with open(file_path, 'a') as file:
#         file.write(url + "\n")

# def send_email(subject, body, to_email):
#     from_email = "attahania193@gmail.com"
#     password = "sfki ewxj zjxa eskz"  
    
#     msg = MIMEMultipart()
#     msg['From'] = from_email
#     msg['To'] = to_email
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'plain'))

#     try:
#         server = smtplib.SMTP('smtp.gmail.com', 587)
#         server.starttls()
#         server.login(from_email, password)
#         text = msg.as_string()
#         server.sendmail(from_email, to_email, text)
#         server.quit()
#         print(f"Email sent to {to_email}")
#     except Exception as e:
#         print(f"Failed to send email: {e}")

# def check_all_websites(websites):
#     sites_status = [] 
#     with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:  # Limit to 20 concurrent threads
#         results = list(executor.map(check_grant_status, websites))  # Concurrently map check_grant_status to websites

#     for site, status in zip(websites, results):
#         sites_status.append({'url': site, 'status': status})

#     return sites_status  

# def home(request):
#     websites = load_websites_from_file() 
#     sites_status = check_all_websites(websites) 

#     open_grants = []

#     for site_status in sites_status:
#         if site_status['status'] == 'OPEN':
#             open_grants.append(site_status['url'])

#     if open_grants:
#         grant_links = "\n".join(open_grants)
#         email_body = f"The following grants are OPEN:\n\n{grant_links}"
#         send_email("Grant Open Notification", email_body, "attahania193@gmail.com")

#     return render(request, 'home.html', {'websites': sites_status})

# @csrf_exempt
# def check_grant(request):
#     if request.method == 'POST':
#         url = request.POST.get('url')
#         if url:
#             websites = load_websites_from_file()
#             if url not in websites:
#                 save_website_to_file(url)  

#         status = check_grant_status(url)
#         return render(request, 'home.html', {
#             'result': status,
#             'url': url,
#             'websites': []
#         })
#     else:
#         return render(request, 'home.html')

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


def check_grant_status(url):
    ua = UserAgent() 
    headers = {
        'User-Agent': ua.random 
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)  
        r.raise_for_status()  
        soup = BeautifulSoup(r.text, 'html.parser')

        open_keywords = [
            'submit a grant', 'accepting proposals', 'open', 'now open', 'currently open', 
            'applications open', 'accepting applications', 'application window open', 'available', 
            'apply now', 'submissions open', 'call for proposals', 'funding available', 'enrollment open', 
            'opportunity open', 'accepting submissions', 'now accepting applications', 'call open', 
            'rfa open', 'cfp open', 'solicitation open', 'registration open', 'live', 'active', 'ongoing'
        ]

        body_text = soup.get_text().lower()

        for keyword in open_keywords:
            if keyword in body_text:
                return 'OPEN'
        return 'CLOSED'

    except requests.exceptions.RequestException as e:
        return 'ERROR'


@csrf_exempt
def check_url_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url')

            if not url:
                return JsonResponse({'status': 'error', 'error': 'No URL provided'})

            status = check_grant_status(url)

            websites = load_websites_from_file()
            if url not in websites:
                save_website_to_file(url)

            if status == 'OPEN':
                return JsonResponse({'status': 'open'})
            elif status == 'CLOSED':
                return JsonResponse({'status': 'closed'})
            else:
                return JsonResponse({'status': 'error', 'error': 'Failed to retrieve grant status'})

        except Exception as e:
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
