import unittest
from pcpp.pcppparser import PCPPParser
from postparsing import detect_pcpp_html_elements


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
        self.assertEqual(expected_anon, elements['anon'][0]['href'])
        
        self.assertEqual(1, len(elements['pcpp_headers']))
        self.assertEqual(1, len(elements['table_headers']))
        self.assertEqual(1, len(elements['table_footers']))

    def test_parse_reddit_with_table_euro(self):
        fp = '../test-posts/table_euro.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(0, len(elements['identifiable']))
    
        self.assertEqual(1, len(elements['anon']))
        expected_anon = 'https://be.pcpartpicker.com/list/KytcBc'
        self.assertEqual(expected_anon, elements['anon'][0]['href'])
    
        self.assertEqual(1, len(elements['pcpp_headers']))
        self.assertEqual(1, len(elements['table_headers']))
        self.assertEqual(1, len(elements['table_footers']))

    def test_parse_reddit_with_table_broken(self):
        fp = '../test-posts/table_broken.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(0, len(elements['identifiable']))
    
        self.assertEqual(1, len(elements['anon']))
        expected_anon = 'https://pcpartpicker.com/list/9qMcNP'
        self.assertEqual(expected_anon, elements['anon'][0]['href'])
    
        self.assertEqual(0, len(elements['pcpp_headers']))
        self.assertEqual(0, len(elements['table_headers']))
        self.assertEqual(0, len(elements['table_footers']))

    def test_parse_reddit_with_table_broken_partial(self):
        fp = '../test-posts/table_partial.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(0, len(elements['identifiable']))
    
        self.assertEqual(1, len(elements['anon']))
        expected_anon = 'https://pcpartpicker.com/list/C6qdgt'
        self.assertEqual(expected_anon, elements['anon'][0]['href'])
    
        self.assertEqual(1, len(elements['pcpp_headers']))
        self.assertEqual(1, len(elements['table_headers']))
        self.assertEqual(0, len(elements['table_footers']))

    def test_parse_reddit_with_table_unfin_footer(self):
        fp = '../test-posts/table_unfin_footer.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(0, len(elements['identifiable']))
    
        self.assertEqual(1, len(elements['anon']))
        expected_anon = 'https://pcpartpicker.com/list/JLpB4d'
        self.assertEqual(expected_anon, elements['anon'][0]['href'])
    
        self.assertEqual(1, len(elements['pcpp_headers']))
        self.assertEqual(1, len(elements['table_headers']))
        self.assertEqual(1, len(elements['table_footers']))

    def test_parse_reddit_with_anon_no_table(self):
        fp = '../test-posts/anon_link.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(0, len(elements['identifiable']))
    
        self.assertEqual(1, len(elements['anon']))
        expected_anon = 'https://pcpartpicker.com/list/3pK2Bc'
        self.assertEqual(expected_anon, elements['anon'][0]['href'])
    
        self.assertEqual(0, len(elements['pcpp_headers']))
        self.assertEqual(0, len(elements['table_headers']))
        self.assertEqual(0, len(elements['table_footers']))

    def test_parse_reddit_with_iden_no_table(self):
        fp = '../test-posts/iden_link.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(1, len(elements['identifiable']))
        expected_iden = 'https://pcpartpicker.com/user/RunDoctorRun/saved/FFrVWZ'
        self.assertEqual(expected_iden, elements['identifiable'][0]['href'])
    
        self.assertEqual(0, len(elements['anon']))
        self.assertEqual(0, len(elements['pcpp_headers']))
        self.assertEqual(0, len(elements['table_headers']))
        self.assertEqual(0, len(elements['table_footers']))

    def test_parse_reddit_with_iden_view_no_table(self):
        fp = '../test-posts/iden_link_view.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(1, len(elements['identifiable']))
        expected_iden = 'https://pcpartpicker.com/user/haydenholton/saved/#view=szvVWZ'
        self.assertEqual(expected_iden, elements['identifiable'][0]['href'])
    
        self.assertEqual(0, len(elements['anon']))
        self.assertEqual(0, len(elements['pcpp_headers']))
        self.assertEqual(0, len(elements['table_headers']))
        self.assertEqual(0, len(elements['table_footers']))


if __name__ == '__main__':
    unittest.main()
