import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
import os

def create_vector_database():
    print("=" * 50)
    print("PHASE 4A: CREATING VECTOR DATABASE")
    print("=" * 50)

    # ── STEP 1: Load cleaned data ───────────────────────
    print("\n[1/5] Loading cleaned products...")
    df = pd.read_csv('data/processed/products_cleaned.csv')
    print(f"      Raw columns: {list(df.columns)}")

    # Add main_category from sub_category if missing
    if 'main_category' not in df.columns:
        print("      ⚠️  main_category missing — creating from sub_category...")
        df['main_category'] = df['sub_category'].str.split('>').str[0].str.strip()

    # Take 50,000 random products across all categories
    df = df.sample(n=min(50000, len(df)), random_state=42).reset_index(drop=True)
    print(f"      Total products loaded : {len(df):,}")
    print(f"      Unique categories     : {df['main_category'].nunique()}")
    print(f"      Sample categories     : {df['main_category'].unique()[:5].tolist()}")

    # ── STEP 2: Load embedding model ────────────────────
    print("\n[2/5] Loading embedding model...")
    print("      (First time = downloads ~90MB, be patient!)")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("      ✅ Model loaded!")

    # ── STEP 3: Create embeddings ────────────────────────
    print("\n[3/5] Creating embeddings (this takes 2-5 mins)...")
    texts = df['search_text'].fillna('').tolist()
    embeddings = model.encode(
        texts,
        batch_size=256,
        show_progress_bar=True
    )
    print(f"      ✅ Created {len(embeddings):,} embeddings")
    print(f"      Each embedding size  : {len(embeddings[0])} dimensions")

    # ── STEP 4: Store in ChromaDB ────────────────────────
    print("\n[4/5] Storing in ChromaDB...")
    os.makedirs('models/chromadb', exist_ok=True)

    client = chromadb.PersistentClient(path='models/chromadb')

    # Delete existing collection if rebuilding
    try:
        client.delete_collection("products")
        print("      Cleared old collection")
    except:
        pass

    collection = client.create_collection(
        name="products",
        metadata={"hnsw:space": "cosine"}
    )

    # Add in batches of 5000
    batch_size = 5000
    total      = len(df)

    for start in range(0, total, batch_size):
        end   = min(start + batch_size, total)
        batch = df.iloc[start:end]

        collection.add(
            ids        = [str(i) for i in batch.index],
            embeddings = embeddings[start:end].tolist(),
            documents  = batch['search_text'].fillna('').tolist(),
            metadatas  = [
                {
                    'name'          : str(row['name'])[:500],
                    'main_category' : str(row.get('main_category', 'general')),
                    'sub_category'  : str(row.get('sub_category', 'general')),
                    'discount_price': str(row.get('discount_price', 'N/A')),
                    'actual_price'  : str(row.get('actual_price', 'N/A')),
                    'ratings'       : str(row.get('ratings', '0')),
                    'no_of_ratings' : str(row.get('no_of_ratings', '0')),
                    'image'         : str(row['image'])[:500]
                                      if pd.notna(row.get('image')) else '',
                    'link'          : str(row['link'])[:500]
                                      if pd.notna(row.get('link')) else '',
                }
                for _, row in batch.iterrows()
            ]
        )
        print(f"      Stored {end:,} / {total:,} products...")

    # ── STEP 5: Verify ───────────────────────────────────
    print("\n[5/5] Verifying database...")
    count = collection.count()
    print(f"      ✅ ChromaDB has {count:,} products stored!")

    # Quick test searches
    test_queries = ["gaming laptop", "cricket bat", "caps under 300"]

    for test_query in test_queries:
        test_embedding = model.encode([test_query])[0].tolist()
        results = collection.query(
            query_embeddings=[test_embedding],
            n_results=2
        )
        print(f"\n      Test search : '{test_query}'")
        for i, meta in enumerate(results['metadatas'][0]):
            price = meta['discount_price'] if meta['discount_price'] != 'nan' else meta['actual_price']
            print(f"      {i+1}. {meta['name'][:70]}...")
            print(f"         Price: ₹{price} | Rating: {meta['ratings']}/5")

    print("\n" + "=" * 50)
    print("✅ VECTOR DATABASE READY!")
    print("=" * 50)


if __name__ == "__main__":
    create_vector_database()