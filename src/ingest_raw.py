import zstandard as zstd
import json
import io
import csv

def isolate_subreddits(input_zst_path, output_csv_path):
    # subreddits to filter for in the master file
    target_subreddits = {
        # general UK politics
        'ukpolitics', 'unitedkingdom', 'uknews', 'BritishPolitics',
        
        # right-leaning
        'tories', 'reformuk', 'gbnews',

        # left-leaning
        'labouruk', 'greenpartyuk',

        # different contexts
        'brexit', 'policeuk'
        }

    # columns to retain 
    columns = ['id', 'created_utc', 'subreddit', 'title', 'selftext', 'score', 'num_comments', 'url']

    decompressor = zstd.ZstdDecompressor()

    with open(input_zst_path, 'rb') as f, open(output_csv_path, 'w', newline='', encoding='utf-8') as csv_out:
        writer = csv.DictWriter(csv_out, fieldnames=columns)
        writer.writeheader()

        stream_reader = decompressor.stream_reader(f)
        text_stream = io.TextIOWrapper(stream_reader, encoding='utf-8')
        
        match_count = 0 
        line_count = 0 

        for line in text_stream:
            line_count += 1
            try:
                post = json.loads(line)
                subreddit = post.get('subreddit', '').lower()

                if subreddit in target_subreddits:
                    title = post.get('title', '')

                    # Ignore the metadata rows that we don't want to ingest
                    if not title or title in ['[deleted]', '[removed]']:
                        continue

                    writer.writerow({
                        'id': post.get('id'),
                        'created_utc': post.get('created_utc'),
                        'subreddit': post.get('subreddit'),
                        'title': title,
                        'selftext': post.get('selftext', ''),
                        'score': int(post.get('score', 0)),
                        'num_comments': int(post.get('num_comments', 0)),
                        'url': post.get('url', '')
                    })
                    match_count += 1

                    if line_count % 5000 == 0:
                        print(f"Processed {line_count} Reddit posts and found {match_count} relevant posts")

            except:
                continue

    print(f"Processing complete. Processed {line_count} posts and saved {match_count} relevant posts to {output_csv_path}")


if __name__ == "__main__":
    isolate_subreddits('data/raw/RS_2024-08.zst', 'data/processed/august_2024_uk_sandbox.csv')