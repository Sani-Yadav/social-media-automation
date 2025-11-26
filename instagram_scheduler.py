"""Timezone-aware scheduler for Instagram autopost.

Run:
  - Dry run once:
      python instagram_scheduler.py --once --dry-run

Notes:
  - This script will try to add the `myproject` folder (next to this file)
    to `sys.path` so `import myapp.auto_post` succeeds.
  - `--dry-run` simulates media creation/upload (no network / no Instagram calls).
  - Scheduling uses IST (Asia/Kolkata) and stores next-run in UTC in `scheduler_state.json`.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from argparse import ArgumentParser
from datetime import datetime, timedelta
from pathlib import Path
import importlib
import pytz
import random
import shutil
import math

LOG_FILE = os.getenv("SCHEDULER_LOG", "scheduler.log")
STATE_FILE = os.getenv("STATE_FILE", "scheduler_state.json")
SCHEDULE_TZ = os.getenv("SCHEDULE_TZ", "Asia/Kolkata")
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "15:00")  # default 15:00 IST

# Default 3 daily jobs (IST times). Format: (job_id, HH:MM, job_type)
DEFAULT_JOBS = [
    ("slot_1", "09:30", "any"),
    ("slot_2", "15:00", "any"),
    ("slot_3", "20:00", "any"),
]


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
    )


def ensure_project_on_path():
    """If `myproject` folder exists next to this script, add it to sys.path so `myapp` is importable."""
    script_dir = Path(__file__).resolve().parent
    candidate = script_dir / "myproject"
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
        logging.info("Added project path to sys.path: %s", candidate)


def import_autopost():
    """Import and return (module, main_fn). Returns (None, None) on failure."""
    try:
        module = importlib.import_module("myapp.auto_post")
        main_fn = getattr(module, "main", None)
        return module, main_fn
    except Exception as exc:
        logging.warning("Import myapp.auto_post failed: %s", exc)
        return None, None


def load_state(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def save_state(path: str, state: dict) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)


def parse_time_hhmm(value: str) -> tuple[int, int]:
    parts = value.split(":")
    if len(parts) != 2:
        raise ValueError("Invalid time format; expected HH:MM")
    return int(parts[0]), int(parts[1])


def compute_next_run(tz: pytz.BaseTzInfo, hour: int, minute: int) -> datetime:
    now = datetime.now(tz)
    candidate = tz.localize(datetime(now.year, now.month, now.day, hour, minute, 0))
    if candidate <= now:
        candidate = candidate + timedelta(days=1)
    return candidate


def main_loop(run_once: bool = False, jobs: list | None = None):
    tz = pytz.timezone(SCHEDULE_TZ)

    # jobs: list of (job_id, 'HH:MM', job_type)
    jobs = jobs or DEFAULT_JOBS

    # Validate no duplicate times
    times = [t for (_id, t, _type) in jobs]
    if len(times) != len(set(times)):
        raise RuntimeError("Duplicate scheduled times found in jobs - ensure times are unique to avoid simultaneous posts.")

    # Ensure project path is available for imports
    ensure_project_on_path()

    # Import autopost module now; require it for live posting
    autopost_mod, autopost_main = import_autopost()
    if autopost_mod is None:
        # Try adding explicit absolute project root if available
        project_root = Path(r"D:/InvisiPost/myproject")
        if project_root.exists() and str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
            logging.info("Added explicit project root to sys.path: %s", project_root)
            autopost_mod, autopost_main = import_autopost()

    if autopost_mod is None:
        logging.error("Critical: cannot import myapp.auto_post from project path. Exiting to avoid missed or unsafe behavior.")
        return

    # Content folders (absolute paths as requested)
    images_dir = Path(os.getenv("IMAGES_DIR", r"D:/InvisiPost/content/images"))
    reels_dir = Path(os.getenv("VIDEOS_DIR", r"D:/InvisiPost/content/videos"))

    # Load per-job persisted state: {job_id: iso-utc}
    state = load_state(STATE_FILE) or {}
    job_next = {}

    for job_id, hhmm, job_type in jobs:
        stored = state.get(job_id)
        if stored:
            try:
                job_next_dt = datetime.fromisoformat(stored).astimezone(pytz.UTC)
            except Exception:
                job_next_dt = None
        else:
            job_next_dt = None

        if not job_next_dt:
            h, m = parse_time_hhmm(hhmm)
            cand_local = compute_next_run(tz, h, m)
            job_next_dt = cand_local.astimezone(pytz.UTC)
            state[job_id] = job_next_dt.isoformat()

        job_next[job_id] = {"next_run_utc": job_next_dt, "hhmm": hhmm, "type": job_type}

    # Persist initial state
    save_state(STATE_FILE, {k: v["next_run_utc"].isoformat() for k, v in job_next.items()})

    logging.info("Scheduler started. Jobs: %s", ", ".join([f"%s@%s" % (j, job_next[j]['hhmm']) for j in job_next]))

    try:
        while True:
            now_utc = datetime.now(pytz.UTC)
            for job_id, meta in list(job_next.items()):
                nxt = meta["next_run_utc"]
                if now_utc >= nxt:
                    local_time = nxt.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
                    logging.info("Executing job %s. Scheduled: %s, Executed: %s", job_id, meta["hhmm"], local_time)

                    # Choose content: randomly select image or reel if both available
                    chosen_type = None
                    chosen_path = None
                    try:
                        image_files = []
                        reel_files = []
                        if images_dir.exists():
                            image_files = [p for p in images_dir.iterdir() if p.is_file()]
                        if reels_dir.exists():
                            reel_files = [p for p in reels_dir.iterdir() if p.is_file()]

                        # Prefer reels if available else images; if both, choose randomly
                        if reel_files and image_files:
                            chosen = random.choice(["reel", "image"])
                        elif reel_files:
                            chosen = "reel"
                        elif image_files:
                            chosen = "image"
                        else:
                            chosen = None

                        if chosen == "reel":
                            chosen_path = str(random.choice(reel_files))
                            chosen_type = "reel"
                        elif chosen == "image":
                            chosen_path = str(random.choice(image_files))
                            chosen_type = "image"
                        else:
                            logging.error("No media files found in %s or %s — skipping job %s", images_dir, reels_dir, job_id)

                        # Perform upload with retries and archiving on success
                        def upload_with_retries(func, args=(), kwargs=None, max_attempts=4, base_delay=5):
                            kwargs = kwargs or {}
                            attempt = 0
                            while attempt < max_attempts:
                                try:
                                    attempt += 1
                                    resp = func(*args, **kwargs)
                                    # Some functions return dict with ok key; otherwise treat non-exception as success
                                    if isinstance(resp, dict):
                                        if resp.get("ok"):
                                            return True, resp
                                        else:
                                            # treat as failure and possibly retry
                                            logging.warning("Upload attempt %d returned error: %s", attempt, resp)
                                            # if last attempt, return failure
                                    else:
                                        return True, {"ok": True, "response": resp}
                                except Exception as exc:
                                    logging.exception("Upload attempt %d raised exception", attempt)
                                # exponential backoff before next attempt
                                delay = base_delay * (2 ** (attempt - 1))
                                jitter = random.uniform(0, 1)
                                sleep_time = delay + jitter
                                logging.info("Retrying in %.1f seconds...", sleep_time)
                                time.sleep(sleep_time)
                            return False, {"ok": False, "error": "Max attempts reached"}

                        if chosen_type == "reel":
                            logging.info("Posting reel: %s", chosen_path)
                            success, result = upload_with_retries(autopost_mod.post_instagram, args=(chosen_path,))
                            if success:
                                logging.info("Reel posted successfully: %s; response=%s", chosen_path, result)
                                # archive
                                try:
                                    archived = reels_dir / "archived"
                                    archived.mkdir(parents=True, exist_ok=True)
                                    dest = archived / Path(chosen_path).name
                                    shutil.move(chosen_path, dest)
                                    logging.info("Archived reel to %s", dest)
                                except Exception:
                                    logging.exception("Failed to archive reel %s", chosen_path)
                            else:
                                logging.error("Failed to post reel %s; result=%s", chosen_path, result)

                        elif chosen_type == "image":
                            # generate caption if available
                            try:
                                caption = autopost_mod.generate_tech_script()
                            except Exception:
                                caption = ""
                            logging.info("Posting image: %s (caption len=%d)", chosen_path, len(caption))
                            success, result = upload_with_retries(autopost_mod.post_instagram_image, args=(caption, chosen_path))
                            if success:
                                logging.info("Image posted successfully: %s; response=%s", chosen_path, result)
                                # archive
                                try:
                                    archived = images_dir / "archived"
                                    archived.mkdir(parents=True, exist_ok=True)
                                    dest = archived / Path(chosen_path).name
                                    shutil.move(chosen_path, dest)
                                    logging.info("Archived image to %s", dest)
                                except Exception:
                                    logging.exception("Failed to archive image %s", chosen_path)
                            else:
                                logging.error("Failed to post image %s; result=%s", chosen_path, result)

                    except Exception as e:
                        logging.exception("Unexpected error while selecting/posting media for job %s: %s", job_id, e)

                    # schedule next run for this job (same local time next day)
                    next_local = (meta["next_run_utc"].astimezone(tz) + timedelta(days=1)).replace(tzinfo=tz)
                    next_utc = next_local.astimezone(pytz.UTC)
                    job_next[job_id]["next_run_utc"] = next_utc
                    # persist
                    persisted = {k: v["next_run_utc"].isoformat() for k, v in job_next.items()}
                    save_state(STATE_FILE, persisted)
                    logging.info("Next run for %s scheduled (UTC): %s", job_id, next_utc.isoformat())

                    if run_once:
                        logging.info("Run-once flag set — exiting after executing jobs due now.")
                        return

            time.sleep(20)
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user.")


if __name__ == "__main__":
    parser = ArgumentParser(description="Instagram autopost scheduler")
    parser.add_argument("--once", action="store_true", help="Run the scheduled job once and exit")
    args = parser.parse_args()

    setup_logging()
    logging.info("Using schedule time %s (%s)", SCHEDULE_TIME, SCHEDULE_TZ)
    main_loop(run_once=args.once)
