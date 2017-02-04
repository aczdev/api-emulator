# crawl.py - a small crawler to grab the page content for an API emulator

#!/usr/bin/env python
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re
import requests


def get_headers(link, active=False):
    """Function retuns a list of headers that could be limited by an argument in API call"""
    r = requests.get(link)
    if r.status_code != 200:
        return send_real_error(r)

    # If everything goes OK, proceed with parsing the page source
    soup = BeautifulSoup(r.content, "html5lib")
    soup = BeautifulSoup(soup.prettify(), "html5lib")

    # Gather the list of divs we are looking for
    if active:
        news = soup.find_all("div", attrs={"class": "news-box act"})
    else:
        news = soup.find_all("div", attrs={"class": "news-box"})

    if not news:
        return send_fake_error()

    tab = []
    for i in news:
        temp = {}
        temp['link'] = i.find('div', attrs={"class": "some-button"}).attrs['link']
        temp['id'] = re.findall('[0-9]+', temp['link'])[0]
        temp['img_thumb'] = i.img['src']
        temp['header'] = i.h3.contents[0]

        # Remove any newline characters before sending it to output
        info = i.find('p', attrs={'class': 'overflow-hidden'}).contents[0]
        temp['info'] = ' '.join(info.split())

        # Format the date in a proper one-line way
        day = i.find('p', attrs={'class': 'news-box-date-big'}).contents[0].strip()
        my = i.find_all('p', attrs={'class': 'news-box-date-small'})
        month = my[0].contents[0].strip().lower()
        year = my[1].contents[0].strip()
        temp['date'] = ' '.join([day, month, year])

        # Strip all the newline symbols at the end of key values
        temp = { k:v.strip() for k, v in temp.iteritems()}

        # Insert a key about activity of an event, grabbed from class attribute
        if 'act' in i.attrs['class']:
            temp['active'] = True
        else:
            temp['active'] = False

        # Add to the list of header dictionaries
        tab.append(temp)
    return tab


def get_content(link, news_id):
    """Function gets the content of a selected page and outputs a dictionary"""
    temp = {}
    r = requests.get(link)
    if r.status_code != 200:
        return send_real_error(r)

    # If everything is OK, parse the site code
    soup = BeautifulSoup(r.content, "html5lib")
    soup = BeautifulSoup(soup.prettify(), "html5lib")

    # Grab the div with the real content
    content = soup.find('div', attrs={'id': 'news-list'})
    if not content:
        return send_fake_error()

    # Gather info about all the images and make static links to them
    images = content.findAll('img')
    linkbase = link[:28]
    imglist = [ linkbase + img.attrs['src'] for img in images ]

    # Format all the texts written in content div
    raw_text = str(content)
    formatted = re.sub(r"<[^>]*>", r"", raw_text)

    # Create and return an output dict
    temp['img_urls'] = imglist
    temp['id'] = news_id
    temp['img_count'] = len(images)
    temp['message'] = ' '.join(formatted.split())
    return temp


def status():
    """Function returns current info about the script and the server"""
    status = {}
    status['pid'] = os.getpid()
    status['now'] = datetime.now().strftime("%c")
    status['loadavg'] = os.getloadavg()
    return status


def send_real_error(req):
    """ Short function to return what went wrong with page for real.
        It's necessary since the main page masks real problems with a lame template
        or just prints a console output without any code. If it will get real troubles
        besides 404, this function will show what is the cause of server breakdown."""
    error = {}
    error['error'] = 'Cannot get the request'
    error['status_code'] = req.status_code
    error['reason'] = req.reason
    return error


def send_fake_error():
    """ if the page doesn't have a div with a correct class, the script assumes that
        server tries to display 404 code. That function is just to inform the user what
        supposedly went wrong. """
    fake = {}
    fake['error'] = 'Page not found or the request is malformed'
    fake['status_code'] = '404'
    fake['reason'] = 'Not Found'
    return fake
