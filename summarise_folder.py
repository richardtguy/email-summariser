from summarise_emails import EmailSummary
from datetime import datetime
import argparse
from pathlib import Path
from tqdm import tqdm
from jinja2 import Environment, PackageLoader, select_autoescape
import re
import sys
import os
import json
import asyncio
import aiohttp


def dt_from_RFC5322(datestring: str) -> datetime:
    dt_pattern = re.compile("\S{3}, (?P<d>\d+) (?P<b>\S{3}) (?P<Y>\d{4}) (?P<H>\d{2}):(?P<M>\d{2}):(?P<S>\d{2}) (?P<z>[+-]\d{4})")
    m = dt_pattern.search(datestring)
    dt = datetime.strptime(f"{m.group('Y')} {m.group('b')} {m.group('d')} {m.group('H')}:{m.group('M')} {m.group('z')}", "%Y %b %d %H:%M %z")
    return dt

def summarise_folder(path: str) -> list:
    files = Path(path).absolute().iterdir()
    results = []
    for item in tqdm(files):
        if item.is_file():
            try:
                with open(item, "r") as f:
                    raw_email = f.read()
            except UnicodeDecodeError as e:
                print(f"Error reading file: {item} ({e})")
                continue
            msg = EmailSummary(raw_email)
            dt = dt_from_RFC5322(msg.Date)
            results.append(
                {
                    "subject": msg.Subject,
                    "from": msg.From,
                    "to": msg.To,
                    "date": dt.isoformat(),
                    "uri": item.as_uri(),
                    "summary": msg.summary,
                }
            )
    results.sort(key=lambda x: x["date"])
    return results 

def output_html(emails: list) -> str:
    env = Environment(
        loader=PackageLoader("summarise_folder"),
        autoescape=select_autoescape()
    )
    template = env.get_template("template.html")
    return(template.render(emails=emails))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder')
    args = parser.parse_args()
    
    summary = summarise_folder(args.folder)
    output = output_html(summary)

    with open(f"summary.html", "w") as f:
        f.write(output)