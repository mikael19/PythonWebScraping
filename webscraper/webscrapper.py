from requests import get
from bs4 import BeautifulSoup
import urllib2
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import xlwt
import datetime

"""
Assumptions made:
- payment by credit card is payment by mastercard
- payment_mobile is payment via google checkout


Questions:
- For a particular shop, what do the following json dictionary entries represent?
	- scraped, paymentnfc, shopcode, wifi, id, notification_type, parent_id, shop_type, intro_message, notes, menu
"""

class WebScrapper:
    """
    Web scrapper class. Gets html from the url given to it,
    and does the scrapping, then write results to json file"""

    def __init__(self, web_url, with_scroll=False, file_name='shops_and_products'):
        self.web_url = web_url
        self.shop_list_url = "https://geizhals.at/?hlist"
        self.parsed_html = ""
        self.with_scroll = with_scroll
        self.file_name = file_name
        self.web_header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                           'Accept-Encoding': 'none',
                           'Accept-Language': 'en-US,en;q=0.8',
                           'Connection': 'keep-alive'}
        self.get_shops_and_products()


    def get_shops_and_products(self):
        """Scrapes both shops and products of the website"""
        self.get_shops()


    def parse_page(self, browser):
        """Parses the html of the given browser instance"""
        parsed_html = BeautifulSoup(browser.page_source, 'html.parser')
        return parsed_html


    def open_page(self, page_url):
        """Open page url given to it, and returns a browser instance"""
        option = webdriver.ChromeOptions()
        browser = webdriver.Chrome(executable_path='/usr/bin/chromedriver', chrome_options=option)
        browser.get(page_url)
        time.sleep(1)
        return browser


    def get_payment_types(self, td_html_content, is_web):
        dict_data = {
            "payment_mobile" : False,
            "payment_cash_only" : False,
            "payment_debit_card" : False,
            "payment_paypal" : False,
            "payment_credit_card" : False,
            "paymentnfc" : False,
            "scraped" : True,
            "country": "",
            "city": ""
        }
        pay_img_list = td_html_content.find_all('img',{'height':'14', 'width':'14'})
        if pay_img_list[-1].has_attr("src"):
            if pay_img_list[-1]["src"].endswith("on.gif"):
                dict_data["payment_paypal"] = True
        if not is_web:
            if pay_img_list[0].has_attr("src"):
                if pay_img_list[0]["src"].endswith("on.gif"):
                    country_city_text = pay_img_list[0].next_sibling
                    if '(' in country_city_text and ')' in country_city_text:
                        dict_data["country"] = country_city_text[country_city_text.find("(")+1:country_city_text.find(")")]
                        dict_data["city"] = country_city_text.split("(")[0]
        if pay_img_list[2].has_attr("src"):
            if pay_img_list[2]["src"].endswith("on.gif"):
                dict_data["payment_debit_card"] = True
        if pay_img_list[1].has_attr("src"):
            if pay_img_list[1]["src"].endswith("on.gif"):
                dict_data["payment_cash_only"] = True
        if pay_img_list[12].has_attr("src"):
            if pay_img_list[12]["src"].endswith("on.gif"):
                dict_data["payment_credit_card"] = True
        if pay_img_list[24].has_attr("src"):
            if pay_img_list[24]["src"].endswith("on.gif"):
                dict_data["payment_mobile"] = True
        return dict_data


    def get_shop_data(self, browser):
        browser.refresh()
        parsed_shop_html = self.parse_page(browser)
        shop_name = parsed_shop_html.find('span', attrs={'class': 'firma'})
        shop_name = shop_name.text.strip()
        logo_url = parsed_shop_html.find('img', alt=shop_name).get('src', '') if parsed_shop_html.find('img', alt=shop_name) is not None else ''
        first_table = parsed_shop_html.find('div',{'id':'maintable'}).findNext('table').findNext('tbody').find_all('tr')[0].findNext('td').findNext('table')
        second_table = parsed_shop_html.find('div',{'id':'maintable'}).findNext('table').findNext('tbody').find_all('tr')[1].findNext('td').findNext('table')
        first_td = first_table.find('tbody').find_all('tr')[1].findNext('td')
        is_web_shop = len(first_table.find('tbody').find_all('tr')[1].find_all('td')[2].find_all('div')[0].contents) == 1
        email = first_td.findNext('a').text.strip()
        website = first_td.find_all('a')[1]
        if website.has_attr("href"):
            website = website['href']
        created_at = first_table.find('tbody').find_all('tr')[1].findNext('td').findNext('time').text.strip()
        second_table_second_tr = second_table.find('tbody').find_all('tr')[1]
        second_table_first_td = second_table_second_tr.find_all('td')[0]
        second_table_second_td = second_table_second_tr.find_all('td')[2] if len(second_table_second_tr.find_all('td')) > 2 else None
        dict_data = self.get_payment_types(second_table_first_td, is_web_shop)
        shop_json_data = {
            "created_at" : created_at,
            "logo" : logo_url,
            "link" : website,
            "web_shop" : is_web_shop,
            "email" : email,
            "name" : shop_name,
            "payment_mobile" : dict_data["payment_mobile"],
            "payment_cash_only" : dict_data["payment_cash_only"],
            "payment_debit_card" : dict_data["payment_debit_card"],
            "payment_paypal" : dict_data["payment_paypal"],
            "paymentnfc" : dict_data["paymentnfc"],
            "scraped" : dict_data["scraped"],
            "payment_credit_card" : dict_data["payment_credit_card"],
            "country" : dict_data["country"],
            "city" : dict_data["city"],
            "updated_at" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "has_availabilities" : not is_web_shop,
            "opening_hours" : "Mo-Fr 09:00 - 18:00 Uhr\nSa 09:00 - 12:00 Uhr\nSo Geschlossen",
            "phone" : None,
            "shop_code" : None,
            "wifi" : False,
            "id" : 737498,
            "street" : "B",
            "imprinturl" : None,
            "slug" : "",
            "location" : "",
            "version" : 0,
            "notification_type" : 0,
            "parent_id" : None,
            "shop_type" : 0,
            "intro_message" : None,
            "zip" : "1030",
            "color" : None,
            "title_image" : None,
            "wheel_chair_accessibility" : True,
            "account_data" : None,
            "notes" : None,
            "menu" : None,
        }
        return shop_json_data


    def get_single_shop_info(self, shop_tr, browser):
        """Click on a shop and get its information"""
        first_td_link = shop_tr.find('td')
        shop_anchor = first_td_link.find('a')
        shop_link = browser.find_element_by_xpath('//a[@href="'+shop_anchor['href']+'"]')
        shop_link.click()
        time.sleep(2)
        # Get shop data
        shop_dict = self.get_shop_data(browser)
        # Go to previous page
        browser.back()
        return shop_dict


    def get_shops(self):
        """Gets shops"""
        opened_page_browser = self.open_page(self.shop_list_url)
        parsed_shop_html = self.parse_page(opened_page_browser)
        next_button_class_name = "gh_pag_next_active"
        for item in range(0, 20):
            page_next_button = None
            try:
                page_next_button = opened_page_browser.find_element_by_class_name(next_button_class_name)
            except NoSuchElementException:
                print("element does not exist")
            if page_next_button is not None:
                table = parsed_shop_html.find('table', attrs={'id': 'gh_hlist_table'})
                table_body = table.find('tbody')
                shops = table_body.find_all('tr')
                for shop in shops:
                    if len(shop.find_all('td')) > 1:
                        shop_data = self.get_single_shop_info(shop, opened_page_browser)
                        self.write_shops_to_json(shop_data)
                if page_next_button is not None:
                    opened_page_browser.refresh()
                    page_next_button = opened_page_browser.find_element_by_class_name(next_button_class_name)
                    page_next_button.click()
                    time.sleep(2)
                    opened_page_browser.refresh()
                    parsed_shop_html = self.parse_page(opened_page_browser)



    def write_shops_to_json(self, data):
        """Write data to json file"""
        f = open(self.file_name,"a+")
        f.write("{0}\r\n".format(data))
        f.close()
