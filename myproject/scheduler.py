import schedule
import sys
import time
import subprocess
import logging
import os
from pathlib import Path

# ---------------------------------------------------------
# LOGGING SETUP
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scheduler.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logging.info("Scheduler script loaded...")

# ---------------------------------------------------------
# PATH SETUP
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR / "myproject"
MANAGE_PY = PROJECT_DIR / "manage.py"

# Auto-detect Python
PYTHON_BIN = BASE_DIR / "env" / "Scripts" / "python.exe"
if not PYTHON_BIN.exists():
    PYTHON_BIN = sys.executable  # fallback

logging.info(f"Using Python: {PYTHON_BIN}")
logging.info(f"Using manage.py: {MANAGE_PY}")

# ---------------------------------------------------------
# FUNCTION TO RUN DJANGO COMMAND
# ---------------------------------------------------------
def run_command(cmd_name):
    try:
        logging.info(f"→ Starting command: {cmd_name}")
        
        cmd = [str(PYTHON_BIN), str(MANAGE_PY), cmd_name]

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["LANG"] = "en_US.UTF-8"

        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env
        )

        if result.stdout:
            logging.info(f"OUTPUT:\n{result.stdout}")
        if result.stderr:
            logging.error(f"ERROR:\n{result.stderr}")

        if result.returncode == 0:
            logging.info(f"✔ {cmd_name} executed successfully")
        else:
            logging.error(f"✖ {cmd_name} failed")

    except Exception as e:
        logging.error(f"Exception while running {cmd_name}: {str(e)}", exc_info=True)


def run_autopost():
    run_command("autopost")


def run_autopost_image():
    run_command("autopost_image")


# ---------------------------------------------------------
# SCHEDULER SETUP
# ---------------------------------------------------------
logging.info("Configuring scheduler times...")

# Environment variables
reel_time = os.getenv("REEL_SCHEDULE_TIME")  # e.g., "10:00,20:00"
photo_time = os.getenv("PHOTO_SCHEDULE_TIME")
custom_time = os.getenv("SCHEDULE_TIME")
test_mode = os.getenv("TEST_MODE")
run_on_start = os.getenv("RUN_ON_START")

def apply_times(time_str, label, func):
    if not time_str:
        return
    times = [t.strip() for t in time_str.split(",") if t.strip()]
    for t in times:
        logging.info(f"{label} scheduled at {t}")
        schedule.every().day.at(t).do(func)

# Apply schedules
apply_times(reel_time, "Reel posting", run_autopost)
apply_times(photo_time, "Photo posting", run_autopost_image)

# Test mode (every 1 minute)
if str(test_mode).lower() in ("1", "true", "yes"):
    logging.info("TEST_MODE ON → Running every 1 minute")
    schedule.every(1).minutes.do(run_autopost)
    schedule.every(1).minutes.do(run_autopost_image)

# Default times
if not (reel_time or photo_time or test_mode):
    logging.info("Using default times")
    schedule.every().day.at("10:00").do(run_autopost)
    schedule.every().day.at("15:00").do(run_autopost_image)
    schedule.every().day.at("20:00").do(run_autopost)

# Run on start
if str(run_on_start).lower() in ("1", "true", "yes"):
    logging.info("RUN_ON_START enabled → Executing immediately")
    run_autopost()
    run_autopost_image()

logging.info("Scheduler Started ✓ Ready to Run!")


# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    logging.info("Scheduler stopped by user")
except Exception as e:
    logging.error(f"Scheduler encountered an error: {str(e)}", exc_info=True)
