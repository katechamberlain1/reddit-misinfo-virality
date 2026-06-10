
"""
Process raw Pushift .zst dump files and extract UK political subreddits

Run once raw .zst files (format RS_YYY-MM.zst) into raw data dir

Produces one csv per month in interim data dir, named uk_subreddits_YYYY-MM.csv
Skips moths that have already been processed so that processing can be re-run without re-processing all months
"""

import argparse
import csv
import io
import json
import re
from pathlib import Path
import zstandard as zstd

# subreddits to filter for
TARGET_SUBREDDITS = {
    # general UK politics
    'ukpolitics', 'unitedkingdom', 'uknews', 'britishpolitics',
    # right-leaning
    'tories', 'reformuk', 'gbnews',
    # left-leaning
    'labouruk', 'greenpartyuk',
    # different contexts
    'brexit', 'policeuk',
}

#columns to retain in csv output
COLUMNS = ['id', 'created_utc', 'subreddit', 'title', 'selftext', 'score', 'num_comments', 'url']

# File naming convention, e.g. RS_2024009.zst goes to 2024-09
ZST_PATTERN = re.compile(r'^RS_(\d{4}-\d{2})\.zst$')

def isolate_subreddits(input_zst_path: Path, output_csv_path: Path) -> int:
    """
    Parse one .zst dump and write matching politcal posts to a CSV. Returns match count
    """"

    decompressor = zstd.ZstdDecompressor()

    match_count = 0
    line_count = 0

    with open(input_zst_path, 'rb') as f, open(output_csv_path, 'w', newline='', encoding='utf-8') as csv_out:
        writer = csv.DictWriter(csv_out, fieldnames=COLUMNS)
        writer.writeheader()

        stream_reader = decompressor.stream_reader(f)
        text_stream = io.TextIOWrapper(stream_reader, encoding='utf-8')

        for line in text_stream:
            line_count += 1
            try:
                post =json.loads(line)
            except:
                continue

            subreddit = post.get('subreddit', '').lower()
            if subreddit not in TARGET_SUBREDDITS:
                continue

            title = post.get('title', '')
            if not title or title in ['[deleted]', '[removed]']:
                continue

            try: 
                writer.writerow({
                                        'id': post.get('id'),
                    'created_utc': post.get('created_utc'),
                    'subreddit': post.get('subreddit'),
                    'title': title,
                    'selftext': post.get('selftext', ''),
                    'score': int(post.get('score', 0)),
                    'num_comments': int(post.get('num_comments', 0)),
                    'url': post.get('url', ''),
                })

                match_count += 1
            except:
                continue

            if line_count % 100_000 == 0:
                print(f"Processed {line_count} lines, found {match_count} matches so far")

    return match_count


def ingest_all_months(raw_dir: Path, interim_dir: Path, force: bool = False):
    """
    Process all .zst files in raw_dir and write matching posts to interim_dir. Skips months that have already been processed unless force=True
    """
    interim_dir.mkdir(parents=True, exist_ok=True)

    zst_files = sorted(raw_dir.glob('RS_*.zst'))
    if not zst_files: 
        print (f'No RS_*.zst files found in raw data directory {raw_dir}')
        return
    
    print(f'Found {len(zst_files)} .zst files to process')

    for zst_path in zst_files: 
        m = ZST_PATTERN.match(zst_path.name)
        if not m:
            print(f'Skipping file with unexpected name format: {zst_path.name}')
            continue

        month = m.group(1)
        out_path = interim_dir / f'uk_subreddits_{month}.csv'

        if out_path.exists() and not force:
            print (f'Skipping {month} as output file already exists (use --force to re-process)')
            continue 

        matches = isolate_subreddits(zst_path, out_path)
        print(f'Finished processing {month}: found {matches} matching posts')

        if __name__ == '__main__':
            parser = argparse.ArgumentParser(description=__doc__)
            parser.add_argument('--raw-dir', type=Path, default=Path('data/raw'), help='Directory containing RS_YYYY-MM.zst files')
            parser.add_argument('--interim-dir', type=Path, default=Path('data/interim'), help='Directory to write per-month CSVs')
            parser.add_argument('--force', action='store_true', help='Re-process months even if their CSV already exists')
            args = parser.parse_args()
 
            ingest_all_months(args.raw_dir, args.interim_dir, force=args.force)
    

            

