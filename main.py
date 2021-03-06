# -*- coding: utf-8 -*-

import socket
import ssl
import datetime
import requests
import sys
from config import DOMAINS, CODEXBOT_NOTIFICATIONS, DAYS_LIMIT


date_fmt = r'%b %d %H:%M:%S %Y %Z'

# tg
def send_message(text):
    requests.post(CODEXBOT_NOTIFICATIONS, data={'message': text})

'''
Source link: https://serverlesscode.com/post/ssl-expiration-alerts-with-lambda/
'''
def ssl_expiry_datetime(hostname):
    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=hostname,
    )

    # 3 second timeout because Lambda has runtime limitations
    conn.settimeout(3.0)

    conn.connect((hostname, 443))
    ssl_info = conn.getpeercert()

    # Parse the string from the certificate into a Python datetime object
    return datetime.datetime.strptime(ssl_info['notAfter'], date_fmt)

def check_ssl_time_left(domain):
    cert_expire_at = ssl_expiry_datetime(domain)
    time_left = cert_expire_at - datetime.datetime.now()
    message = 'SSL cert for {} has {}'.format(domain, days_left_to_format_string(time_left))
    if time_left.days <= DAYS_LIMIT:
        message = '{}'.format(message)
        send_message(message)
    print(message)

def days_left_to_format_string(timedelta):
    return '{} day{} left'.format(timedelta.days,  ('s', '')[timedelta.days == 1])

if not CODEXBOT_NOTIFICATIONS:
    print('No CODEXBOT_NOTIFICATIONS link was found in config file.')
    exit()

for domain in DOMAINS:
    try:
        check_ssl_time_left(domain)
    except:
        print("Unexpected error:", sys.exc_info()[0])
