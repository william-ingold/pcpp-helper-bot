from pcpp.pcpartpickerlist import PCPartPickerList
from markupcreator import MarkupCreator

from pcpphelperbot import PCPPHelperBot

if __name__ == '__main__':
    test_url = 'https://pcpartpicker.com/list/PtCbTJ'
    
    pcpp = PCPartPickerList()
    
    # Load it locally
    test_html = 'C:/Users/willi/Development/PycharmProjects/pcpp-helper-bot/test-pages/page_two.htm'
    with open(test_html, 'r') as file:
        page_html = file.read()
        
    pcpp.parse_page(page_html)
    pcpp.print_parts()
    print(pcpp.total)
    
    MC = MarkupCreator(test_url, pcpp.parts_list, pcpp.total)
    MC.create_markup_table()
    print(MC.markup)
    
    """
    bot = PCPPHelperBot()
    bot.monitor_subreddit('buildapc')
    """
