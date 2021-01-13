import unittest
from pcpp.pcpartpickerlist import PCPartPickerList


class MyTestCase(unittest.TestCase):
    
    def setUp(self):
        self.test_pages = [('../test-pages/page_one.htm', '../tests/expected/page_one_part_list.txt'),
                           ('../test-pages/page_two.htm', '../tests/expected/page_two_part_list.txt')]
    
    def test_request_page_data_valid(self):
        pcpp = PCPartPickerList()
        test_url = 'https://pcpartpicker.com/list/HQzZgJ'
        html_doc = pcpp.request_page_data(test_url)
        self.assertIsNotNone(html_doc)
        
    def test_request_page_data_invalid(self):
        pcpp = PCPartPickerList()
        test_url = 'https://pcpartpicker.com/list/abc123'
        html_doc = pcpp.request_page_data(test_url)
        self.assertIsNone(html_doc)

    def test_parse_local_pages(self):
        for local, expected in self.test_pages:
            # TODO: Need a new object per list, should make it only a parser?
            pcpp = PCPartPickerList()
            pcpp.set_local()
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
            


if __name__ == '__main__':
    unittest.main()
