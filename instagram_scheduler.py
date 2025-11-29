"""Timezone-aware scheduler for Instagram autopost.

Run:
  - Dry run once:
      python instagram_scheduler.py --once --dry-run
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

LOG_FILE = os.getenv("SCHEDULER_LOG", "scheduler.log")
STATE_FILE = os.getenv("STATE_FILE", "scheduler_state.json")
SCHEDULE_TZ = os.getenv("SCHEDULE_TZ", "Asia/Kolkata")
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "15:00")

DEFAULT_JOBS = [
    ("slot_1", "09:30", "any"),
    ("slot_2", "15:00", "any"),
    ("slot_3", "20:00", "any"),
]


# ---------------------------------------------------------------------------
# Setup Logging
# ---------------------------------------------------------------------------
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
    )


# ---------------------------------------------------------------------------
# Ensure project on path
# ---------------------------------------------------------------------------
def ensure_project_on_path():
    """Add myproject/ folder (next to script) to sys.path if exists"""
    script_dir = Path(__file__).resolve().parent
    candidate = script_dir / "myproject"
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
        logging.info("Added project path to sys.path: %s", candidate)


# ---------------------------------------------------------------------------
# Import autopost module
# ---------------------------------------------------------------------------
def import_autopost():
    try:
        module = importlib.import_module("myapp.auto_post")
        main_fn = getattr(module, "main", None)
        return module, main_fn
    except Exception as exc:
        logging.warning("Import myapp.auto_post failed: %s", exc)
        return None, None


# ---------------------------------------------------------------------------
# State handling
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Time parsing helpers
# ---------------------------------------------------------------------------
def parse_time_hhmm(value: str) -> tuple[int, int]:
    parts = value.split(":")
    return int(parts[0]), int(parts[1])


def compute_next_run(tz: pytz.BaseTzInfo, hour: int, minute: int) -> datetime:
    now = datetime.now(tz)
    candidate = tz.localize(datetime(now.year, now.month, now.day, hour, minute))
    if candidate <= now:
        candidate += timedelta(days=1)
    return candidate


# ---------------------------------------------------------------------------
# Main scheduler loop
# ---------------------------------------------------------------------------
def main_loop(run_once: bool = False, dry_run: bool = False, jobs: list | None = None):
    tz = pytz.timezone(SCHEDULE_TZ)
    jobs = jobs or DEFAULT_JOBS

    ensure_project_on_path()
    autopost_mod, autopost_main = import_autopost()

    # fallback path
    if autopost_mod is None:
        project_root = Path(r"D:/InvisiPost/myproject")
        if project_root.exists() and str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
            logging.info("Added fallback project root to sys.path: %s", project_root)
            autopost_mod, autopost_main = import_autopost()

    if autopost_mod is None:
        logging.error("Cannot import myapp.auto_post. Exiting safely.")
        return

    # content folders
    images_dir = Path(os.getenv("IMAGES_DIR", r"D:/InvisiPost/content/images"))
    reels_dir = Path(os.getenv("VIDEOS_DIR", r"D:/InvisiPost/content/videos"))

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

        job_next[job_id] = {
            "next_run_utc": job_next_dt,
            "hhmm": hhmm,
            "type": job_type,
        }

    save_state(STATE_FILE, {k: v["next_run_utc"].isoformat() for k, v in job_next.items()})

    logging.info("Scheduler started. Jobs: %s",
                 ", ".join([f"{j}@{job_next[j]['hhmm']}" for j in job_next]))

    try:
        while True:
            now_utc = datetime.now(pytz.UTC)

            for job_id, meta in job_next.items():
                nxt = meta["next_run_utc"]

                if now_utc >= nxt:
                    local_time = nxt.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S %Z")
                    logging.info("Running job %s (scheduled: %s, local: %s)",
                                 job_id, meta["hhmm"], local_time)

                    # choose content
                    image_files = list(images_dir.glob("*")) if images_dir.exists() else []
                    reel_files = list(reels_dir.glob("*")) if reels_dir.exists() else []

                    chosen_type = None
                    chosen_path = None

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

                    if not chosen_type:
                        logging.error("No media found; skipping job %s", job_id)
                    else:
                        # -----------------------------
                        # DRY RUN SUPPORT ADDED HERE
                        # -----------------------------
                        if dry_run:
                            logging.info("[DRY RUN] Would post %s: %s", chosen_type, chosen_path)
                        else:
                            # real posting
                            try:
                                if chosen_type == "reel":
                                    logging.info("Posting reel: %s", chosen_path)
                                    autopost_mod.post_instagram(chosen_path)

                                elif chosen_type == "image":
                                    try:
                                        caption = autopost_mod.generate_tech_script()
                                    except Exception:
                                        caption = ""
                                    logging.info("Posting image: %s", chosen_path)
                                    autopost_mod.post_instagram_image(caption, chosen_path)

                            except Exception as e:
                                logging.exception("Upload failed: %s", e)

                    # schedule for next day
                    next_local = nxt.astimezone(tz) + timedelta(days=1)
                    next_local = tz.localize(
                        datetime(next_local.year, next_local.month, next_local.day,
                                 int(meta["hhmm"].split(":")[0]),
                                 int(meta["hhmm"].split(":")[1]))
                    )
                    next_utc = next_local.astimezone(pytz.UTC)

                    job_next[job_id]["next_run_utc"] = next_utc
                    save_state(STATE_FILE, {k: v["next_run_utc"].isoformat() for k, v in job_next.items()})

                    if run_once:
                        logging.info("Run-once enabled. Exiting.")
                        return

            time.sleep(20)

    except KeyboardInterrupt:
        logging.info("Scheduler stopped.")


# ---------------------------------------------------------------------------
# CLI ENTRY
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = ArgumentParser(description="Instagram autopost scheduler")
    parser.add_argument("--once", action="store_true", help="Run only one cycle then exit")
    parser.add_argument("--dry-run", action="store_true", help="Simulate run without uploading")
    args = parser.parse_args()

    setup_logging()
    logging.info("Scheduler using timezone: %s", SCHEDULE_TZ)

    main_loop(run_once=args.once, dry_run=args.dry_run)
