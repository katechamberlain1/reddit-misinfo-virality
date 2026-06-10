"""
Combine all monthly UK subreddit CSV files from interim dir, clean, and split into train/val/test sets in processed dir

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
 
 
def split(df: pd.DataFrame, val_test_size: int, random_state: int):
    """
    Hold out val + test as a stratified ground-truth pool, rest is train.
 
    val_test_size is the combined size of val + test (split 50/50).
    """
    # drop subreddits with <2 posts (can't stratify on them)
    counts = df['subreddit'].value_counts()
    valid_subs = counts[counts >= 2].index
    df = df[df['subreddit'].isin(valid_subs)].copy()
 
    train_unlabelled, eval_pool = train_test_split(
        df,
        test_size=val_test_size,
        random_state=random_state,
        shuffle=True,
        stratify=df['subreddit'],
    )
 
    val_set, test_set = train_test_split(
        eval_pool,
        test_size=0.5,
        random_state=random_state,
        shuffle=True,
        stratify=eval_pool['subreddit'] if eval_pool['subreddit'].value_counts().min() >= 2 else None,
    )
 
    return train_unlabelled, val_set, test_set
 
 
def process_and_split_data(interim_dir: Path, processed_dir: Path,
                           val_test_size: int = 400, random_state: int = 42):
    df = load_all_months(interim_dir)
    df = clean(df)
    train_unlabelled, val_set, test_set = split(df, val_test_size, random_state)
 
    processed_dir.mkdir(parents=True, exist_ok=True)
    train_unlabelled.to_csv(processed_dir / 'train_unlabelled.csv', index=False)
    val_set.to_csv(processed_dir / 'val_ground_truth.csv', index=False)
    test_set.to_csv(processed_dir / 'test_ground_truth.csv', index=False)
 
    print(f"\nSplits written to {processed_dir}:")
    print(f"  train_unlabelled.csv: {len(train_unlabelled):,}")
    print(f"  val_ground_truth.csv: {len(val_set):,}")
    print(f"  test_ground_truth.csv: {len(test_set):,}")
 
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--interim-dir', type=Path, default=Path('data/interim'))
    parser.add_argument('--processed-dir', type=Path, default=Path('data/processed/UK'))
    parser.add_argument('--val-test-size', type=int, default=400,help='Combined size of val + test sets (split 50/50)')
    parser.add_argument('--random-state', type=int, default=42)
    args = parser.parse_args()
 
    process_and_split_data(
        args.interim_dir, args.processed_dir,
        val_test_size=args.val_test_size,
        random_state=args.random_state,
    )