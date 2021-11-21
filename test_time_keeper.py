# Gelin Eguinosa Rosique

import unittest
import time
from time_keeper import TimeKeeper

class TestTimeKeeper(unittest.TestCase):
    """
    Test the class TimeKeeper to check it measures the time segments properly.    
    """

    def setUp(self) -> None:
        """
        Set up the variables we are going to use in the test units.
        """
        self.start_time = time.time()
        self.stopwatch = TimeKeeper()

    def test_pause(self):
        """
        Test the class works properly when pausing the timer.
        """
        # Check the timer is running before pausing.
        self.assertEqual(self.stopwatch.current_state, 'running')

        # Get the current time before pausing.
        current_time = time.time()
        # Pause the timer, and check is paused.
        self.stopwatch.pause()
        self.assertEqual(self.stopwatch.current_state, 'paused')

        # Test the value of the runtime of the timer
        current_runtime = self.stopwatch.total_runtime()
        test_runtime = current_time - self.start_time
        self.assertAlmostEqual(current_runtime, test_runtime, 2)

        # Test the runtime stays the same after sleeping for a while.
        time.sleep(3)
        self.assertEqual(current_runtime, self.stopwatch.total_runtime())

    def test_restart(self):
        """
        Test the restart method of the class
        """
        # Check if the timer is running.
        self.assertEqual(self.stopwatch.current_state, 'running')
        # Run the timer for a little bit.
        time.sleep(2)
        # Check we have at least 2 seconds of runtime.
        self.assertGreater(self.stopwatch.total_runtime(), 2)

        # Reset the timer.
        self.stopwatch.restart()
        # Check the the timer is almost 0 (smaller than 0.005)
        self.assertAlmostEqual(0, self.stopwatch.total_runtime(), 2)


if __name__ == '__main__':
    # Run the test for the 'TimeKeeper' class
    unittest.main()
