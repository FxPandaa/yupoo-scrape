"""
Search API with Typesense and SQLite fallback
"""

import os
import time
import typesense
from typing import List, Dict, Any, Optional

from .database import search_products, get_product_count, get_all_sellers_stats, get_all_categories, get_all_brands

# Typesense configuration
TYPESENSE_HOST = os.environ.get("TYPESENSE_HOST", "typesense")
TYPESENSE_PORT = os.environ.get("TYPESENSE_PORT", "8108")
TYPESENSE_API_KEY = os.environ.get("TYPESENSE_API_KEY", "yupoo-search-key")

# Typesense client
try:
    typesense_client = typesense.Client({
        "nodes": [{
            "host": TYPESENSE_HOST,
            "port": TYPESENSE_PORT,
            "protocol": "http"
        }],
        "api_key": TYPESENSE_API_KEY,
        "connection_timeout_seconds": 5
    })
except Exception as e:
    print(f"Warning: Could not initialize Typesense client: {e}")
    typesense_client = None

COLLECTION_NAME = "products"

def init_typesense():
    """Initialize Typesense collection"""
    if not typesense_client:
        return False
    
    schema = {
        "name": COLLECTION_NAME,
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "seller", "type": "string", "facet": True},
            {"name": "title", "type": "string"},
            {"name": "url", "type": "string"},
            {"name": "image_url", "type": "string", "optional": True},
            {"name": "price", "type": "float", "optional": True},
            {"name": "price_currency", "type": "string", "optional": True},
            {"name": "category", "type": "string", "facet": True, "optional": True},
            {"name": "detected_category", "type": "string", "facet": True, "optional": True},
            {"name": "brand", "type": "string", "facet": True, "optional": True},
            {"name": "purchase_url", "type": "string", "optional": True},
            {"name": "purchase_platform", "type": "string", "optional": True},
            {"name": "weidian_url", "type": "string", "optional": True},
            {"name": "weidian_price", "type": "float", "optional": True},
            {"name": "taobao_url", "type": "string", "optional": True},
            {"name": "taobao_price", "type": "float", "optional": True},
            {"name": "scraped_at", "type": "int64"}
        ],
        "default_sorting_field": "scraped_at"
    }
    
    try:
        # Delete existing collection
        try:
            typesense_client.collections[COLLECTION_NAME].delete()
        except:
            pass
        
        # Create new collection
        typesense_client.collections.create(schema)
        print("Typesense collection created successfully")
        return True
        
    except Exception as e:
        print(f"Error initializing Typesense: {e}")
        return False

def index_products(products: List[Dict[str, Any]]) -> int:
    """Index products in Typesense"""
    if not typesense_client:
        return 0
    
    indexed = 0
    
    for product in products:
        try:
            # Prepare document for Typesense
            doc = {
                "id": str(product.get("id", "")),
                "seller": str(product.get("seller", "")),
                "title": str(product.get("title", "")),
                "url": str(product.get("url", "")),
                "scraped_at": int(product.get("scraped_at", time.time()))
            }
            
            # Optional fields
            if product.get("image_url"):
                doc["image_url"] = str(product["image_url"])
            if product.get("price"):
                doc["price"] = float(product["price"])
            if product.get("price_currency"):
                doc["price_currency"] = str(product["price_currency"])
            if product.get("category"):
                doc["category"] = str(product["category"])
            if product.get("detected_category"):
                doc["detected_category"] = str(product["detected_category"])
            if product.get("brand"):
                doc["brand"] = str(product["brand"])
            if product.get("purchase_url"):
                doc["purchase_url"] = str(product["purchase_url"])
            if product.get("purchase_platform"):
                doc["purchase_platform"] = str(product["purchase_platform"])
            if product.get("weidian_url"):
                doc["weidian_url"] = str(product["weidian_url"])
            if product.get("weidian_price"):
                doc["weidian_price"] = float(product["weidian_price"])
            if product.get("taobao_url"):
                doc["taobao_url"] = str(product["taobao_url"])
            if product.get("taobao_price"):
                doc["taobao_price"] = float(product["taobao_price"])
            
            typesense_client.collections[COLLECTION_NAME].documents.upsert(doc)
            indexed += 1
            
        except Exception as e:
            print(f"Error indexing product {product.get('id')}: {e}")
    
    return indexed

def search_typesense(
    query: str = "",
    seller: str = None,
    category: str = None,
    brand: str = None,
    min_price: float = None,
    max_price: float = None,
    has_links: bool = False,
    page: int = 1,
    per_page: int = 48
) -> Dict[str, Any]:
    """Search products in Typesense with fallback to SQLite"""
    
    # Check if Typesense is available and has documents
    use_typesense = False
    
    if typesense_client:
        try:
            collection = typesense_client.collections[COLLECTION_NAME].retrieve()
            if collection.get("num_documents", 0) > 0:
                use_typesense = True
        except:
            pass
    
    if use_typesense:
        return _search_typesense(query, seller, category, brand, min_price, max_price, has_links, page, per_page)
    else:
        # Fallback to SQLite
        return _search_sqlite(query, seller, category, brand, min_price, max_price, has_links, page, per_page)

def _search_typesense(
    query: str = "",
    seller: str = None,
    category: str = None,
    brand: str = None,
    min_price: float = None,
    max_price: float = None,
    has_links: bool = False,
    page: int = 1,
    per_page: int = 48
) -> Dict[str, Any]:
    """Internal Typesense search"""
    try:
        # Build filter string
        filters = []
        
        if seller:
            filters.append(f"seller:={seller}")
        if category:
            filters.append(f"(category:={category} || detected_category:={category})")
        if brand:
            filters.append(f"brand:={brand}")
        if min_price is not None:
            filters.append(f"price:>={min_price}")
        if max_price is not None:
            filters.append(f"price:<={max_price}")
        
        filter_by = " && ".join(filters) if filters else ""
        
        search_params = {
            "q": query if query else "*",
            "query_by": "title,brand,category,seller",
            "filter_by": filter_by,
            "sort_by": "scraped_at:desc",
            "page": page,
            "per_page": per_page,
            "facet_by": "seller,category,brand",
            "max_facet_values": 100
        }
        
        results = typesense_client.collections[COLLECTION_NAME].documents.search(search_params)
        
        # Format response
        products = []
        for hit in results.get("hits", []):
            doc = hit.get("document", {})
            products.append(doc)
        
        # Extract facets
        facets = {}
        for facet in results.get("facet_counts", []):
            field = facet.get("field_name")
            counts = facet.get("counts", [])
            facets[field] = [{"value": c["value"], "count": c["count"]} for c in counts]
        
        return {
            "products": products,
            "total": results.get("found", 0),
            "page": page,
            "per_page": per_page,
            "total_pages": (results.get("found", 0) + per_page - 1) // per_page,
            "facets": facets,
            "source": "typesense"
        }
        
    except Exception as e:
        print(f"Typesense search error: {e}, falling back to SQLite")
        return _search_sqlite(query, seller, category, brand, min_price, max_price, page, per_page)

def _search_sqlite(
    query: str = "",
    seller: str = None,
    category: str = None,
    brand: str = None,
    min_price: float = None,
    max_price: float = None,
    has_links: bool = False,
    page: int = 1,
    per_page: int = 48
) -> Dict[str, Any]:
    """SQLite fallback search"""
    offset = (page - 1) * per_page
    
    products = search_products(
        query=query,
        seller=seller,
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        limit=per_page,
        offset=offset
    )
    
    # Filter for products with links if requested
    if has_links:
        products = [p for p in products if p.get('weidian_url') or p.get('taobao_url') or p.get('purchase_url')]
    
    total = get_product_count(query=query, seller=seller, category=category, brand=brand)
    
    # Get facets
    facets = {
        "seller": [{"value": s["seller"], "count": s["product_count"]} for s in get_all_sellers_stats()],
        "category": [{"value": c, "count": 0} for c in get_all_categories()],
        "brand": [{"value": b, "count": 0} for b in get_all_brands()]
    }
    
    return {
        "products": products,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
        "facets": facets,
        "source": "sqlite"
    }

def get_stats() -> Dict[str, Any]:
    """Get search statistics"""
    from .database import get_total_products, get_products_with_links_count
    
    sellers = get_all_sellers_stats()
    categories = get_all_categories()
    brands = get_all_brands()
    total = get_total_products()
    
    try:
        with_links = get_products_with_links_count()
    except:
        with_links = 0
    
    return {
        "total_products": total,
        "total_sellers": len(sellers),
        "total_categories": len(categories),
        "total_brands": len(brands),
        "products_with_links": with_links,
        "sellers": sellers,
        "categories": categories,
        "brands": brands
    }
