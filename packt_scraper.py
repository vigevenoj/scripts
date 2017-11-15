#!/usr/bin/env python3

import datetime
import requests
from bs4 import BeautifulSoup


class Book():
    """
    It's a book. It has a title and a link.
    """
    def __init__(self, title, link):
        self._title = title
        self._link = link

    @property
    def title(self):
        return self._title

    @property
    def link(self):
        return self._link


class Notification():
    """
    Holds some info for notifying about the book
    """

    def __init__(self, book):
        self._book = book

    def text(self):
        text = "The free ebook for {0} is {1}".format(
            str(datetime.date.today()),
            self._book.title)
        return text


class Scraper():
    """
    Scrapes the Packt page for the book information
    """
    def __init__(self):
        self._base = "https://www.packtpub.com/packt/offers/free-learning"
        # The python requests default user agent is blocked
        self._useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36"

    def fetch(self):
        book_response = requests.get(self._base, headers={
            'User-Agent': self._useragent})
        if book_response != "200":
            print("Problem fetching page, got {0}".format(
                book_response.status_code))
        return book_response.content

    def parse(self, content):
        """
        Parse the content passed in
        """
        soup = BeautifulSoup(content, "lxml")
        title = soup.find("div", class_="dotd-title").text.strip()
        book = Book(title, None)
        return book

if __name__ == '__main__':
    scraper = Scraper()
    content = scraper.fetch()
    book = scraper.parse(content)
    notification = Notification(book)
    print(notification.text())
#    print(book.title)
