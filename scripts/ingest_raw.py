import argparse, csv, io, json, re
from pathlib import Path
import zstandard as zstd

TARGET_SUBREDDITS = {
    'ukpolitics', 'unitedkingdom', 'uknews', 'britishpolitics',
    'tories', 'reformuk', 'gbnews', 'labouruk', 'greenpartyuk',
    'brexit', 'policeuk',
}
COLUMNS = ['id', 'created_utc', 'subreddit', 'title', 'selftext', 'score', 'num_comments', 'url']
ZST_PATTERN = re.compile(r'^RS_(\d{4}-\d{2})\.zst$')

def isolate_subreddits(input_zst_path, output_csv_path):
    decompressor = zstd.ZstdDecompressor(max_window_size=2**31)
    match_count = 0
    line_count = 0
    with open(input_zst_path, 'rb') as f, \
         open(output_csv_path, 'w', newline='', encoding='utf-8') as csv_out:
        writer = csv.DictWriter(csv_out, fieldnames=COLUMNS)
        writer.writeheader()
        for line in io.TextIOWrapper(decompressor.stream_reader(f), encoding='utf-8'):
            line_count += 1
            try:
                post = json.loads(line)
            except:
                continue
            if post.get('subreddit', '').lower() not in TARGET_SUBREDDITS:
                continue
            title = post.get('title', '')
            if not title or title in ['[deleted]', '[removed]']:
                continue
            try:
                writer.writerow({
                    'id': post.get('id'), 'created_utc': post.get('created_utc'),
                    'subreddit': post.get('subreddit'), 'title': title,
                    'selftext': post.get('selftext', ''),
                    'score': int(post.get('score', 0)),
                    'num_comments': int(post.get('num_comments', 0)),
                    'url': post.get('url', ''),
                })
                match_count += 1
            except:
                continue
            if line_count % 100_000 == 0:
                print(f"    {line_count:,} lines, {match_count:,} matches")
    return match_count

def ingest_all_months(raw_dir, interim_dir, force=False):
    interim_dir.mkdir(parents=True, exist_ok=True)
    zst_files = sorted(raw_dir.glob('RS_*.zst'))
    if not zst_files:
        print(f"No RS_*.zst files found in {raw_dir}"); return
    print(f"Found {len(zst_files)} file(s)")
    for zst_path in zst_files:
        m = ZST_PATTERN.match(zst_path.name)
        if not m:
            print(f"Skipping {zst_path.name}"); continue
        month = m.group(1)
        out_path = interim_dir / f'uk_subreddits_{month}.csv'
        if out_path.exists() and not force:
            print(f"  {month}: already done (skipping)"); continue
        print(f"  {month}: processing...")
        matches = isolate_subreddits(zst_path, out_path)
        print(f"  {month}: done — {matches:,} posts saved")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw-dir', type=Path, default=Path('data/raw'))
    parser.add_argument('--interim-dir', type=Path, default=Path('data/interim'))
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    ingest_all_months(args.raw_dir, args.interim_dir, force=args.force)
