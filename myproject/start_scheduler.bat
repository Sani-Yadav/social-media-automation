@echo off
cd /d %~dp0
call .\env\Scripts\activate.bat
echo Starting InvisiPost Scheduler in TEST MODE (posts every minute)
echo Check scheduler.log for detailed logs
set SCHEDULER_TEST=1
set SKIP_POST=1
set RUN_ON_START=1
set REEL_SCHEDULE_TIME=06:00,17:00
set PHOTO_SCHEDULE_TIME=12:00
python scheduler.py
pause
