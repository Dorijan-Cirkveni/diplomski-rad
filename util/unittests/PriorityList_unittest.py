import unittest
from util.struct.PriorityList import PriorityList

class TestPriorityList(unittest.TestCase):
    def test_add(self):
        plist = PriorityList()
        plist.add(3, 'value1')
        plist.add(5, 'value2')
        plist.add(3, 'value3')
        self.assertEqual(plist.allValues, {3: ['value1', 'value3'], 5: ['value2']})

    def test_popLowerThan(self):
        plist = PriorityList()
        plist.add(3, 'value1')
        plist.add(5, 'value2')
        plist.add(3, 'value3')
        self.assertEqual(plist.popLowerThan(4), [(3, ['value1', 'value3'])])

if __name__ == '__main__':
    unittest.main()
