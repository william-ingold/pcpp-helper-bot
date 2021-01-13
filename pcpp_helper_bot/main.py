from pcpp.pcpartpickerlist import PCPartPickerList
from tablecreator import TableCreator

from pcpphelperbot import PCPPHelperBot


def run_parse_local(pcpp:PCPartPickerList):
    pcpp.set_local()
    test_html = '../test-pages/page_two.htm'
    with open(test_html, 'r') as file:
        local_html = file.read()
        
    dummy_url = 'www.TEST-URL.com'
    return local_html, dummy_url


def run_parse_live():
    test_url = 'https://pcpartpicker.com/list/HQzZgJ'
    live_html = pcpp.request_page_data(test_url)

    return live_html, test_url


def run_reddit_bot():
    bot = PCPPHelperBot()
    bot.monitor_subreddit('buildapc')


if __name__ == '__main__':
    pcpp = PCPartPickerList()
    
    #page_html, url = run_parse_live()
    page_html, url = run_parse_local(pcpp)
    pcpp.parse_page(page_html)
    pcpp.print_parts()
    print(pcpp.total)
    
    TC = TableCreator()
    TC.create_markup_table(pcpp.url, pcpp.parts_list, pcpp.total)
    print(TC.markup)
    
    # run_reddit_bot()
