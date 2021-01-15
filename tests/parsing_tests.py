import unittest
from pcpp.pcppparser import PCPPParser
from postparsing import detect_pcpp_html_elements, get_urls_with_no_table, Table, \
    combine_iden_anon_urls


def read_file(filepath):
    with open(filepath, 'r') as file:
        text = file.read().strip()
        
    return text


class MyTestCase(unittest.TestCase):
    
    def setUp(self):
        self.test_pages = [('../test-pages/page_one.htm', '../tests/expected/page_one_part_list.txt'),
                           ('../test-pages/page_two.htm', '../tests/expected/page_two_part_list.txt')]

    def test_request_page_data_valid(self):
        pcpp = PCPPParser()
        test_url = 'https://pcpartpicker.com/list/HQzZgJ'
        html_doc = pcpp.request_page_data(test_url)
        self.assertIsNotNone(html_doc)
        
    def test_request_page_data_invalid(self):
        pcpp = PCPPParser()
        test_url = 'https://pcpartpicker.com/list/abc123'
        html_doc = pcpp.request_page_data(test_url)
        self.assertIsNone(html_doc)

    def test_parse_local_pages(self):
        pcpp = PCPPParser()
        pcpp.set_local()
        
        for local, expected in self.test_pages:
            # TODO: Need a new object per list, should make it only a parser?
            with open(local, 'r') as file:
                local_html = file.read()
                
            expected_parts = []
            with open(expected, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    expected_parts.append(line.strip())
                    
            pcpp.parse_page(local_html)
            actual = []
            for part in pcpp.parts_list:
                actual.append(str(part))
                
            self.assertEqual(expected_parts, actual)
            
    def test_parse_reddit_with_table_us(self):
        fp = '../test-posts/table_us.htm'
        text = read_file(fp)
        
        elements = detect_pcpp_html_elements(text)

        self.assertEqual(0, len(elements['identifiable']))
        
        self.assertEqual(1, len(elements['anon']))
        expected_anon = 'https://pcpartpicker.com/list/phGvqp'
        self.assertEqual(expected_anon, elements['anon'][0])
        self.assertEqual(1, len(elements['tables']))
        self.assertTrue(elements['tables'][0].is_valid)

    def test_parse_reddit_with_table_euro(self):
        fp = '../test-posts/table_euro.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(0, len(elements['identifiable']))
    
        self.assertEqual(1, len(elements['anon']))
        expected_anon = 'https://be.pcpartpicker.com/list/KytcBc'
        self.assertEqual(expected_anon, elements['anon'][0])
    
        self.assertEqual(1, len(elements['tables']))
        self.assertTrue(elements['tables'][0].is_valid())

    def test_parse_reddit_with_table_broken(self):
        fp = '../test-posts/table_broken.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(0, len(elements['identifiable']))
    
        self.assertEqual(1, len(elements['anon']))
        expected_anon = 'https://pcpartpicker.com/list/9qMcNP'
        self.assertEqual(expected_anon, elements['anon'][0])
    
        self.assertEqual(0, len(elements['tables']))

    def test_parse_reddit_with_table_broken_partial(self):
        fp = '../test-posts/table_partial.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(0, len(elements['identifiable']))
    
        self.assertEqual(1, len(elements['anon']))
        expected_anon = 'https://pcpartpicker.com/list/C6qdgt'
        self.assertEqual(expected_anon, elements['anon'][0])
    
        self.assertEqual(1, len(elements['tables']))
        self.assertFalse(elements['tables'][0].is_valid())

    def test_parse_reddit_with_table_unfin_footer(self):
        fp = '../test-posts/table_unfin_footer.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(0, len(elements['identifiable']))
    
        self.assertEqual(1, len(elements['anon']))
        expected_anon = 'https://pcpartpicker.com/list/JLpB4d'
        self.assertEqual(expected_anon, elements['anon'][0])
    
        self.assertEqual(1, len(elements['tables']))
        self.assertTrue(elements['tables'][0].is_valid())

    def test_parse_reddit_with_anon_no_table(self):
        fp = '../test-posts/anon_link.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(0, len(elements['identifiable']))
    
        self.assertEqual(1, len(elements['anon']))
        expected_anon = 'https://pcpartpicker.com/list/3pK2Bc'
        self.assertEqual(expected_anon, elements['anon'][0])
    
        self.assertEqual(0, len(elements['tables']))

    def test_parse_reddit_with_iden_no_table(self):
        fp = '../test-posts/iden_link.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(1, len(elements['identifiable']))
        expected_iden = 'https://pcpartpicker.com/user/RunDoctorRun/saved/FFrVWZ'
        self.assertEqual(expected_iden, elements['identifiable'][0])
    
        self.assertEqual(0, len(elements['anon']))
        self.assertEqual(0, len(elements['tables']))

    def test_parse_reddit_with_iden_view_no_table(self):
        fp = '../test-posts/iden_link_view.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(1, len(elements['identifiable']))
        expected_iden = 'https://pcpartpicker.com/user/haydenholton/saved/szvVWZ'
        self.assertEqual(expected_iden, elements['identifiable'][0])
    
        self.assertEqual(0, len(elements['anon']))
        self.assertEqual(0, len(elements['tables']))
        
    def test_pcpp_urls_anon_no_table(self):
        fp = '../test-posts/anon_link.htm'
        text = read_file(fp)
        
        elements = detect_pcpp_html_elements(text)
        all_anon_urls = combine_iden_anon_urls(elements['anon'], elements['identifiable'])
        remaining_urls = get_urls_with_no_table(all_anon_urls, elements['tables'])
        
        self.assertEqual(1, len(remaining_urls))

    def test_pcpp_urls_broken_table(self):
        fp = '../test-posts/table_broken.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
        all_anon_urls = combine_iden_anon_urls(elements['anon'], elements['identifiable'])
        remaining_urls = get_urls_with_no_table(all_anon_urls, elements['tables'])
    
        self.assertEqual(1, len(remaining_urls))

    def test_pcpp_urls_partial_table(self):
        fp = '../test-posts/table_partial.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
        all_anon_urls = combine_iden_anon_urls(elements['anon'], elements['identifiable'])
        remaining_urls = get_urls_with_no_table(all_anon_urls, elements['tables'])
    
        self.assertEqual(1, len(remaining_urls))

    def test_pcpp_urls_unfin_table(self):
        fp = '../test-posts/table_unfin_footer.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
        all_anon_urls = combine_iden_anon_urls(elements['anon'], elements['identifiable'])
        remaining_urls = get_urls_with_no_table(all_anon_urls, elements['tables'])
    
        self.assertEqual(0, len(remaining_urls))

    def test_pcpp_urls_table_us(self):
        fp = '../test-posts/table_us.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
        all_anon_urls = combine_iden_anon_urls(elements['anon'], elements['identifiable'])
        remaining_urls = get_urls_with_no_table(all_anon_urls, elements['tables'])
    
        self.assertEqual(0, len(remaining_urls))

    def test_pcpp_urls_table_euro(self):
        fp = '../test-posts/table_euro.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
        all_anon_urls = combine_iden_anon_urls(elements['anon'], elements['identifiable'])
        remaining_urls = get_urls_with_no_table(all_anon_urls, elements['tables'])
    
        self.assertEqual(0, len(remaining_urls))
        
    def test_pcpp_urls_iden_anon_same(self):
        fp = '../test-posts/same_anon_iden_links.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
        all_anon_urls = combine_iden_anon_urls(elements['anon'], elements['identifiable'])
    
        self.assertEqual(1, len(all_anon_urls))
        self.assertEqual('https://pcpartpicker.com/list/ZqWwj2', all_anon_urls[0])

    def test_pcpp_urls_iden_anon_same_euro(self):
        fp = '../test-posts/same_anon_iden_links_euro.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
        all_anon_urls = combine_iden_anon_urls(elements['anon'], elements['identifiable'])
    
        self.assertEqual(1, len(all_anon_urls))
        self.assertEqual('https://dk.pcpartpicker.com/list/ZqWwj2', all_anon_urls[0])


if __name__ == '__main__':
    unittest.main()
