"""
Database module for Yupoo Scraper
SQLite database with enhanced schema for products, prices, and categories
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional
from contextlib import contextmanager
import time

DATABASE_PATH = os.environ.get("DATABASE_PATH", "/app/data/yupoo.db")

def get_db_path():
    """Get database path, ensuring directory exists"""
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    return DATABASE_PATH

@contextmanager
def get_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database with enhanced schema"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Main products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                seller TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                image_url TEXT,
                price REAL,
                price_currency TEXT DEFAULT 'CNY',
                category TEXT,
                detected_category TEXT,
                brand TEXT,
                purchase_url TEXT,
                purchase_platform TEXT,
                weidian_url TEXT,
                weidian_price REAL,
                taobao_url TEXT,
                taobao_price REAL,
                scraped_at INTEGER DEFAULT (strftime('%s', 'now')),
                updated_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        
        # Sellers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sellers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                yupoo_user TEXT UNIQUE NOT NULL,
                categories TEXT,
                brands TEXT,
                weidian_id TEXT,
                taobao_shop TEXT,
                last_scraped INTEGER,
                product_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active'
            )
        """)
        
        # Scrape log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scrape_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller TEXT NOT NULL,
                started_at INTEGER DEFAULT (strftime('%s', 'now')),
                completed_at INTEGER,
                products_found INTEGER DEFAULT 0,
                pages_scraped INTEGER DEFAULT 0,
                status TEXT DEFAULT 'running',
                error TEXT
            )
        """)
        
        # Category mappings table (for image-based detection)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS category_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                category TEXT NOT NULL
            )
        """)
        
        # Insert default category mappings
        default_mappings = [
            # Bags
            ("bag", "bags"), ("backpack", "bags"), ("purse", "bags"), ("wallet", "bags"),
            ("tote", "bags"), ("clutch", "bags"), ("handbag", "bags"), ("crossbody", "bags"),
            ("messenger", "bags"), ("satchel", "bags"), ("duffle", "bags"), ("briefcase", "bags"),
            
            # Shoes
            ("shoe", "shoes"), ("sneaker", "shoes"), ("boot", "shoes"), ("sandal", "shoes"),
            ("slipper", "shoes"), ("loafer", "shoes"), ("trainer", "shoes"), ("runner", "shoes"),
            ("dunk", "shoes"), ("jordan", "shoes"), ("yeezy", "shoes"), ("force", "shoes"),
            ("air max", "shoes"), ("aj1", "shoes"), ("aj4", "shoes"),
            
            # Tops
            ("hoodie", "hoodies"), ("sweatshirt", "hoodies"), ("pullover", "hoodies"),
            ("t-shirt", "tshirts"), ("tee", "tshirts"), ("shirt", "shirts"),
            ("polo", "shirts"), ("blouse", "shirts"),
            
            # Jackets
            ("jacket", "jackets"), ("coat", "jackets"), ("parka", "jackets"), 
            ("bomber", "jackets"), ("windbreaker", "jackets"), ("down", "jackets"),
            ("puffer", "jackets"), ("vest", "jackets"), ("gilet", "jackets"),
            
            # Pants
            ("pant", "pants"), ("jean", "pants"), ("trouser", "pants"), 
            ("jogger", "pants"), ("short", "shorts"), ("cargo", "pants"),
            ("sweatpant", "pants"), ("legging", "pants"),
            
            # Accessories
            ("belt", "accessories"), ("hat", "accessories"), ("cap", "accessories"),
            ("scarf", "accessories"), ("glove", "accessories"), ("beanie", "accessories"),
            ("sunglasses", "accessories"), ("glasses", "accessories"), ("tie", "accessories"),
            ("watch", "watches"), ("jewelry", "jewelry"), ("necklace", "jewelry"),
            ("bracelet", "jewelry"), ("ring", "jewelry"), ("earring", "jewelry"),
            ("chain", "jewelry"),
            
            # Other
            ("sweater", "knitwear"), ("cardigan", "knitwear"), ("knit", "knitwear"),
            ("dress", "dresses"), ("skirt", "dresses"),
            ("suit", "suits"), ("blazer", "suits"),
            ("underwear", "underwear"), ("sock", "socks"),
        ]
        
        cursor.execute("SELECT COUNT(*) FROM category_mappings")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO category_mappings (keyword, category) VALUES (?, ?)",
                default_mappings
            )
        
        # Create indexes for faster searches
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_seller ON products(seller)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_title ON products(title)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_scraped ON products(scraped_at)")
        
        conn.commit()
        print("Database initialized successfully")

def save_product(product: Dict[str, Any]) -> bool:
    """Save or update a product in the database"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO products (
                id, seller, title, url, image_url, price, price_currency,
                category, detected_category, brand, purchase_url, purchase_platform,
                weidian_url, weidian_price, taobao_url, taobao_price,
                scraped_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product.get("id"),
            product.get("seller"),
            product.get("title"),
            product.get("url"),
            product.get("image_url"),
            product.get("price"),
            product.get("price_currency", "CNY"),
            product.get("category"),
            product.get("detected_category"),
            product.get("brand"),
            product.get("purchase_url"),
            product.get("purchase_platform"),
            product.get("weidian_url"),
            product.get("weidian_price"),
            product.get("taobao_url"),
            product.get("taobao_price"),
            product.get("scraped_at", int(time.time())),
            int(time.time())
        ))
        
        conn.commit()
        return True

def save_products_batch(products: List[Dict[str, Any]]) -> int:
    """Save multiple products in a batch"""
    saved = 0
    with get_connection() as conn:
        cursor = conn.cursor()
        
        for product in products:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO products (
                        id, seller, title, url, image_url, price, price_currency,
                        category, detected_category, brand, purchase_url, purchase_platform,
                        weidian_url, weidian_price, taobao_url, taobao_price,
                        scraped_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product.get("id"),
                    product.get("seller"),
                    product.get("title"),
                    product.get("url"),
                    product.get("image_url"),
                    product.get("price"),
                    product.get("price_currency", "CNY"),
                    product.get("category"),
                    product.get("detected_category"),
                    product.get("brand"),
                    product.get("purchase_url"),
                    product.get("purchase_platform"),
                    product.get("weidian_url"),
                    product.get("weidian_price"),
                    product.get("taobao_url"),
                    product.get("taobao_price"),
                    product.get("scraped_at", int(time.time())),
                    int(time.time())
                ))
                saved += 1
            except Exception as e:
                print(f"Error saving product {product.get('id')}: {e}")
        
        conn.commit()
    return saved

def search_products(
    query: str = "",
    seller: str = None,
    category: str = None,
    brand: str = None,
    min_price: float = None,
    max_price: float = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Search products in SQLite database"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        if query:
            conditions.append("(title LIKE ? OR brand LIKE ? OR category LIKE ?)")
            like_query = f"%{query}%"
            params.extend([like_query, like_query, like_query])
        
        if seller:
            conditions.append("seller = ?")
            params.append(seller)
        
        if category:
            conditions.append("(category = ? OR detected_category = ?)")
            params.extend([category, category])
        
        if brand:
            conditions.append("brand LIKE ?")
            params.append(f"%{brand}%")
        
        if min_price is not None:
            conditions.append("price >= ?")
            params.append(min_price)
        
        if max_price is not None:
            conditions.append("price <= ?")
            params.append(max_price)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        sql = f"""
            SELECT * FROM products
            WHERE {where_clause}
            ORDER BY scraped_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]

def get_product_count(
    query: str = "",
    seller: str = None,
    category: str = None,
    brand: str = None
) -> int:
    """Get total count of products matching criteria"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        conditions = []
        params = []
        
        if query:
            conditions.append("(title LIKE ? OR brand LIKE ? OR category LIKE ?)")
            like_query = f"%{query}%"
            params.extend([like_query, like_query, like_query])
        
        if seller:
            conditions.append("seller = ?")
            params.append(seller)
        
        if category:
            conditions.append("(category = ? OR detected_category = ?)")
            params.extend([category, category])
        
        if brand:
            conditions.append("brand LIKE ?")
            params.append(f"%{brand}%")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        sql = f"SELECT COUNT(*) FROM products WHERE {where_clause}"
        cursor.execute(sql, params)
        
        return cursor.fetchone()[0]

def get_all_sellers_stats() -> List[Dict[str, Any]]:
    """Get statistics for all sellers"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT seller, COUNT(*) as product_count,
                   MAX(scraped_at) as last_scraped
            FROM products
            GROUP BY seller
            ORDER BY product_count DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

def get_all_categories() -> List[str]:
    """Get all unique categories"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT category FROM products WHERE category IS NOT NULL
            UNION
            SELECT DISTINCT detected_category FROM products WHERE detected_category IS NOT NULL
        """)
        return [row[0] for row in cursor.fetchall() if row[0]]

def get_all_brands() -> List[str]:
    """Get all unique brands"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT brand FROM products WHERE brand IS NOT NULL ORDER BY brand")
        return [row[0] for row in cursor.fetchall() if row[0]]

def get_category_mappings() -> Dict[str, str]:
    """Get keyword to category mappings for detection"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT keyword, category FROM category_mappings")
        return {row["keyword"]: row["category"] for row in cursor.fetchall()}

def detect_category(title: str) -> Optional[str]:
    """Detect category from product title using keyword mappings"""
    mappings = get_category_mappings()
    title_lower = title.lower()
    
    for keyword, category in mappings.items():
        if keyword in title_lower:
            return category
    
    return None

def log_scrape_start(seller: str) -> int:
    """Log the start of a scraping session"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO scrape_log (seller, started_at, status) VALUES (?, ?, 'running')",
            (seller, int(time.time()))
        )
        conn.commit()
        return cursor.lastrowid

def log_scrape_complete(log_id: int, products_found: int, pages_scraped: int, status: str = "completed", error: str = None):
    """Log the completion of a scraping session"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE scrape_log
            SET completed_at = ?, products_found = ?, pages_scraped = ?, status = ?, error = ?
            WHERE id = ?
        """, (int(time.time()), products_found, pages_scraped, status, error, log_id))
        conn.commit()

def get_recent_scrapes(limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent scraping sessions"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM scrape_log
            ORDER BY started_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

def clear_products_for_seller(seller: str):
    """Clear all products for a specific seller before re-scraping"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE seller = ?", (seller,))
        conn.commit()

def get_total_products() -> int:
    """Get total number of products in database"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        return cursor.fetchone()[0]

# Initialize database on import
if __name__ == "__main__":
    init_db()
    print(f"Database path: {get_db_path()}")
    print(f"Total products: {get_total_products()}")
