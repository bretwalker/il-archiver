#!/usr/bin/env python3

import re
import time
import os

import argparse
import feedparser
from weasyprint import CSS, HTML

TITLE_REGEX = re.compile(r"[^0-9a-zA-Z]+")


def get_entries_page(feed_url, start_page):
    page = start_page
    while True:
        print(f"Fetching page {page}")
        f = feedparser.parse(f"{feed_url}?paged={page}")
        if f.get("bozo_exception"):
            raise Exception(f.get("bozo_exception"))
        page += 1
        yield f["entries"]


def main(feed_url, output_dir, start_page, wait_time):
    for entries_page in get_entries_page(feed_url, start_page):
        if not entries_page:
            print("No more entries")
            return
        for entry in entries_page:
            print(f"Generating PDF for: {entry['title']}")
            entry_date_string = time.strftime("%Y-%m-%d", entry["published_parsed"])
            entry_title = TITLE_REGEX.sub("_", entry["title"])[:50]
            HTML(entry["link"]).write_pdf(
                os.path.join(output_dir, f"{entry_date_string}-{entry_title}.pdf"),
                stylesheets=[
                    CSS(
                        string="""
                    @page { 
                        size: Letter; 
                        margin: 0in 0.44in 0.2in 0.44in;
                    }
                    
                    .content-area {
                        float: none !important;
                        margin: 5 !important;
                    }
                    
                    .alignright, .alignleft, * {
                        float: none !important;
                    }
                    """
                    )
                ],
            )

            time.sleep(wait_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("feed_url", help="IL author RSS feed URL")
    parser.add_argument("output", help="output directory absolute path")
    parser.add_argument("-w", "--wait", help="time to wait between requests", type=int, default=3)
    parser.add_argument("-s", "--start", help="which page to start on", type=int, default=1)
    args = parser.parse_args()
    main(args.feed_url, args.output, args.start, args.wait)
