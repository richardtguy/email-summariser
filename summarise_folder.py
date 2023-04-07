from summarise_emails import EmailSummary
import json
import argparse
from pathlib import Path
from tqdm import tqdm

def summarise_folder(path: str) -> list:
    files = Path(path).absolute().iterdir()
    results = []
    for item in tqdm(files):
        if item.is_file():
            with open(item, "r") as f:
                raw_email = f.read()
            msg = EmailSummary(raw_email)
            results.append(
                {
                    "subject": msg.Subject,
                    "from": msg.From,
                    "to": msg.To,
                    "date": msg.Date,
                    "uri": item.as_uri(),
                    "summary": msg.summary,
                }
            )
    return results 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folder')
    args = parser.parse_args()
    
    summary = summarise_folder(args.folder)
    json_summary = json.dumps(summary, indent=4)

    with open(f"summary.json", "w") as f:
        f.write(json_summary)