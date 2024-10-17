#!/usr/bin/python3
# coding: Latin-1

import os
import re
import sys
import argparse
import datetime
from datetime import date
from datetime import timedelta
import time
from time import localtime
import traceback
from pathlib import Path
import json

import httpx
from requests import JSONDecodeError, ConnectionError, ConnectTimeout

SOURCE_PATH = Path(__file__).resolve().parent

class Product:
    """
    Data-storage class for products.
    """

    def __init__(self):
        self._id = ''
        self._name = ''
        self._price = ''
        self._discount = ''
        self._discount_valid = ''
        self._link = ''
        self._base_price = ''
        self._description = ''
        self._category = ''

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = self.__clean_string(name)

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, price):
        if price is str:
            self._price = self.__clean_string(price).replace('.', ',')
        else:
            self._price = str(price).replace('.', ',')

    @property
    def discount(self):
        return self._discount

    @discount.setter
    def discount(self, discount):
        self._discount = self.__clean_string(discount)

    @property
    def discount_valid(self):
        return self._discount_valid

    @discount_valid.setter
    def discount_valid(self, discount_valid):
        self._discount_valid = self.__clean_string(discount_valid)

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, link):
        self._link = self.__clean_string(link)

    @property
    def base_price(self):
        return self._base_price

    @base_price.setter
    def base_price(self, base_price):
        self._base_price = self.__clean_string(base_price)

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = self.__clean_string(description)

    @property
    def category(self):
        return self._category

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    def __clean_string(self, input):
        """
        Replaces all newline characters in an input string with blank spaces.

        Args:
            input (str): Input string.

        Returns:
            output (str): Cleaned output string.

        """
        output = (input.replace('\n', ' ').replace('\u2028', ' ')
                  .replace('\u000A', ' ').rstrip().lstrip())
        return output


def custom_exit(message):
    traceback.print_exc()
    print(message)
    sys.exit(1)

def load_product_highlights():
    # Check and process highlights file
    product_highlights = []
    if highlight_file:
        try:
            with open(highlight_file, 'r') as file:
                all_lines = file.readlines()
            product_highlights = [item.strip('\n') for item in all_lines if
                                  not item.startswith('#') and item.strip('\n')]
        except FileNotFoundError:  # file not found or
            custom_exit('FAIL: Highlights file "{}" not found. '
                        'Please check for typos or create it and write one url per line.'.format(highlight_file))
        if not product_highlights:
            print('WARNING: No product highlights in file "{}" found. '
                  'Ignoring user request to highlight and continuing anyway.'.format(highlight_file))
    return product_highlights


def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def remove_prefix(input_string, prefix):
    if prefix and input_string.startswith(prefix):
        return input_string[len(prefix):]
    return input_string

def print_market_ids(zip_code):
    useproxy = 1
    url = "https://www.netto-online.de/api/stores/search_stores?latitude=50.000000000000000&longitude=8.000000000000000&dist=15.00000000&api_user=nettoapp&api_token=e6Ddd8gYybhZVTen&user_ip=91.237.117.254"
    headers = {"user-agent": "NettoApp/7.1.2 (Build: 7.1.2.1; Android 11)"}
    while True:
      if useproxy == 1:        
        proxycmd = "socks5://user:try" + datetime.datetime.now().strftime('%M%S') + "@127.0.0.1:9150"
        res = httpx.Client(http1=True, timeout=60.0, headers=headers, proxy=proxycmd).get(url)
      else:
        res = httpx.Client(http1=True, headers=headers, timeout=50).get(url)
      sys.stderr.write('Status-Code: ' + str(res.status_code) + "\n")
      if res.status_code == 200:
        break



    try:
      markets_raw = res.json()
    except:
      return None

    if not ((data := markets_raw.get("data")) != None) and (len(data) != 0):
      return None
  
    markets_raw = data
    print('  ID     Location')

    for market_raw in markets_raw:
      id = market_name = street_with_house_number = city = zip_code = latitude = longitude = None
      if not ((id := market_raw.get("store_id"))
              and (market_name := market_raw.get("store_name"))
              and (street_with_house_number := market_raw.get("street"))
              and (city := market_raw.get("city"))
              and (zip_code := market_raw.get("post_code"))
              and (latitude := market_raw.get("coord_latitude"))
              and (longitude := market_raw.get("coord_longitude"))):
        return None
      print('{}: {}, {}, {} {}'.format(id, market_name, street_with_house_number,zip_code,city))

    print('\nEnde.')
    sys.exit(0)


def elegant_query(market_id):
    useproxy = 1

    url = "https://www.clickforbrand.de/offers-qa/rest/v1/offers?store_id=" + market_id
    proxycmd = "socks5://userf:try" + datetime.datetime.now().strftime('%M%S') + "@127.0.0.1:9150"
    headers = {
      "user-agent": "NettoApp/7.1.2 (Build: 7.1.2.1; Android 11)",
      "x-netto-api-key": "78b72bf5-3229-4972-88df-486bcf6191bb",
    }
    while True:
      if useproxy == 1:        
        proxycmd = "socks5://user:try" + datetime.datetime.now().strftime('%M%S') + "@127.0.0.1:9150"
        res = httpx.Client(http1=True, timeout=60.0, headers=headers, proxy=proxycmd).get(url)
      else:
        res = httpx.Client(http1=True, headers=headers, timeout=50).get(url)
      sys.stderr.write('Status-Code: ' + str(res.status_code) + "\n")
      if res.status_code == 200:
        break

    try:
      markets = res.json()
    except:
      return None

    products_raw = markets.get("data")
    try:
      n = 0
      ausgabe = ''

      for category in products_raw:
        valid_from = valid_to = articles = None
        if not ((valid_from := category.get("offer_date_valid_from")) 
                and (valid_to := category.get("offer_date_valid_to"))
                and (articles := category.get("article"))):
          continue
        date_format = "%Y-%m-%d %H:%M:%S"
        valid_from = datetime.datetime.strptime(valid_from, date_format)
        valid_from = date(valid_from.year, valid_from.month, valid_from.day)
        valid_to = datetime.datetime.strptime(valid_to, date_format)
        valid_to = date(valid_to.year, valid_to.month, valid_to.day)
        ausgabe += '\n# ' + category["link_title"] + ' ab ' + str(valid_from) + '\n'
        for article in articles:
          is_online = article.get("isOnline")
          if is_online == "true":
            continue
          if not ((name := article.get("title"))
                  and (price_raw := article.get("price"))
                  and (price := price_raw.get("price"))):
            continue
          product = Product()
          product.valid_from = valid_from
          product.valid_to = valid_to
          product.name = name
          product.link = article.get("image")
          product.price = remove_suffix(price,"*")
          product.quantity = article.get("text_gebinde")
          if (base_price_raw := article.get("hp_grundpreis")) != "":
            base_price_raw = base_price_raw.split("/")
            if len(base_price_raw) >= 2:
              base_price = base_price_raw[:-1]
              base_price = "/".join(base_price)
              base_price_unit = base_price_raw[-1]
            else:
              pass
            base_price = base_price.strip()
            product.base_price = base_price
            product.base_price_unit = base_price_unit.strip()
          if (price_before := price_raw.get("save_price")) != "":
            if (price_before_match := re.search(r"\d+", price_before)) != None and (price_before_match.group() != ""):
              #price_before = price_before.strip().removeprefix("UVP").removeprefix("statt").strip()
              remove_prefix(price_before,"UVP")
              remove_prefix(price_before,"statt").strip()
              product.price_before = price_before
          description = article.get("description_short").replace("<br />", " ")
          description = re.match("[^<]*", description).group()

          if (description_extra := article.get("text_more_info").replace("<br />", " ")):
            description = ", ".join([description, description_extra])
          product.description = remove_prefix(description,"versch. Sorten")

          ausgabe += product.name
          ausgabe += ';' + product.price + ' €'
          ausgabe += ';' + product.link
          ausgabe += ';' + product.quantity
          if product.base_price:
              ausgabe += ' (' + product.base_price + ')'
          if product.description:
              ausgabe += ';' + product.description
          ausgabe += '\n'
          n += 1

      with open(output_file, 'w', encoding="utf-8") as file:
          file.truncate(0)
          print(ausgabe, file=file)

      print('{} OK: Wrote {} discounts to file "{}".'.format(
          datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
          n, 
          output_file))

    except Exception as err:
      sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Fetches current Rewe discount offers for a specific market.',
        epilog=
        'Example usages:\n'
        ' - Prints the market IDs of all Rewe markets in/near the zip code/PLZ "63773":\n'
        '      rewe_discounts.py --list-markets 63773\n'
        ' - Exports current discounts of the market with the ID "562286":\n'
        '      rewe_discounts.py --market-id 562286 --output-file "Angebote Rewe.md"\n'
        ' - Exports current discounts of the market with the ID "562286" and highlights defined products:\n'
        '      rewe_discounts.py --market-id 562286 --output-file "Angebote Rewe.md" --highlights=highlights.txt'
    )
      
    parser.add_argument('--market-id', type=str, help='= selling_region')
    parser.add_argument('--output-file', type=str, help='Output file path.')
    parser.add_argument('--highlights', type=str, help='Products mentioned in this file, e.g. "Joghurt", '
                                                       'are highlighted in the output file.')
    parser.add_argument('--list-markets', type=str, help='Given the zip code (PLZ), list all markets and their ID.')
    args = parser.parse_args()
    market_id = args.market_id
    output_file = args.output_file
    highlight_file = args.highlights

    if args.list_markets:  # mode "print market IDs"
        print_market_ids(args.list_markets)

    else:  # mode "print offers of selected market"
        if not output_file:
            parser.print_help()
            sys.exit(0)
        try:
            elegant_query(market_id)
        except (JSONDecodeError, ConnectionError, ConnectTimeout):
            print('INFO: Unknown error while fetching discounts.')
        except (KeyError, TypeError):  # data got retrieved successfully
            pass

