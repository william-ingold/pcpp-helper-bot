import requests
import logging
import re
import traceback

from bs4 import BeautifulSoup

from pcpp.part import Part


class PCPartPickerList:
    """Parses component list table from PC Part Picker.
    
    This can take either URL to the PC Part Picker list, or an HTML document,
    and parses each component. A component is simply a
    :class:`~pcpp-helper-bot.Part` object.
    
    Attributes:
        total (str): String containing the currency and price.
        parts_list (list(Part)): List of parts from the PC Part Picker list.
    """
    
    def __init__(self):
        """Initializes setup variables."""
        
        self.pcpp_base_url = 'https://pcpartpicker.com'
        self.url = ''
        self.total = '0.0'
        self.desired_cols = ['component', 'name', 'price', 'where']
        self.parts_list = []
        
        self.GET_VENDOR_URLS = False
        
    def set_local(self):
        """If files are local, full url will be in <a> tags."""
        self.pcpp_base_url = ''

    def request_page_data(self, url: str):
        """Requests the PC Part Picker url for HTML text.
        
        Args:
            url (str): URL to a PC Part Picker component list.
            
        Returns:
            HTML text from the page of the URL.
            
        Raises:
            AttributeError if the URL or page was malformed.
        """
        
        self.url = url
        try:
            response = requests.get(self.url)
            
            if response.status_code == 200:
                logging.info('Request status code was successful')
                return response.text
            else:
                logging.error(f'Could not resolve PC Part Picker URL. Status code: {response.status_code}, URL: {self.url}')
                raise AttributeError('PC Part Picker URL or Page malformed', self.url)
        except:
            logging.error(f'Request error: {traceback.print_exc()}')
        
    def parse_page(self, html_doc):
        """Parses the provided html_doc for its component list.
        
        Args:
            html_doc (str): HTML document with component list.
        """
        
        # Reset data
        self.parts_list = []
        self.url = ''
        self.total = '0.0'

        # Use BeautifulSoup to find the div with class '.partlist' (Only one)
        soup = BeautifulSoup(html_doc, 'lxml')
        div_partlist = soup.find("div", class_="partlist")
        
        # Check if the div was found and it contains a <table> element
        if div_partlist and div_partlist.table:
            logging.info('Found the part list table')
            
            # Parse the PC parts
            table_body = div_partlist.table.tbody
            self._parse_list(table_body)
        
        else:
            logging.error('Could not find the part list table.\n URL: %s', self.url)

    def get_anon_list_url(self, iden_url: str):
        """Parses a user's list page for the anonymous list url, then parses
        that page.

        An example would be https://pcpartpicker.com/user/<usermame>/saved/ABC123
        but, we don't want users sharing these and instead prefer anonymous links
        such as https://pcpartpicker.com/list/ABC123

        Args:
            iden_url (str): An identifiable URL to a PC Part Picker list.
        """
    
        html_doc = self.request_page_data(iden_url)
        soup = BeautifulSoup(html_doc, 'lxml')
        markup = soup.find('textarea', id='markup_text')
    
        anon_url_pat = r"(https://pcpartpicker.com/list/\w+)"
        anon_url = re.search(anon_url_pat, markup).group()
        
        return anon_url

    def _parse_list(self, table_body):
        """Parses the only the component list table body from PC Part Picker."
        
        Args:
            table_body (:obj:`bs4.element.tag`): BeautifulSoup object holding
                the table body tag <tbody> of the component list.
        """
        
        for row in table_body.find_all('tr'):
            data = self._parse_row(row)
            
            row_classes = row.get('class')
            if row_classes:
                if 'tr__product' in row_classes:
                    
                    # TODO: Check if the data was empty or bad
                    component = Part(**data)
                    self.parts_list.append(component)
                
                elif 'tr__total--final' in row_classes:
                    # Text will be: 'Total: <currency><price>
                    self.total = row.text.replace('Total:', '').strip()
    
    def _parse_row(self, table_row):
        """Parses a single row of the component list table.
        
        A row may either be a component, or the total pricing.
        
        Args:
            table_row (:obj:`bs4.element.tag`): A <tr> from the component table list.

        Returns:
            A :dict: holding the component, name, url, price, vendor, and vendor_aff_url.
        """
        
        data = {'component': '', 'name': '', 'url': '', 'price': -1.0,
                'vendor': '', 'vendor_aff_url': '', 'vendor_url': ''}
        
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
                    part_url = col.a.get('href')
                    data['name'] = part_name.strip()
                    data['url'] = self.pcpp_base_url + part_url
                
                # Get the price. Only a link if the vendor is specified
                elif col_name == 'price' and 'td--empty' not in col_classes:
                    # Remove the h6.xs-block with the header "Price" for smaller screens
                    price_header = col.find('h6', class_='xs-block')
                    if price_header:
                        price_header.decompose()
                    
                    if col.find('a'):
                        price = col.a.text.strip()
                    else:
                        price = col.text.strip()
                    
                    data['price'] = price
                
                # Always a link
                elif col_name == 'component':
                    data['component'] = col.a.text.strip()
                
                # Get the vendor, or if its been purchased
                elif col_name == 'where' and 'td--empty' not in col_classes:
                    if col.text == 'Purchased':
                        data['vendor'] = 'Purchased'
                    elif col.find('a'):
                        vendor_aff_url = col.a.get('href')
                        vendor_aff_url = self.pcpp_base_url + vendor_aff_url
    
                        # Link format: /mr/<vendor name>/<hash>
                        vendor = re.findall(r"\/mr\/(\w*)\/", vendor_aff_url)
    
                        # TODO: Improve upon vendor names
                        if len(vendor) != 0:
                            vendor = update_vendor(vendor[0])
                            data['vendor'] = vendor
                            
                        if self.GET_VENDOR_URLS:
                            data['vendor_aff_url'] = vendor_aff_url
                            # Get the actual vendor URL (redirected to it)
                            r = requests.get(data['vendor_aff_url'])
                            if len(r.history) > 1:
                                data['vendor_url'] = r.history[-1].url
                            elif vendor.lower() == "amazon":
                                data['vendor_url'] = r.history[0].headers['Location']

        return data

    def print_parts(self):
        """Prints the parts from a component list."""
        for part in self.parts_list:
            print(part)
            

# TODO: Store in another format or create them more intelligently?
# One word vendors are taken care of by simply capitalizing them.
vendor_mapping = {
    'bestbuy': 'Best Buy',
    'westerndigital': 'Western Digital',
    'bhphotovideo': 'B&H Photo',
    'bytesatwork': 'Bytes At Work',
    'alternatebe': 'Alternate Belgium'
}


def update_vendor(vendor: str):
    """Updates the vendor name to a proper format.
    
    Args:
        vendor (str): Name of the vendor.

    Returns:
        A properly formatted vendor name.
    """
    
    if vendor in vendor_mapping:
        return vendor_mapping[vendor]
    else:
        return vendor.capitalize()
