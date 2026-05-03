import pandas as pd
import re
import os

def clean_price(price_str):
    """Convert '₹32,999' → 32999.0"""
    if pd.isna(price_str):
        return None
    # Remove ₹ symbol and commas
    cleaned = re.sub(r'[₹,]', '', str(price_str)).strip()
    try:
        return float(cleaned)
    except:
        return None

def clean_rating(rating_str):
    """Convert '4.2' → 4.2"""
    if pd.isna(rating_str):
        return None
    try:
        return float(str(rating_str).strip())
    except:
        return None

def clean_no_of_ratings(val):
    """Convert '2,255' → 2255"""
    if pd.isna(val):
        return 0
    cleaned = re.sub(r'[,]', '', str(val)).strip()
    try:
        return int(cleaned)
    except:
        return 0

def preprocess_data():
    print("=" * 50)
    print("PHASE 3: DATA CLEANING")
    print("=" * 50)

    # ── STEP 1: Load raw data ───────────────────────────
    print("\n[1/6] Loading raw data...")
    df = pd.read_csv('data/raw/Amazon-Products.csv',
                     on_bad_lines='skip')
    print(f"      Loaded {len(df):,} products")

    # ── STEP 2: Drop useless columns ───────────────────
    print("\n[2/6] Dropping useless columns...")
    df = df.drop(columns=['Unnamed: 0'], errors='ignore')
    print(f"      Columns remaining: {list(df.columns)}")

    # ── STEP 3: Clean prices ────────────────────────────
    print("\n[3/6] Cleaning prices...")
    df['discount_price'] = df['discount_price'].apply(clean_price)
    df['actual_price']   = df['actual_price'].apply(clean_price)
    print(f"      Sample prices: {df['discount_price'].dropna().head(3).tolist()}")

    # ── STEP 4: Clean ratings ───────────────────────────
    print("\n[4/6] Cleaning ratings...")
    df['ratings']       = df['ratings'].apply(clean_rating)
    df['no_of_ratings'] = df['no_of_ratings'].apply(clean_no_of_ratings)
    print(f"      Sample ratings: {df['ratings'].dropna().head(3).tolist()}")

    # ── STEP 5: Drop rows with no name or price ─────────
    print("\n[5/6] Removing incomplete rows...")
    before = len(df)
    df = df.dropna(subset=['name', 'actual_price'])
    df = df[df['name'].str.strip() != '']
    after = len(df)
    print(f"      Removed {before - after:,} incomplete rows")
    print(f"      Products remaining: {after:,}")

    # ── STEP 6: Create search_text column ───────────────
    # This is what our AI will search through!
    print("\n[6/6] Creating search_text column...")
    df['search_text'] = (
        df['name'].fillna('') + ' | ' +
        df['main_category'].fillna('') + ' | ' +
        df['sub_category'].fillna('') + ' | ' +
        'Price: ₹' + df['discount_price'].fillna(
            df['actual_price']).astype(str) + ' | ' +
        'Rating: ' + df['ratings'].fillna(0).astype(str) + '/5 | ' +
        'Reviews: ' + df['no_of_ratings'].astype(str)
    )

    # ── SAVE cleaned data ───────────────────────────────
    os.makedirs('data/processed', exist_ok=True)
    output_path = 'data/processed/products_cleaned.csv'
    df.to_csv(output_path, index=False)

    print("\n" + "=" * 50)
    print("✅ DATA CLEANING COMPLETE!")
    print("=" * 50)
    print(f"  Total clean products : {len(df):,}")
    print(f"  Saved to             : {output_path}")
    print(f"\n  Category breakdown:")
    print(df['main_category'].value_counts().head(8).to_string())
    print(f"\n  Sample search_text:")
    print(df['search_text'].iloc[0])
    
    return df

if __name__ == "__main__":
    df = preprocess_data()