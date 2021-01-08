from pcpp.pcpartpickerlist import PCPartPickerList
from tablecreator import TableCreator

from pcpphelperbot import PCPPHelperBot


def run_parse_local():
    test_html = 'C:/Users/willi/Development/PycharmProjects/pcpp-helper-bot/test-pages/page_two.htm'
    with open(test_html, 'r') as file:
        local_html = file.read()
        
    dummy_url = 'www.TEST-URL.com'
    return local_html, dummy_url


def run_parse_live():
    test_url = 'https://pcpartpicker.com/list/HQzZgJ'
    live_html = pcpp.request_page_data(test_url)

    return page_html, test_url


def run_reddit_bot():
    bot = PCPPHelperBot()
    bot.monitor_subreddit('buildapc')


if __name__ == '__main__':
    pcpp = PCPartPickerList()
    
    page_html, url = run_parse_local()
    pcpp.parse_page(page_html)
    pcpp.print_parts()
    print(pcpp.total)
    
    MC = TableCreator(url, pcpp.parts_list, pcpp.total)
    MC.create_markup_table()
    print(MC.markup)
    
    # run_reddit_bot()
