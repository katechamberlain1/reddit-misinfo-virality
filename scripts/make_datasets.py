"""
Combine all monthly UK subreddit CSV files from interim dir, clean, and split into train/val/test sets in processed dir

    1. Load all monthly CSVs from interim_dir
    2. Clean text
    3. Sample gold_set_size posts for hand-labelling (BERT validation only)
    4. Split remaining posts 80/10/10 into train/val/test for XGBoost

To be run after ingest_raw.py
"""

import argparse
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

 
def load_all_months(interim_dir: Path) -> pd.DataFrame:
    """Concatenate every uk_subreddits_*.csv in interim_dir."""
    files = sorted(interim_dir.glob('uk_subreddits_*.csv'))
    if not files:
        raise FileNotFoundError(
            f"No uk_subreddits_*.csv files found in {interim_dir}. "
            f"Run ingest_raw.py first."
        )
 
    print(f"Loading {len(files)} monthly file(s):")
    dfs = []
    for f in files:
        df = pd.read_csv(f)
        print(f"  {f.name}: {len(df):,} rows")
        dfs.append(df)
 
    combined = pd.concat(dfs, ignore_index=True)
    print(f"\nTotal: {len(combined):,} rows across {len(files)} month(s)")
    return combined
 
 
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Apply text cleaning and feature engineering."""
    df = df.copy()
 
    # combine title and selftext with a separator
    df['combined_text'] = (
        df['title'].fillna('') + ' ' + df['selftext'].fillna('')
    ).str.strip()
 
    # strip removed/deleted markers
    df['combined_text'] = df['combined_text'].str.replace(
        r'\[removed\]|\[deleted\]', '', regex=True
    ).str.strip()
 
    # word count
    df['word_count'] = df['combined_text'].str.split().str.len().fillna(0).astype(int)
 
    # drop empty posts (no useful text)
    df = df[df['word_count'] >= 1].copy()
 
    return df

def extract_gold_set(df, gold_set_size, random_state):
    """
    Sample gold_set_size posts for hand-labelling.
    Used ONLY for BERT veracity validation — never for XGBoost.
    """
    counts = df['subreddit'].value_counts()
    valid_subs = counts[counts >= 2].index
    df = df[df['subreddit'].isin(valid_subs)].copy()
 
    gold_df, remaining_df = train_test_split(
        df,
        test_size=len(df) - gold_set_size,
        random_state=random_state,
        shuffle=True,
        stratify=df['subreddit'],
    )
    return gold_df, remaining_df
 
def split(df, val_test_size, random_state):
    """Split into train/val/test for XGBoost pipeline."""
    counts = df['subreddit'].value_counts()
    valid_subs = counts[counts >= 2].index
    df = df[df['subreddit'].isin(valid_subs)].copy()
 
    train_df, eval_pool = train_test_split(
        df,
        test_size=val_test_size,
        random_state=random_state,
        shuffle=True,
        stratify=df['subreddit'],
    )
 
    val_df, test_df = train_test_split(
        eval_pool,
        test_size=0.5,
        random_state=random_state,
        shuffle=True,
        stratify=eval_pool['subreddit']
        if eval_pool['subreddit'].value_counts().min() >= 2
        else None,
    )
    return train_df, val_df, test_df
 
 
def process_and_split_data(interim_dir, processed_dir, 
                           gold_set_size=200,
                           random_state=42):
    df = load_all_months(interim_dir)
    df = clean(df)
    print(f"\nTotal clean posts: {len(df):,}")

 
    # step 1: extract gold set
    gold_df, remaining_df = extract_gold_set(df, gold_set_size, random_state)
    print(f"\nGold set (hand-labelling): {len(gold_df):,} posts")
    print(f"Remaining for XGBoost splits: {len(remaining_df):,} posts")
 
    # step 2: split remaining
    train_df, temp_df = train_test_split(
    df,
    test_size=0.2,          # 20% for val+test combined
    random_state=random_state,
    shuffle=True,
    stratify=df['subreddit'],
    )

    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.5,          # split 20% evenly → 10% val, 10% test
        random_state=random_state,
        shuffle=True,
        stratify=temp_df['subreddit']
        if temp_df['subreddit'].value_counts().min() >= 2
        else None,
    )

 
    # save
    processed_dir.mkdir(parents=True, exist_ok=True)
    gold_df.to_csv(processed_dir / 'gold_set_unlabelled.csv', index=False)
    train_df.to_csv(processed_dir / 'train.csv', index=False)
    val_df.to_csv(processed_dir / 'val.csv', index=False)
    test_df.to_csv(processed_dir / 'test.csv', index=False)
 
    print(f"\nFiles written to {processed_dir}:")
    print(f"  gold_set_unlabelled.csv : {len(gold_df):,}  <- hand-label for BERT validation")
    print(f"  train.csv               : {len(train_df):,}")
    print(f"  val.csv                 : {len(val_df):,}")
    print(f"  test.csv                : {len(test_df):,}")
    print(f"\nSubreddit distribution in train:")
    print(train_df['subreddit'].value_counts().to_string())
 
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--interim-dir', type=Path, default=Path('data/interim'))
    parser.add_argument('--processed-dir', type=Path, default=Path('data/processed/UK'))
    parser.add_argument('--gold-set-size', type=int, default=200,
                        help='Posts for hand-labelling (BERT validation only).')
    parser.add_argument('--random-state', type=int, default=42)
    args = parser.parse_args()
 
    process_and_split_data(
        args.interim_dir, args.processed_dir,
        gold_set_size=args.gold_set_size,
        random_state=args.random_state,
    )