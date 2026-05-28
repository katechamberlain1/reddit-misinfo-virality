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
                    
                
            except:
                continue