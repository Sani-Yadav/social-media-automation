# SocialBot — Automated Instagram Posting Bot
Live : https://socialbot-1.onrender.com

SocialBot is an automated Instagram posting system that generates and publishes images and reels on a schedule.

**Features**
- Automatic posting of images and reels to Instagram using `myapp.auto_post`.
- Scheduled posting three times a day (India / Asia-Kolkata timezone):
  - 09:30 IST — Reel (video)
  - 15:00 IST — Image post
  - 20:00 IST — Reel + Image
- Retries network failures with exponential backoff.
- Logs API responses and errors for every upload.
- Archives posted media automatically into `archived/` subfolders.

**Repository layout (key files)**
- `instagram_scheduler.py` — Scheduler and uploader (schedules jobs, selects media, performs uploads, archives posted files).
- `myproject/myapp/auto_post.py` — Media generation and actual Instagram upload helpers (uses `instagrapi`).
- `scheduler_state.json` — Scheduler state (next-run timestamps, stored in UTC).
- `content/images/` and `content/videos/` — Default media folders (see configuration).

## Quickstart (Windows PowerShell)
1. Clone repository and change into project folder (if not already):

```powershell
cd D:\InvisiPost
```

2. Create and activate a Python virtual environment (Windows PowerShell):

```powershell
python -m venv env
# Activate
.\env\Scripts\Activate.ps1
```

(If using Command Prompt use `env\Scripts\activate.bat`.)

3. Install dependencies (use the project's `requirements.txt` if present):

```powershell
pip install -r myproject/requirements.txt
# or, if you don't have a requirements file, at minimum install instagrapi:
pip install instagrapi pytz
```

4. Configure credentials and keys
- Edit `myproject/myapp/config.py` (or set environment variables) to include:
  - `INSTAGRAM_USERNAME`
  - `INSTAGRAM_PASSWORD`
  - Any API keys required by your content generation (e.g., Groq, Unsplash keys)

5. Prepare content folders (defaults used by scheduler):
- Images: `D:\InvisiPost\content\images` (or `content/images/` inside repo)
- Videos: `D:\InvisiPost\content\videos`

Create folders if they do not exist. Posted files will be moved to `archived/` inside these folders.

## Running the Scheduler
- Run once (execute any jobs that are due now and exit):

```powershell
# From D:\InvisiPost
& .\env\Scripts\python.exe instagram_scheduler.py --once
```

- Run continuously (keeps the scheduler running):

```powershell
& .\env\Scripts\python.exe instagram_scheduler.py
```

## Environment configuration (optional)
You may set environment variables to override defaults:
- `IMAGES_DIR` — path to images folder (default: `D:/InvisiPost/content/images`)
- `VIDEOS_DIR` — path to videos folder (default: `D:/InvisiPost/content/videos`)
- `SCHEDULE_TZ` — timezone (default: `Asia/Kolkata`)

Example (PowerShell):

```powershell
$env:IMAGES_DIR = 'D:\InvisiPost\content\images'
$env:VIDEOS_DIR = 'D:\InvisiPost\content\videos'
```

## Logs & State
- Scheduler logs to `scheduler.log` (configured in `instagram_scheduler.py`) and also prints to stdout.
- `scheduler_state.json` stores the next-run UTC times for each job. Do not delete this file if you want the scheduler to preserve its schedule between restarts.

## Implementation notes
- The scheduler computes times in IST (Asia/Kolkata), converts to UTC for storage and comparisons, and schedules the next run at the same local time the following day.
- The scheduler selects media files randomly from the configured folders. After a successful upload the file is moved into `<folder>/archived/` to avoid reposts.
- Upload functions in `myapp.auto_post` return structured responses so that the scheduler can log API responses and implement retry logic.

## Disclaimer — Instagram automation risks
- Automating posting to Instagram may violate Instagram's Terms of Use and can trigger account restrictions or bans, especially for repeat/automated behavior.
- Use at your own risk. Test thoroughly with a non-production account first.
- Ensure 2FA, suspicious login alerts, and session management are handled (the `instagrapi` client may fail if these are not addressed).

## Suggested next steps / safety improvements
- Implement a database or CSV history for posted media to avoid accidental duplicates.
- Add rate limiting and randomized posting times (small offsets) to mimic human behavior.
- Add monitoring/alerts (email, Slack) for persistent failures or account issues.

If you want, I can also:
- Add a `--dry-run` mode back for safe testing (simulate uploads without posting),
- Add a `--project-root` flag so the scheduler imports the project explicitly, or
- Implement archival policies (timestamped folders, move-to-remote storage).

---
SocialBot — automated Instagram posting. Use responsibly.
