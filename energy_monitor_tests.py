import unittest
from energy_monitor import EnergyMonitor
from energy_monitor import *
import tkinter as tk
import datetime
from os import path

class TestBasicLoading(unittest.TestCase):

    def test_initial(self):
        print('Testing the loading methods')

        self.assertIsNotNone(self.gui)
        self.assertIsInstance(self.gui, EnergyMonitor)


    def test_badfiles(self):
        print("Testing for bad file types")

        # Currently this test fails, because this file actually does exist. How could you change the
        # tests so they do actually test what they're supposed to?
        with self.assertRaises(ValueError):
            self.gui.load_file(self.working_dir + '\\resources\\test1_both_daily.csv')


    def test_correctload(self):
        print("Testing that when a correct file is used the data is populated correctly")

        self.gui.load_file(self.working_dir + '\\resources\\test1_both_daily.csv')

        self.assertEqual(len(self.gui.loaded_ids), 1)
        self.assertEqual(self.gui.loaded_ids[0], 'test1')

        self.assertEqual(len(self.gui.loaded_fuels), 2)

        self.assertEqual(len(list(self.gui.data_container.keys())), 4)
        first_date = datetime.date(2016, 1, 1)
        self.assertEqual(list(self.gui.data_container.keys())[0], first_date)

    def setUp(self):
        self.root = tk.Tk()
        self.gui = EnergyMonitor(self.root)
        self.working_dir = path.dirname(path.abspath(__file__))



if __name__ == '__main__':
    unittest.main()
