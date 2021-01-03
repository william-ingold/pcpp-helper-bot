from pcpartpickerlist import PCPartPickerList

if __name__ == '__main__':
    test_url = 'https://pcpartpicker.com/list/PtCbTJ'
    
    test_html = 'C:/Users/willi/Development/PycharmProjects/pcpp-helper-bot/test-pages/page_one.htm'
    
    pcpp = PCPartPickerList(test_url)
    
    with open(test_html, 'r') as file:
        page_html = file.read()
        
    pcpp.parse_page(page_html)
    pcpp.print_parts()
    pcpp.print_total()
