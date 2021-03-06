import socket
import struct
from datetime import datetime

import os
from bs4 import BeautifulSoup
from html2text import html2text
from os.path import expanduser
from subprocess import call, DEVNULL

html_mime = 'text/html'
plain_mime = 'text/plain'

correct_mime = [html_mime, plain_mime]
correct_extensions = ['html', 'html', 'txt']

excluded_ips = [
    [167772160, 184549375],
    [2130706432, 2147483647],
    [2886729728, 2887778303],
    [3232235520, 3232301055],
]

SUCCESS = '\033[92m'
WARNING = '\033[93m'
NORMAL = '\033[0m'


def execute(command):
    return call(command, stderr=DEVNULL, stdout=DEVNULL, shell=True)


def is_mime_correct(content_type):
    mime_type = content_type.split(';')[0]
    if not (mime_type in correct_mime):
        return False
    return True


def has_correct_extension(url):
    supposed_extension = url.split('.')[-1]
    if len(supposed_extension) > 4:
        return True
    if supposed_extension in correct_extensions:
        return True
    return False


def get_onion_domain(url):
    try:
        if url.split('/')[2][-6:] != '.onion':
            return None
        return '/'.join(url.split('/')[:3])
    except IndexError:
        return None


def get_urls(current_url, content, content_type):
    if not is_mime_correct(content_type):
        return None
    mime_type = content_type.split(';')[0]

    # Different processing for different MIME types
    urls = []
    if mime_type == html_mime:
        try:
            soup = BeautifulSoup(content, features="html.parser")
            for a_href in soup.findAll('a', href=True):
                urls.append(a_href['href'])
        except UnicodeEncodeError:
            print('Invalid HTML/TEXT file')
    else:
        words = content.replace('\n', ' ').split()
        for word in words:
            if word[:4] == 'http':
                urls.append(word)

    # Final validation
    results = []
    for url in urls:
        # url = url.split('#')[0]
        if url[0] == '/':
            url = get_onion_domain(current_url) + url
        if get_onion_domain(url) and has_correct_extension(url):
            results.append(url)
    return results


def get_title(content):
    return BeautifulSoup(content, features="html.parser").title.string


def get_plain(content):
    soup = BeautifulSoup(content, features="html.parser")
    body = soup.find('body')
    return html2text(body.text).replace('\n', ' ')


def get_words(plain):
    lower_text = plain.lower()
    line = ''
    for c in lower_text:
        if c.isalnum() or c.isspace():
            line += c
    all_words = list(set(line.split()))

    words = []
    for word in all_words:
        if 0 < len(word) < 16:
            words.append(word)
    return words


def get_sentences(plain):
    sep_split = plain.split()

    sentences = []
    current_sentence = ''

    for s in sep_split:
        if (len(s) + len(current_sentence)) < 150:
            current_sentence += ' ' + s
        else:
            sentences.append(current_sentence)
            current_sentence = s
    return sentences


def int_to_ip(no):
    return socket.inet_ntoa(struct.pack("!I", no))


def get_default_path():
    slash = ['/', '\\'][os.name == 'nt']

    return expanduser("~") + slash + datetime.now().strftime("%Y-%m-%d %H_%M_%S") + '.db'


def is_ip_permitted(ip_int):
    return not any(
        [
            ip_range[0] <= ip_int <= ip_range[1]
            for ip_range in excluded_ips
        ]
    )
