#!/usr/bin/env python3

import argparse
import sys
import time
import itertools
import threading
import contextlib
import os

from insta_collect.scraper import scrape_hashtag
from insta_collect.saver import save_data


PREVIEW_LIMIT = 5


# ================= SPINNER =================
def spinner_task(message, stop_event):
    spinner = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    while not stop_event.is_set():
        sys.stdout.write(f"\r{message} {next(spinner)}")
        sys.stdout.flush()
        time.sleep(0.1)

    sys.stdout.write(f"\r{message} done\n")
    sys.stdout.flush()


# ================= PREVIEW =================
def preview_posts(data, n=PREVIEW_LIMIT):
    print("\n--- SAMPLE POSTS ---")

    for i, post in enumerate(data[:n], start=1):
        url = post.get("url", "[no url]")

        caption = post.get("caption") or ""
        caption = caption.replace("\n", " ").strip()
        caption_preview = caption[:120] + ("..." if len(caption) > 120 else "")

        hashtags = post.get("hashtags", [])
        hashtag_preview = " ".join(f"#{h}" for h in hashtags[:5])

        print(f"[{i}] {url}")

        if caption_preview:
            print(f"    caption : {caption_preview}")
        else:
            print("    caption : [no caption]")

        if hashtag_preview:
            print(f"    hashtags: {hashtag_preview}")

        print()

@contextlib.contextmanager
def suppress_stdout():
    """
    Menonaktifkan stdout sementara.
    Digunakan agar log scraper tidak merusak spinner UX.
    """
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

# ================= MAIN =================
def main():
    parser = argparse.ArgumentParser(
        description="Instagram hashtag scraper"
    )

    parser.add_argument(
        "--tag",
        required=True,
        help="Hashtag tanpa tanda #"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Jumlah post maksimal"
    )

    parser.add_argument(
        "--profile",
        default="ig_profile",
        help="Folder profile Playwright (persistent login)"
    )

    args = parser.parse_args()

    print(f"▶ Target hashtag : #{args.tag}")
    print(f"▶ Max posts      : {args.limit}\n")

    # ---- Spinner start ----
    stop_event = threading.Event()
    spinner_thread = threading.Thread(
        target=spinner_task,
        args=("[SCRAPING] Collecting posts...", stop_event),
        daemon=True
    )
    spinner_thread.start()

    # ---- Scraping (silent) ----
    with suppress_stdout():
        data = scrape_hashtag(
            hashtag=args.tag,
            limit=args.limit,
            profile_dir=args.profile
        )

    stop_event.set()
    spinner_thread.join()
    # ---- Spinner end ----

    print(f"[DONE] {len(data)} posts successfully scraped")

    if not data:
        print("[!] No data collected.")
        return

    preview_posts(data)

    filename = f"result_{args.tag}.json"
    save_data(data, filename=filename)
    print(f"[✓] Data saved in {filename}")
