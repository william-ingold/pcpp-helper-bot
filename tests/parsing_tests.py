import unittest
import logging

from pcpp.pcppparser import PCPPParser
from postparsing import detect_pcpp_html_elements, get_urls_with_no_table, Table, \
    combine_iden_anon_urls, parse_submission
import postparsing


def read_file(filepath):
    with open(filepath, 'r') as file:
        text = file.read().strip()
        
    return text


class MyTestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        self.test_pages = [('../tests/test-pages/page_one.htm', '../tests/test-pages/expected/page_one_part_list.txt'),
                           ('../tests/test-pages/page_two.htm', '../tests/test-pages/expected/page_two_part_list.txt')]
        self.f_handler = logging.FileHandler(f'../logs/parse_tests.log', mode='w', encoding='utf-8')
        self.pcpp = PCPPParser(self.f_handler)
        
    @classmethod
    def tearDownClass(self):
        self.f_handler.close()

    def test_request_page_data_valid(self):
        test_url = 'https://pcpartpicker.com/list/HQzZgJ'
        html_doc = self.pcpp.request_page_data(test_url)
        self.assertIsNotNone(html_doc)
        
    def test_request_page_data_invalid(self):
        test_url = 'https://pcpartpicker.com/list/abc123'
        html_doc = self.pcpp.request_page_data(test_url)
        self.assertIsNone(html_doc)

    def test_parse_local_pages(self):
        pcpp = PCPPParser(self.f_handler)
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
            
    def test_detect_pcpp_html_table_us(self):
        fp = '../tests/test-posts/table_us.htm'
        text = read_file(fp)
        
        elements = detect_pcpp_html_elements(text)

        self.assertEqual(0, len(elements['identifiable']))
        
        self.assertEqual(1, len(elements['anon']))
        expected_anon = 'https://pcpartpicker.com/list/phGvqp'
        self.assertEqual(expected_anon, elements['anon'][0])
        self.assertEqual(1, len(elements['tables']))
        self.assertTrue(elements['tables'][0].is_valid)

    def test_detect_pcpp_html_table_euro(self):
        fp = '../tests/test-posts/table_euro.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(0, len(elements['identifiable']))
    
        self.assertEqual(1, len(elements['anon']))
        expected_anon = 'https://be.pcpartpicker.com/list/KytcBc'
        self.assertEqual(expected_anon, elements['anon'][0])
    
        self.assertEqual(1, len(elements['tables']))
        self.assertTrue(elements['tables'][0].is_valid())

    def test_detect_pcpp_html_table_broken(self):
        fp = '../tests/test-posts/table_broken.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(0, len(elements['identifiable']))
    
        self.assertEqual(1, len(elements['anon']))
        expected_anon = 'https://pcpartpicker.com/list/9qMcNP'
        self.assertEqual(expected_anon, elements['anon'][0])
    
        self.assertEqual(0, len(elements['tables']))

    def test_detect_pcpp_html_table_partial(self):
        fp = '../tests/test-posts/table_partial.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(0, len(elements['identifiable']))
    
        self.assertEqual(1, len(elements['anon']))
        expected_anon = 'https://pcpartpicker.com/list/C6qdgt'
        self.assertEqual(expected_anon, elements['anon'][0])
    
        self.assertEqual(1, len(elements['tables']))
        self.assertFalse(elements['tables'][0].is_valid())

    def test_detect_pcpp_html_table_unfin_footer(self):
        fp = '../tests/test-posts/table_unfin_footer.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(0, len(elements['identifiable']))
    
        self.assertEqual(1, len(elements['anon']))
        expected_anon = 'https://pcpartpicker.com/list/JLpB4d'
        self.assertEqual(expected_anon, elements['anon'][0])
    
        self.assertEqual(1, len(elements['tables']))
        self.assertTrue(elements['tables'][0].is_valid())

    def test_detect_pcpp_html_anon_no_table(self):
        fp = '../tests/test-posts/anon_link.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(0, len(elements['identifiable']))
    
        self.assertEqual(1, len(elements['anon']))
        expected_anon = 'https://pcpartpicker.com/list/3pK2Bc'
        self.assertEqual(expected_anon, elements['anon'][0])
    
        self.assertEqual(0, len(elements['tables']))

    def test_detect_pcpp_html_iden_no_table(self):
        fp = '../tests/test-posts/iden_link.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(1, len(elements['identifiable']))
        expected_iden = 'https://pcpartpicker.com/user/RunDoctorRun/saved/FFrVWZ'
        self.assertEqual(expected_iden, elements['identifiable'][0])
    
        self.assertEqual(0, len(elements['anon']))
        self.assertEqual(0, len(elements['tables']))

    def test_detect_pcpp_html_iden_view_no_table(self):
        fp = '../tests/test-posts/iden_link_view.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        self.assertEqual(1, len(elements['identifiable']))
        expected_iden = 'https://pcpartpicker.com/user/haydenholton/saved/szvVWZ'
        self.assertEqual(expected_iden, elements['identifiable'][0])
    
        self.assertEqual(0, len(elements['anon']))
        self.assertEqual(0, len(elements['tables']))
        
    def test_unpaired_urls_anon_no_table(self):
        fp = '../tests/test-posts/anon_link.htm'
        text = read_file(fp)
        
        elements = detect_pcpp_html_elements(text)
        all_anon_urls, iden_anon_urls = combine_iden_anon_urls(elements['anon'], elements['identifiable'], self.pcpp)
        remaining_urls = get_urls_with_no_table(all_anon_urls, elements['tables'])
        
        self.assertEqual(1, len(remaining_urls))

    def test_unpaired_urls_broken_table(self):
        fp = '../tests/test-posts/table_broken.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
        all_anon_urls, iden_anon_urls = combine_iden_anon_urls(elements['anon'], elements['identifiable'], self.pcpp)
        remaining_urls = get_urls_with_no_table(all_anon_urls, elements['tables'])
    
        self.assertEqual(1, len(remaining_urls))

    def test_unpaired_urls_partial_table(self):
        fp = '../tests/test-posts/table_partial.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
        all_anon_urls, iden_anon_urls = combine_iden_anon_urls(elements['anon'], elements['identifiable'], self.pcpp)
        remaining_urls = get_urls_with_no_table(all_anon_urls, elements['tables'])
    
        self.assertEqual(1, len(remaining_urls))

    def test_unpaired_urls_unfin_table(self):
        fp = '../tests/test-posts/table_unfin_footer.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
        all_anon_urls, iden_anon_urls = combine_iden_anon_urls(elements['anon'], elements['identifiable'], self.pcpp)
        remaining_urls = get_urls_with_no_table(all_anon_urls, elements['tables'])
    
        self.assertEqual(0, len(remaining_urls))

    def test_unpaired_urls_table_us(self):
        fp = '../tests/test-posts/table_us.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
        all_anon_urls, iden_anon_urls = combine_iden_anon_urls(elements['anon'], elements['identifiable'], self.pcpp)
        remaining_urls = get_urls_with_no_table(all_anon_urls, elements['tables'])
    
        self.assertEqual(0, len(remaining_urls))

    def test_unpaired_urls_table_euro(self):
        fp = '../tests/test-posts/table_euro.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
        all_anon_urls, iden_anon_urls = combine_iden_anon_urls(elements['anon'], elements['identifiable'], self.pcpp)
        remaining_urls = get_urls_with_no_table(all_anon_urls, elements['tables'])
    
        self.assertEqual(0, len(remaining_urls))
        
    def test_unpaired_urls_iden_anon_same(self):
        fp = '../tests/test-posts/same_anon_iden_links.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
        all_anon_urls, iden_anon_urls = combine_iden_anon_urls(elements['anon'], elements['identifiable'], self.pcpp)
    
        self.assertEqual(1, len(all_anon_urls))
        self.assertEqual('https://pcpartpicker.com/list/ZqWwj2', all_anon_urls[0])

    def test_unpaired_urls_iden_anon_same_euro(self):
        fp = '../tests/test-posts/same_anon_iden_links_euro.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
        all_anon_urls, iden_anon_urls = combine_iden_anon_urls(elements['anon'], elements['identifiable'], self.pcpp)
    
        self.assertEqual(1, len(all_anon_urls))
        self.assertEqual('https://dk.pcpartpicker.com/list/ZqWwj2', all_anon_urls[0])

    def test_unpaired_urls_link_after_table(self):
        fp = '../tests/test-posts/link_after_table.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
        urls = elements['anon'] # No identifiable links
        unpaired_urls = get_urls_with_no_table(urls, elements['tables'])
    
        self.assertEqual(0, len(unpaired_urls))

    def test_unpaired_urls_two_link_one_unpaired(self):
        fp = '../tests/test-posts/three_link_one_unpaired.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
        
        urls = elements['anon']  # No identifiable links
        self.assertEqual(2, len(urls))
        
        unpaired_urls = get_urls_with_no_table(urls, elements['tables'])
        
        expected_url = "https://mx.pcpartpicker.com/list/ZGFq7X"
        self.assertEqual(1, len(unpaired_urls))
        self.assertEqual(expected_url, unpaired_urls[0])

    def test_unpaired_urls_unpaired_url_before_after(self):
        fp = '../tests/test-posts/unpaired_link_before_after.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
    
        urls = elements['anon']  # No identifiable links
        self.assertEqual(2, len(urls))
    
        unpaired_urls = get_urls_with_no_table(urls, elements['tables'])
    
        expected_url = "https://mx.pcpartpicker.com/list/ZGFq7X"
        self.assertEqual(1, len(unpaired_urls))
        self.assertEqual(expected_url, unpaired_urls[0])
        
    def test_unpaired_urls_table_iden_only(self):
        fp = '../tests/test-posts/table_iden_only.htm'
        text = read_file(fp)
    
        elements = detect_pcpp_html_elements(text)
        anon_urls = elements['anon']
        iden_urls = elements['identifiable']
        all_urls, iden_anon_urls = combine_iden_anon_urls(anon_urls, iden_urls, self.pcpp)
        
        self.assertEqual(1, len(all_urls))
        
        rem_urls = get_urls_with_no_table(all_urls, elements['tables'])
        
        self.assertEqual(0, len(rem_urls))
        
    def test_parse_submission_anon(self):
        fp = '../tests/test-posts/anon_link.htm'
        text = read_file(fp)
        pcpp = PCPPParser(self.f_handler)
        
        urls, iden_anon, table = parse_submission(text, '', pcpp)
        self.assertEqual(1, len(urls))
        self.assertEqual(0, len(iden_anon))
        self.assertEqual(0, table['total'])

    def test_parse_submission_iden(self):
        fp = '../tests/test-posts/iden_link.htm'
        text = read_file(fp)
        pcpp = PCPPParser(self.f_handler)
    
        urls, iden_anon, table = parse_submission(text, '', pcpp)
        self.assertEqual(1, len(urls))
        self.assertEqual(1, len(iden_anon))
        self.assertEqual(0, table['total'])

    def test_parse_submission_link_after_table(self):
        fp = '../tests/test-posts/iden_link.htm'
        text = read_file(fp)
        pcpp = PCPPParser(self.f_handler)
    
        urls, iden_anon, table = parse_submission(text, '', pcpp)
        self.assertEqual(1, len(urls))
        self.assertEqual(1, len(iden_anon))
        self.assertEqual(0, table['total'])

    def test_parse_submission_same_link_anon_iden(self):
        fp = '../tests/test-posts/same_anon_iden_links.htm'
        text = read_file(fp)
        pcpp = PCPPParser(self.f_handler)
    
        urls, iden_anon, table = parse_submission(text, '', pcpp)
        self.assertEqual(1, len(urls))
        self.assertEqual(1, len(iden_anon))
        self.assertEqual(0, table['total'])

    def test_parse_submission_table_broken(self):
        fp = '../tests/test-posts/table_broken.htm'
        text = read_file(fp)
        pcpp = PCPPParser(self.f_handler)
    
        urls, iden_anon, table = parse_submission(text, text, pcpp)
        self.assertEqual(1, len(urls))
        self.assertEqual(0, len(iden_anon))
        self.assertEqual(0, table['total'])
        self.assertTrue(table['bad_markdown'])

    def test_parse_submission_table_partial(self):
        fp = '../tests/test-posts/table_partial.htm'
        text = read_file(fp)
        pcpp = PCPPParser(self.f_handler)
    
        urls, iden_anon, table = parse_submission(text, text, pcpp)
        self.assertEqual(1, len(urls))
        self.assertEqual(0, len(iden_anon))
        self.assertEqual(1, table['total'])
        self.assertEqual(1, table['invalid'])
        self.assertTrue(table['bad_markdown'])

    def test_parse_submission_table_unfin_footer(self):
        fp = '../tests/test-posts/table_unfin_footer.htm'
        text = read_file(fp)
        pcpp = PCPPParser(self.f_handler)
    
        urls, iden_anon, table = parse_submission(text, '', pcpp)
        self.assertEqual(0, len(urls))
        self.assertEqual(0, len(iden_anon))
        self.assertEqual(1, table['total'])
        self.assertEqual(0, table['invalid'])
        self.assertEqual(1, table['valid'])
        self.assertFalse(table['bad_markdown'])

    def test_parse_submission_table_us(self):
        fp = '../tests/test-posts/table_us.htm'
        text = read_file(fp)
        pcpp = PCPPParser(self.f_handler)
    
        urls, iden_anon, table = parse_submission(text, '', pcpp)
        self.assertEqual(0, len(urls))
        self.assertEqual(0, len(iden_anon))
        self.assertEqual(1, table['total'])
        self.assertEqual(0, table['invalid'])
        self.assertEqual(1, table['valid'])
        self.assertFalse(table['bad_markdown'])

    def test_parse_submission_three_link_one_unpaired(self):
        fp = '../tests/test-posts/three_link_one_unpaired.htm'
        text = read_file(fp)
        pcpp = PCPPParser(self.f_handler)
    
        urls, iden_anon, table = parse_submission(text, '', pcpp)
        self.assertEqual(1, len(urls))
        self.assertEqual(1, len(iden_anon))
        self.assertEqual(1, table['total'])
        self.assertEqual(0, table['invalid'])
        self.assertEqual(1, table['valid'])
        self.assertFalse(table['bad_markdown'])


if __name__ == '__main__':
    unittest.main()
