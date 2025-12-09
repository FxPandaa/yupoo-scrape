"""
FastAPI Backend for Yupoo Scraper Search Engine
"""

from fastapi import FastAPI, Query, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import asyncio
import time

from .database import init_db, get_total_products, get_recent_scrapes
from .search import search_typesense, get_stats, init_typesense, index_products
from .sellers import SELLERS, get_all_sellers, get_sellers_by_category, get_sellers_by_brand, Seller
from .scraper import scrape_seller, scrape_multiple_sellers, quick_test_seller

app = FastAPI(
    title="Yupoo Search Engine",
    description="Search 200+ FashionReps trusted sellers",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Scraping status
scraping_status = {
    "is_running": False,
    "current_seller": None,
    "progress": 0,
    "total_sellers": 0,
    "products_found": 0,
    "started_at": None,
    "errors": []
}

@app.on_event("startup")
async def startup():
    """Initialize database and search on startup"""
    print("Initializing database...")
    init_db()
    print(f"Total products in database: {get_total_products()}")
    
    print("Initializing Typesense...")
    init_typesense()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Yupoo Search Engine",
        "total_products": get_total_products(),
        "total_sellers": len(SELLERS)
    }

@app.get("/api/search")
async def search(
    q: str = Query("", description="Search query"),
    seller: Optional[str] = Query(None, description="Filter by seller"),
    category: Optional[str] = Query(None, description="Filter by category"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(48, ge=1, le=100, description="Results per page")
):
    """Search products"""
    results = search_typesense(
        query=q,
        seller=seller,
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        page=page,
        per_page=per_page
    )
    return results

@app.get("/api/stats")
async def stats():
    """Get database statistics"""
    return get_stats()

@app.get("/api/sellers")
async def list_sellers():
    """Get all available sellers"""
    sellers = get_all_sellers()
    return {
        "sellers": [
            {
                "name": s.name,
                "yupoo_user": s.yupoo_user,
                "categories": s.categories,
                "brands": s.brands,
                "weidian_id": s.weidian_id,
                "url": f"https://x.yupoo.com/photos/{s.yupoo_user}/albums"
            }
            for s in sellers
        ],
        "total": len(sellers)
    }

@app.get("/api/sellers/by-category/{category}")
async def sellers_by_category(category: str):
    """Get sellers for a specific category"""
    sellers = get_sellers_by_category(category)
    return {
        "category": category,
        "sellers": [
            {"name": s.name, "yupoo_user": s.yupoo_user}
            for s in sellers
        ],
        "total": len(sellers)
    }

@app.get("/api/sellers/by-brand/{brand}")
async def sellers_by_brand(brand: str):
    """Get sellers for a specific brand"""
    sellers = get_sellers_by_brand(brand)
    return {
        "brand": brand,
        "sellers": [
            {"name": s.name, "yupoo_user": s.yupoo_user}
            for s in sellers
        ],
        "total": len(sellers)
    }

@app.get("/api/scrape/status")
async def scrape_status():
    """Get current scraping status"""
    return scraping_status

@app.post("/api/scrape/start")
async def start_scraping(
    background_tasks: BackgroundTasks,
    seller_names: Optional[List[str]] = None,
    max_pages: int = Query(50, ge=1, le=100)
):
    """Start scraping sellers"""
    global scraping_status
    
    if scraping_status["is_running"]:
        raise HTTPException(status_code=400, detail="Scraping is already running")
    
    # Get sellers to scrape
    if seller_names:
        sellers = [s for s in SELLERS if s.name in seller_names or s.yupoo_user in seller_names]
    else:
        sellers = SELLERS
    
    if not sellers:
        raise HTTPException(status_code=400, detail="No sellers found")
    
    # Update status
    scraping_status = {
        "is_running": True,
        "current_seller": None,
        "progress": 0,
        "total_sellers": len(sellers),
        "products_found": 0,
        "started_at": int(time.time()),
        "errors": []
    }
    
    # Run in background
    background_tasks.add_task(run_scraping, sellers, max_pages)
    
    return {
        "message": f"Started scraping {len(sellers)} sellers",
        "sellers": [s.name for s in sellers]
    }

async def run_scraping(sellers: List[Seller], max_pages: int):
    """Background scraping task - CONCURRENT for speed"""
    global scraping_status
    
    total_products = 0
    completed_count = 0
    
    # Use semaphore for concurrent but limited scraping
    semaphore = asyncio.Semaphore(5)  # 5 concurrent scrapers
    
    async def scrape_one(seller: Seller) -> int:
        nonlocal completed_count, total_products
        async with semaphore:
            try:
                scraping_status["current_seller"] = seller.name
                count = await scrape_seller(seller, max_pages)
                total_products += count
                completed_count += 1
                scraping_status["progress"] = completed_count
                scraping_status["products_found"] = total_products
                return count
            except Exception as e:
                error_msg = f"{seller.name}: {str(e)}"
                scraping_status["errors"].append(error_msg)
                print(f"Error scraping {seller.name}: {e}")
                completed_count += 1
                scraping_status["progress"] = completed_count
                return 0
    
    # Run all sellers concurrently
    tasks = [scrape_one(seller) for seller in sellers]
    await asyncio.gather(*tasks)
    
    # Done
    scraping_status["is_running"] = False
    scraping_status["progress"] = len(sellers)
    scraping_status["current_seller"] = None
    
    print(f"Scraping complete. Total products: {total_products}")
    
    # Re-index in Typesense
    try:
        from .database import search_products
        all_products = search_products(limit=100000)
        indexed = index_products(all_products)
        print(f"Indexed {indexed} products in Typesense")
    except Exception as e:
        print(f"Error indexing: {e}")

@app.post("/api/scrape/stop")
async def stop_scraping():
    """Stop current scraping (sets flag, won't immediately stop)"""
    global scraping_status
    
    if not scraping_status["is_running"]:
        raise HTTPException(status_code=400, detail="No scraping is running")
    
    scraping_status["is_running"] = False
    return {"message": "Scraping will stop after current seller"}

@app.get("/api/scrape/logs")
async def scrape_logs(limit: int = Query(20, ge=1, le=100)):
    """Get recent scrape logs"""
    logs = get_recent_scrapes(limit)
    return {"logs": logs}

@app.post("/api/test-seller/{yupoo_user}")
async def test_seller(yupoo_user: str):
    """Test if a seller's Yupoo is accessible"""
    # Find seller
    seller = next((s for s in SELLERS if s.yupoo_user == yupoo_user), None)
    
    if not seller:
        # Create temporary seller object
        seller = Seller(name=yupoo_user, yupoo_user=yupoo_user)
    
    accessible = await quick_test_seller(seller)
    
    return {
        "seller": yupoo_user,
        "accessible": accessible,
        "url": f"https://x.yupoo.com/photos/{yupoo_user}/albums"
    }

@app.post("/api/reindex")
async def reindex_typesense():
    """Reindex all products in Typesense"""
    from .database import search_products
    
    # Reinitialize collection
    init_typesense()
    
    # Get all products from SQLite
    all_products = search_products(limit=100000)
    
    # Index in Typesense
    indexed = index_products(all_products)
    
    return {
        "message": f"Reindexed {indexed} products",
        "total_in_db": len(all_products)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
