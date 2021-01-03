import requests
import logging
import re

from bs4 import BeautifulSoup

from part import Part


class PCPartPickerList:
    
    def __init__(self, url: str):
        self.url = url
        self.total = 0.0
        self.desired_cols = ['component', 'name', 'price']
        self.part_list = []

    def request_page_data(self):
        response = requests.get(self.url)
        
        if response.status_code == 200:
            logging.info('Request status code was successful')
            self.parse_page(response.text)
        else:
            logging.error('Could not resolve PC Part Picker URL. Status code: %s, URL: %s',
                          response.status_code, self.url)

    def parse_page(self, html_doc):
        # Use BeautifulSoup to find the div with class '.partlist' (Only one)
        soup = BeautifulSoup(html_doc, 'lxml')
        div_partlist = soup.find("div", class_="partlist")

        # Check if the div was found and it contains a <table> element
        if div_partlist and div_partlist.table:
            logging.info('Found the part list table')

            # Parse the PC parts
            table_body = div_partlist.table.tbody
            self.parse_list(table_body)

        else:
            logging.error('Could not find the part list table.\n URL: %s', self.url)

    def parse_list(self, table_body):
        for row in table_body.find_all('tr'):
            data = self.parse_row(row)
            
            row_classes = row.get('class')
            if row_classes:
                if 'tr__product' in row_classes:
                
                    # TODO: Check if the data was empty or bad
                    component = Part(**data)
                    self.part_list.append(component)
                    
                elif 'tr__total--final' in row_classes:
                    # Text will be: 'Total: <currency><price>
                    self.total = row.text.replace('Total:', '').strip()

    def parse_row(self, table_row):
        data = {'component': '', 'name': '', 'url': '', 'price': -1.0,
                'vendor': '', 'vendor_url': ''}
        
        for col in table_row.find_all('td'):
            col_classes = col.get('class')
            
            # The column has no classes, ignore it
            if not col_classes:
                continue

            # Class name format: .td__<name> (td--empty)
            col_name = col_classes[0]
            col_name = col_name[4:]

            # Check if it is a wanted column
            if col_name in self.desired_cols:
                
                # Get the name. Always a link, since it is within PCPartPicker
                if col_name == 'name':
                    part_name = col.a.text
                    part_url = 'https://pcpartpicker.com' + col.a.get('href')
                    data['name'] = part_name.strip()
                    data['url'] = part_url

                # Get the price. Only a link if the vendor is specified
                elif col_name == 'price' and 'td--empty' not in col_classes:
                    if col.find('a'):
                        price = col.a.text.strip()
                        
                        vendor_url = col.a.get('href')
                        data['vendor_url'] = vendor_url
                        
                        # Link format: /mr/<vendor name>/<hash>
                        vendor = re.findall("\/mr\/(\w*)\/", vendor_url)
                        
                        # TODO: Improve upon vendor names
                        if len(vendor) != 0:
                            vendor = update_vendor(vendor[0])
                            data['vendor'] = vendor
                    else:
                        price = col.text.strip()
                    
                    # 'Price' is a header used for XS screens
                    data['price'] = price.replace('Price', '')
                        
                # Only other column is the 'Component.' Always a link
                else:
                    data['component'] = col.a.text.strip()
        
        return data
    
    
    def get_data(self):
        return {'Parts': self.part_list, 'Total': self.total}
    
    def print_parts(self):
        for part in self.part_list:
            print(part)
        
    def print_total(self):
        print(self.total)
        
        
# TODO: Store in another format or create them more intelligently?
vendor_mapping = {
    'newegg': 'NewEgg',
    'bestbuy': 'Best Buy',
    'westerndigital': 'Western Digital',
    'bhphotovideo': 'B&H Photo',
    'bytesatwork': 'Bytes At Work',
    'alternatebe': 'Alternate Belgium'
}

def update_vendor(vendor: str):
    if vendor in vendor_mapping:
        return vendor_mapping[vendor]
    else:
        return vendor.capitalize()
