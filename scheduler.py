import schedule
import sys
import time
import subprocess
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)

def run_autopost():
    """Function to run the Django management command using subprocess."""
    try:
        logging.info("Starting Django autopost command...")
        # Using the full path to the Python interpreter in the virtual environment
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        python_path = os.path.join(os.getcwd(), 'env', 'Scripts', 'python.exe')
        if not os.path.exists(python_path):
            python_path = sys.executable
        cmd = [python_path, "manage.py", "autopost"]
        
        if str(env.get("SKIP_POST", "")).lower() in ("1", "true", "yes"):
            cmd.append("--skip-post")
            
        logging.info(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            cwd=os.path.join(os.getcwd(), 'myproject'),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            env=env,
        )
        
        # Log all output for debugging
        logging.info(f"Command return code: {result.returncode}")
        if result.stdout:
            logging.info(f"Command output:\n{result.stdout}")
        if result.stderr:
            logging.error(f"Command error:\n{result.stderr}")
            
        if result.returncode == 0:
            logging.info("Django autopost command executed successfully")
            return True
        else:
            error_msg = result.stderr if result.stderr else "No error details available"
            logging.error(f"Django autopost command failed with error: {error_msg}")
            return False
            
    except Exception as e:
        logging.error(f"Error running autopost script: {str(e)}", exc_info=True)
        return False

def run_autopost_image():
    try:
        logging.info("Starting Django autopost_image command...")
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        python_path = os.path.join(os.getcwd(), 'env', 'Scripts', 'python.exe')
        if not os.path.exists(python_path):
            python_path = sys.executable
        cmd = [python_path, "manage.py", "autopost_image"]
        if str(env.get("SKIP_POST", "")).lower() in ("1", "true", "yes"):
            cmd.append("--skip-post")
        logging.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            cwd=os.path.join(os.getcwd(), 'myproject'),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            env=env,
        )
        logging.info(f"Command return code: {result.returncode}")
        if result.stdout:
            logging.info(f"Command output:\n{result.stdout}")
        if result.stderr:
            logging.error(f"Command error:\n{result.stderr}")
        if result.returncode == 0:
            logging.info("Django autopost_image command executed successfully")
            return True
        logging.error("Django autopost_image command failed")
        return False
    except Exception as e:
        logging.error(f"Error running autopost_image script: {str(e)}", exc_info=True)
        return False

def main():
    logging.info("Starting scheduler...")
    
    # Schedule the jobs
    reel_time = os.environ.get("REEL_SCHEDULE_TIME")
    photo_time = os.environ.get("PHOTO_SCHEDULE_TIME")
    custom_time = os.environ.get("SCHEDULE_TIME")

    def _apply_times(var_value, label, func):
        times = [t.strip() for t in (var_value or "").split(",") if t.strip()]
        for t in times:
            logging.info(f"{label} schedule set: {t}")
            schedule.every().day.at(t).do(func)

    if reel_time:
        _apply_times(reel_time, "Reel", run_autopost)
    if photo_time:
        _apply_times(photo_time, "Photo", run_autopost_image)
    if not (reel_time or photo_time):
        if custom_time:
            schedule.every().day.at(custom_time).do(run_autopost)
        else:
            test_flag = os.environ.get("SCHEDULER_TEST") or os.environ.get("TEST_MODE")
            if str(test_flag or "").lower() in ("1", "true", "yes"):
                logging.info("TEST MODE: Scheduler running every 1 minute.")
                schedule.every(1).minutes.do(run_autopost)
                schedule.every(1).minutes.do(run_autopost_image)
            else:
                schedule.every().day.at("10:00").do(run_autopost)
                schedule.every().day.at("15:00").do(run_autopost_image)
                schedule.every().day.at("20:00").do(run_autopost)
    
    logging.info("Scheduler started. Press Ctrl+C to exit.")
    logging.info("Scheduled times: 10:00 AM, 3:00 PM, 8:00 PM")
    
    run_on_start = os.environ.get("RUN_ON_START")
    if str(run_on_start or "").lower() in ("1", "true", "yes"):
        run_autopost()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user")
    except Exception as e:
        logging.error(f"Scheduler encountered an error: {str(e)}")
        raise
