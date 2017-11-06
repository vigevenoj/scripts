#!/usr/bin/env python3

import PyPDF2
import requests
from bs4 import BeautifulSoup

warn_url = "https://ccwd.hecc.oregon.gov/Layoff/WARN"


class WarnListing():
    def __init__(self, track_no, notification_date, layoff_type, count,
                 employer, city, notice_pdf):
        self.track_no = track_no
        self.notification_date = notification_date
        self.layoff_type = layoff_type
        self.count = count
        self.employer = employer
        self.city = city
        self.notice_pdf = notice_pdf
        self.notice_text


class Fetcher():
    """
    Scrape the layoff website and download any new PDFs to parse locally
    """
    def __init__(self):
        pass

    def handle_row(self, row):
        for cell in row.find_all('td'):
            if len(cell.get_text()) > 0:
                print(cell.get_text())
            else:
                if len(cell.find_all('a')) > 0:
                    print(cell.find('a').get('href'))
#            print(cell)
#            print(cells)
#            listing = WarnListing(cells[0], cells[1], cells[2], cells[3],
#                                  cells[4], cells[5], cells[6])
#            print("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}".format(cells[0].get_text(),
#                                                             cells[1].get_text(),
#                                                             cells[2].get_text(),
#                                                             cells[3].get_text(),
#                                                             cells[4].get_text(),
#                                                             cells[5].get_text(),
#                                                             cells[6].get_text()))

    def fetch(self):
        warn_page = requests.get(warn_url).text
        soup = BeautifulSoup(warn_page)
        rows = soup.find("table", id="index").find_all("tr")
        print("track #\t date\t type\t count\t employer\t city\t notice")
        for row in rows:
            self.handle_row(row)


class Parser():
    """
    Parse PDF for text
    """
    def __init__(self):
        pass

    def getPdfContent(self, path):
        content = ""
        try:
            with open(path, 'rb') as f:
                data = f.read()
                pdf = PyPDF2.PdfFileReader(data)
        except IOError as e:
            print("Unable to open {0}: {1}".format(path, e))
        for page in range(0, pdf.getNumPages()):
            page_text = pdf.getPage(page).extractText()
            content += page_text
            print(page_text)
        return content


if __name__ == '__main__':
    fetcher = Fetcher()
    fetcher.fetch()
