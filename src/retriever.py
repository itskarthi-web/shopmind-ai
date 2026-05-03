import chromadb
from sentence_transformers import SentenceTransformer

# Load once, reuse everywhere
_model      = None
_collection = None

def get_model():
    global _model
    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def get_collection():
    global _collection
    if _collection is None:
        client      = chromadb.PersistentClient(path='models/chromadb')
        _collection = client.get_collection("products")
    return _collection

def search_products(query: str, n_results: int = 5, 
                    category: str = None):
    """
    Search for products similar to the query.
    Returns list of product dicts.
    """
    model      = get_model()
    collection = get_collection()

    # Convert query to vector
    query_embedding = model.encode([query])[0].tolist()

    # Search ChromaDB
    where = None
    if category:
        where = {"main_category": {"$eq": category}}

    results = collection.query(
        query_embeddings = [query_embedding],
        n_results        = n_results,
        where            = where
    )

    # Format results nicely
    products = []
    for i in range(len(results['ids'][0])):
        meta = results['metadatas'][0][i]
        
        # Calculate discount %
        try:
            actual   = float(meta['actual_price']) if meta['actual_price'] != 'nan' else 0
            discount = float(meta['discount_price']) if meta['discount_price'] != 'nan' else actual
            discount_pct = int(((actual - discount) / actual) * 100) if actual > 0 else 0
        except:
            discount_pct = 0

        products.append({
            'name'          : meta['name'],
            'main_category' : meta['main_category'],
            'sub_category'  : meta['sub_category'],
            'discount_price': meta['discount_price'],
            'actual_price'  : meta['actual_price'],
            'ratings'       : meta['ratings'],
            'no_of_ratings' : meta['no_of_ratings'],
            'discount_pct'  : discount_pct,
            'image'         : meta.get('image', ''),
            'link'          : meta.get('link', ''),
        })

    return products

def format_products_for_ai(products: list) -> str:
    """Format product list into text for the AI to read."""
    if not products:
        return "No products found."
    
    formatted = []
    for i, p in enumerate(products, 1):
        price = p['discount_price'] if p['discount_price'] != 'nan' else p['actual_price']
        discount_info = f" ({p['discount_pct']}% off)" if p['discount_pct'] > 0 else ""
        
        formatted.append(
            f"Product {i}:\n"
            f"  Name     : {p['name'][:120]}\n"
            f"  Category : {p['main_category']} > {p['sub_category']}\n"
            f"  Price    : ₹{price}{discount_info}\n"
            f"  Rating   : {p['ratings']}/5 ({p['no_of_ratings']} reviews)\n"
            f"  Link     : {p['link']}\n"
        )
    
    return "\n".join(formatted)


if __name__ == "__main__":
    # Quick test
    print("Testing retriever...")
    products = search_products("wireless headphones under 2000", n_results=3)
    print(format_products_for_ai(products))