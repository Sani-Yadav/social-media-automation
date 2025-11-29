import os
import time
import unittest
from unittest.mock import patch, MagicMock
from scheduler import run_autopost, main
import schedule
import schedule

class TestScheduler(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.original_env = os.environ.copy()
        os.environ.update({
            'TEST_MODE': 'true',
            'SKIP_POST': 'true',
            'PYTHONIOENCODING': 'utf-8',
            'RUN_ON_START': 'true'
        })
        
    @patch('subprocess.run')
    def test_run_autopost_success(self, mock_run):
        """Test successful autopost execution"""
        print("\n🔍 Testing successful autopost...")
        # Mock subprocess.run to return success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Test output"
        mock_run.return_value.stderr = ""
        
        result = run_autopost()
        self.assertTrue(result)
        print("✅ Success test passed")
    
    @patch('subprocess.run')
    def test_run_autopost_failure(self, mock_run):
        """Test failed autopost execution"""
        print("\n❌ Testing failed autopost...")
        # Mock subprocess.run to return failure
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Test error"
        
        result = run_autopost()
        self.assertFalse(result)
        print("✅ Failure test passed")
        
    def test_test_mode_scheduling(self):
        """Test job scheduling in test mode"""
        print("\n⏰ Testing job scheduling in test mode...")
        # In test mode, the scheduler should run every minute
        # We'll test this by checking the environment variable
        os.environ['TEST_MODE'] = 'true'
        
        # Clear any existing jobs
        schedule.clear()
        
        # The main function will set up the scheduling
        with patch('schedule.every') as mock_every:
            with patch('schedule.run_pending'):
                with patch('time.sleep', side_effect=KeyboardInterrupt):
                    main()
        
        # In test mode, should have scheduled to run every minute
        mock_every.assert_called_with(1)
        print("✅ Test mode scheduling passed")
        
    def test_production_mode_scheduling(self):
        """Test job scheduling in production mode"""
        print("\n🏭 Testing job scheduling in production mode...")
        # Switch to production mode
        os.environ['TEST_MODE'] = 'false'
        
        # Clear any existing jobs
        schedule.clear()
        
        # The main function will set up the scheduling
        with patch('schedule.every') as mock_every:
            with patch('schedule.run_pending'):
                with patch('time.sleep', side_effect=KeyboardInterrupt):
                    main()
        
        # In production mode, should have called every().day.at() 3 times
        self.assertGreaterEqual(mock_every.return_value.day.at.call_count, 3)
        print("✅ Production mode scheduling passed")
    
    @patch('scheduler.run_autopost')
    @patch('schedule.every')
    @patch('schedule.run_pending')
    @patch('time.sleep')
    def test_main_function(self, mock_sleep, mock_run_pending, mock_every, mock_run_autopost):
        """Test the main function"""
        print("\n🚀 Testing main function...")
        # Mock run_autopost to return True
        mock_run_autopost.return_value = True
        
        # Mock schedule methods
        mock_job = MagicMock()
        mock_every.return_value = mock_job
        
        # Make sleep raise KeyboardInterrupt on first call
        mock_sleep.side_effect = KeyboardInterrupt()
        
        # Run the main function
        main()
        
        # Verify run_autopost was called if RUN_ON_START is true
        if os.environ.get('RUN_ON_START', '').lower() in ('1', 'true', 'yes'):
            mock_run_autopost.assert_called_once()
        
        # Verify run_pending was called at least once
        mock_run_pending.assert_called()
        
        print("✅ Main function test passed")
        
    def tearDown(self):
        """Clean up"""
        schedule.clear()
        os.environ.clear()
        os.environ.update(self.original_env)

if __name__ == "__main__":
    # Set up test environment first
    import setup_test_env
    setup_test_env.setup_test_environment()
    
    # Run tests
    unittest.main()
