# Gelin Eguinosa Rosique

import unittest
from papers import _number_to_3digits


class NumberToDigitsTestCase(unittest.TestCase):
    """
    Test for '_number_to3digits'
    """

    def test_one_digit_number(self):
        """
        Test the function when it receives a number with only one digit.
        """
        result = _number_to_3digits(3)
        self.assertEqual(result, '003')

    def test_two_digit_number(self):
        """
        Test the function when it receives a number with two digits.
        """
        result = _number_to_3digits(83)
        self.assertEqual(result, '083')

    def test_three_digit_number(self):
        """
        Test the function when it receives a number with 3 digits.
        """
        result = _number_to_3digits(837)
        self.assertEqual(result, '837')


if __name__ == '__main__':
    unittest.main()
