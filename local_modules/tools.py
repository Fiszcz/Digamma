# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
from html2text import html2text
from os.path import expanduser

html_mime = 'text/html'
plain_mime = 'text/plain'

correct_mime = [html_mime, plain_mime]
correct_extensions = ['html', 'html', 'txt']


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


def is_onion_domain(url):
    try:
        if url.split('/')[2][-6:] != '.onion':
            return False
        return True
    except IndexError:
        return False


def get_urls(content, content_type):
    if not is_mime_correct(content_type):
        return None
    mime_type = content_type.split(';')[0]

    # Different processing for different MIME types
    urls = []
    if mime_type == html_mime:
        try:
            soup = BeautifulSoup(content)
            for a_href in soup.findAll('a', href=True):
                urls.append(a_href['href'])
        except UnicodeEncodeError:
            print 'Invalid HTML/TEXT file'
    else:
        words = content.replace('\n', ' ').split()
        for word in words:
            if word[:4] == 'http':
                urls.append(word)

    # Final validation
    results = []
    for url in urls:
        url = url.split('#')[0]
        if is_onion_domain(url) and has_correct_extension(url):
            results.append(url)
    return results


def get_title(content):
    return BeautifulSoup(content).title.string


def get_plain(content):
    soup = BeautifulSoup(content)
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


def ip_to_no(ip):
    i = map(int, ip.split('.'))
    return i[0] * (2 ** 24) + i[1] * (2 ** 16) + i[2] * (2 ** 8) + i[3]


def no_to_ip(no):
    no = ('0' * 8 + hex(no)[2:])[-8:]
    i = map(str, map(lambda x: int(x, 16), [no[i:i + 2] for i in range(0, len(no), 2)]))
    return '.'.join(i)


def get_home_path():
    return expanduser("~")
