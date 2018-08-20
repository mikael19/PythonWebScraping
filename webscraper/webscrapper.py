from requests import get
from bs4 import BeautifulSoup
import urllib2
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import xlwt


class WebScrapper:
    """
    Web scrapper class. Gets html from the url given to it,
    and does the scrapping, then write results to excel file"""

    def __init__(self, web_url, with_scroll=True, excel_file_name='sights_in_africa', excel_sheet_name='Sights In Africa'):
        self.web_url = web_url
        self.parsed_html = ""
        self.with_scroll = with_scroll
        self.excel_file_name = excel_file_name
        self.excel_sheet_name = excel_sheet_name
        self.web_header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                           'Accept-Encoding': 'none',
                           'Accept-Language': 'en-US,en;q=0.8',
                           'Connection': 'keep-alive'}
        if self.with_scroll:
            self.get_sights_with_scroll()
        else:
            self.get_sights_without_scroll()


    def get_sights_with_scroll(self):
        """Gets page html, then get all sights
        by srolling the page to get the
        sights that are loaded upon scroll"""
        option = webdriver.ChromeOptions()
        browser = webdriver.Chrome(executable_path='/usr/bin/chromedriver', chrome_options=option)
        browser.get(self.web_url)
        time.sleep(1)

        elem = browser.find_element_by_tag_name("body")

        lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while match == False:
            lastCount = lenOfPage
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(3)
            lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            if lastCount == lenOfPage:
                match=True

        post_elems = browser.find_elements_by_class_name("ListItem-container")
        self.parsed_html =BeautifulSoup(browser.page_source, 'html.parser')
        self.get_sights_in_africa()


    def get_sights_without_scroll(self):
        """Gets page html, then get sights
        without srolling the page to get the
        sights that are loaded upon scroll"""
        html_request = urllib2.Request(self.web_url, headers=self.web_header)
        page = ""
        try:
            page = urllib2.urlopen(html_request)
        except urllib2.HTTPError, e:
            print(e.fp.read())
        self.parsed_html = BeautifulSoup(page.read(), 'html.parser')
        self.get_sights_in_africa()


    def rreplace(self, s, old, new, occurrence):
        li = s.rsplit(old, occurrence)
        return new.join(li)


    def get_sights_in_africa(self):
        """Gets sights data from html page."""
        content_lst = []
        for item in self.parsed_html.find_all('div', attrs={'class': 'ListItem-container'}):
            span0_content = item.select('div > div > header > div > span')[0].get_text(strip=True)
            site_location_content = item.select('div > div > header > div > span')
            site_location = ""
            if len(site_location_content) > 1:
                site_location = site_location_content[1].get_text(strip=True)
            site_name = item.select('div > div > header > h2')[0].get_text(strip=True)
            site_description = item.select('div > div > div')[0].get_text(strip=True)
            site_type = item.select('div > div > header > div')[0].get_text(strip=True)
            if site_name != site_location:
                site_type = site_type.replace(site_location, '', 1)
            if site_type.count(site_name) > 1:
                site_type = self.rreplace(site_type, site_name, '', 1)
            if site_name != span0_content:
                site_type = site_type.replace(span0_content, '', 1)
            site_location = site_location.replace('in', '', 1).lstrip()
            content_lst.append([site_name, site_type, site_location, site_description])
        self.write_to_excel(content_lst)


    def write_to_excel(self, excel_complete_content):
        """Write page data to excel file."""
        book = xlwt.Workbook()
        sheet = book.add_sheet(self.excel_sheet_name)
        sheet.write(0, 0, "Name")
        sheet.write(0, 1, "Type")
        sheet.write(0, 2, "Location")
        sheet.write(0, 3, "Description")
        content = sorted(excel_complete_content, key = lambda x: x[2])

        row = 1
        col = 0

        for excel_row_content in (content):
            sheet.write(row, col,     excel_row_content[0])
            sheet.write(row, col + 1, excel_row_content[1])
            sheet.write(row, col + 2, excel_row_content[2])
            sheet.write(row, col + 3, excel_row_content[3])
            row += 1
        book.save("{0}.xls".format(self.excel_file_name))
