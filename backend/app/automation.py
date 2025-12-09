"""
Unified Automation System for Yupoo Scraper
Handles:
- Auto Reddit discovery
- Auto scraping of new sellers
- Buy link extraction from album pages
- Status tracking
"""

import asyncio
import time
import re
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime

from .sellers import Seller, SELLERS
from .database import (
    save_products_batch, save_discovered_seller, get_discovered_sellers,
    verify_discovered_seller, get_total_products, search_products
)
from .search import index_products

# Global automation state
automation_state = {
    "is_running": False,
    "mode": None,  # "discovery", "scraping", "both"
    "started_at": None,
    
    # Discovery stats
    "discovery": {
        "is_running": False,
        "subreddits_checked": 0,
        "total_subreddits": 6,
        "current_subreddit": None,
        "sellers_found": 0,
        "new_sellers": 0,
        "last_discovery": None,
    },
    
    # Scraping stats  
    "scraping": {
        "is_running": False,
        "current_seller": None,
        "sellers_done": 0,
        "total_sellers": 0,
        "products_found": 0,
        "products_with_links": 0,
        "albums_checked_for_links": 0,
        "errors": [],
    },
    
    # Overall stats
    "total_products": 0,
    "total_sellers_in_db": 0,
    "products_with_buy_links": 0,
}

# Dynamic sellers list (includes discovered ones)
dynamic_sellers: List[Seller] = []

def get_all_known_yupoo_users() -> Set[str]:
    """Get all known Yupoo users from SELLERS and dynamic_sellers"""
    known = set()
    for s in SELLERS:
        known.add(s.yupoo_user.lower())
    for s in dynamic_sellers:
        known.add(s.yupoo_user.lower())
    return known

async def discover_sellers_from_reddit() -> List[Dict]:
    """
    Discover new sellers from Reddit without using the Reddit API
    Uses public JSON endpoints
    """
    global automation_state
    
    discovered = []
    subreddits = ["FashionReps", "DesignerReps", "QualityReps", "Repsneakers", "RepLadies", "CoutureReps"]
    
    automation_state["discovery"]["is_running"] = True
    automation_state["discovery"]["subreddits_checked"] = 0
    automation_state["discovery"]["total_subreddits"] = len(subreddits)
    
    known_users = get_all_known_yupoo_users()
    
    import httpx
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    
    # Yupoo URL patterns
    yupoo_patterns = [
        r'https?://([a-zA-Z0-9_-]+)\.x\.yupoo\.com',
        r'https?://x\.yupoo\.com/photos/([a-zA-Z0-9_-]+)',
        r'([a-zA-Z0-9_-]+)\.x\.yupoo\.com',
    ]
    
    # Weidian patterns
    weidian_patterns = [
        r'https?://(?:www\.)?weidian\.com/item\.html\?itemID=(\d+)',
        r'https?://shop(\d+)\.v\.weidian\.com',
        r'https?://(?:www\.)?weidian\.com/\?userid=(\d+)',
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for subreddit in subreddits:
            automation_state["discovery"]["current_subreddit"] = subreddit
            
            try:
                # Fetch top posts from last month
                url = f"https://www.reddit.com/r/{subreddit}/top.json?t=month&limit=100"
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("data", {}).get("children", [])
                    
                    for post in posts:
                        post_data = post.get("data", {})
                        title = post_data.get("title", "")
                        selftext = post_data.get("selftext", "")
                        url_field = post_data.get("url", "")
                        
                        combined_text = f"{title} {selftext} {url_field}"
                        
                        # Extract Yupoo users
                        for pattern in yupoo_patterns:
                            matches = re.findall(pattern, combined_text, re.IGNORECASE)
                            for match in matches:
                                yupoo_user = match.lower().strip()
                                if yupoo_user and len(yupoo_user) > 2 and yupoo_user not in known_users:
                                    # New seller found!
                                    seller_dict = {
                                        "yupoo_user": yupoo_user,
                                        "yupoo_url": f"https://{yupoo_user}.x.yupoo.com",
                                        "source": f"reddit/{subreddit}",
                                        "discovered_at": int(time.time()),
                                        "verified": False,
                                        "added_to_main": False,
                                    }
                                    
                                    # Check for Weidian links in same post
                                    for wp in weidian_patterns:
                                        wm = re.search(wp, combined_text)
                                        if wm:
                                            seller_dict["weidian_id"] = wm.group(1)
                                            break
                                    
                                    discovered.append(seller_dict)
                                    known_users.add(yupoo_user)
                                    automation_state["discovery"]["sellers_found"] += 1
                    
                    # Small delay to be nice to Reddit
                    await asyncio.sleep(1)
                    
            except Exception as e:
                print(f"Error fetching r/{subreddit}: {e}")
            
            automation_state["discovery"]["subreddits_checked"] += 1
    
    # Save all discovered sellers
    new_count = 0
    for seller in discovered:
        if save_discovered_seller(seller):
            new_count += 1
    
    automation_state["discovery"]["new_sellers"] = new_count
    automation_state["discovery"]["last_discovery"] = int(time.time())
    automation_state["discovery"]["is_running"] = False
    automation_state["discovery"]["current_subreddit"] = None
    
    return discovered

async def add_discovered_to_scrape_queue() -> List[Seller]:
    """Add verified discovered sellers to the dynamic sellers list"""
    global dynamic_sellers
    
    discovered = get_discovered_sellers(verified_only=False, limit=500)
    added = []
    
    for d in discovered:
        yupoo_user = d.get("yupoo_user")
        if not yupoo_user:
            continue
        
        # Check if already in dynamic_sellers or SELLERS
        known = get_all_known_yupoo_users()
        if yupoo_user.lower() in known:
            continue
        
        # Create a Seller object
        new_seller = Seller(
            name=yupoo_user,
            yupoo_user=yupoo_user,
            categories=["discovered"],
            brands=[],
            weidian_id=d.get("weidian_id"),
        )
        
        dynamic_sellers.append(new_seller)
        added.append(new_seller)
    
    return added

async def scrape_album_for_buy_links(album_url: str) -> Dict[str, Any]:
    """
    Visit a single album page to extract buy links (Weidian/Taobao/1688)
    Uses Playwright for JavaScript rendering
    """
    result = {
        "weidian_url": None,
        "taobao_url": None,
        "purchase_url": None,
        "purchase_platform": None,
    }
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.goto(album_url, wait_until='domcontentloaded', timeout=15000)
            await page.wait_for_timeout(1000)
            
            html = await page.content()
            
            # Weidian patterns
            weidian_match = re.search(
                r'https?://(?:www\.)?weidian\.com/item\.html\?itemID=\d+|'
                r'https?://shop\d+\.v\.weidian\.com/item\.html\?itemID=\d+',
                html, re.IGNORECASE
            )
            if weidian_match:
                result["weidian_url"] = weidian_match.group(0)
                result["purchase_platform"] = "weidian"
            
            # Taobao patterns  
            taobao_match = re.search(
                r'https?://item\.taobao\.com/item\.htm[^\s"<>]+id=\d+|'
                r'https?://(?:www\.)?taobao\.com/[^\s"<>]+',
                html, re.IGNORECASE
            )
            if taobao_match:
                result["taobao_url"] = taobao_match.group(0)
                if not result["purchase_platform"]:
                    result["purchase_platform"] = "taobao"
            
            # 1688 patterns
            ali_match = re.search(
                r'https?://detail\.1688\.com/offer/\d+\.html',
                html, re.IGNORECASE
            )
            if ali_match:
                result["purchase_url"] = ali_match.group(0)
                if not result["purchase_platform"]:
                    result["purchase_platform"] = "1688"
            
            await browser.close()
            
    except Exception as e:
        pass  # Silently fail for individual albums
    
    return result

async def scrape_seller_with_links(seller: Seller, max_pages: int = 20, check_links: bool = True) -> int:
    """
    Scrape a seller and optionally check album pages for buy links
    """
    global automation_state
    
    from .scraper import scrape_seller
    
    automation_state["scraping"]["current_seller"] = seller.name
    
    try:
        # First do normal scraping
        count = await scrape_seller(seller, max_pages)
        automation_state["scraping"]["products_found"] += count
        
        # If check_links is enabled, go back and check some albums for buy links
        if check_links and count > 0:
            # Get recently scraped products for this seller
            products = search_products(seller=seller.name, limit=50)
            
            links_found = 0
            for product in products[:20]:  # Check up to 20 albums per seller
                if product.get("weidian_url") or product.get("taobao_url"):
                    continue  # Already has links
                
                album_url = product.get("url")
                if not album_url:
                    continue
                
                automation_state["scraping"]["albums_checked_for_links"] += 1
                
                links = await scrape_album_for_buy_links(album_url)
                
                if links.get("weidian_url") or links.get("taobao_url") or links.get("purchase_url"):
                    # Update product in database
                    from .database import save_product
                    product.update(links)
                    save_product(product)
                    links_found += 1
                    automation_state["scraping"]["products_with_links"] += 1
                
                # Small delay between album checks
                await asyncio.sleep(0.5)
        
        return count
        
    except Exception as e:
        automation_state["scraping"]["errors"].append(f"{seller.name}: {str(e)}")
        return 0

async def run_full_automation(
    discover_reddit: bool = True,
    scrape_existing: bool = True,
    scrape_discovered: bool = True,
    check_buy_links: bool = True,
    max_pages_per_seller: int = 20,
):
    """
    Run the full automation pipeline:
    1. Discover new sellers from Reddit
    2. Scrape existing sellers 
    3. Scrape newly discovered sellers
    4. Check album pages for buy links
    """
    global automation_state
    
    automation_state["is_running"] = True
    automation_state["started_at"] = int(time.time())
    automation_state["mode"] = "full"
    
    # Reset stats
    automation_state["scraping"]["sellers_done"] = 0
    automation_state["scraping"]["products_found"] = 0
    automation_state["scraping"]["products_with_links"] = 0
    automation_state["scraping"]["albums_checked_for_links"] = 0
    automation_state["scraping"]["errors"] = []
    
    try:
        # Step 1: Discover from Reddit
        if discover_reddit:
            print("Starting Reddit discovery...")
            await discover_sellers_from_reddit()
            print(f"Discovery complete. Found {automation_state['discovery']['sellers_found']} sellers")
        
        # Step 2: Add discovered sellers to queue
        if scrape_discovered:
            new_sellers = await add_discovered_to_scrape_queue()
            print(f"Added {len(new_sellers)} new sellers to scrape queue")
        
        # Step 3: Build scrape list
        sellers_to_scrape = []
        
        if scrape_existing:
            sellers_to_scrape.extend(SELLERS)
        
        if scrape_discovered:
            sellers_to_scrape.extend(dynamic_sellers)
        
        automation_state["scraping"]["total_sellers"] = len(sellers_to_scrape)
        automation_state["scraping"]["is_running"] = True
        
        # Step 4: Scrape all sellers with concurrency
        semaphore = asyncio.Semaphore(3)  # 3 concurrent scrapers
        
        async def scrape_one(seller: Seller):
            async with semaphore:
                count = await scrape_seller_with_links(seller, max_pages_per_seller, check_buy_links)
                automation_state["scraping"]["sellers_done"] += 1
                return count
        
        tasks = [scrape_one(seller) for seller in sellers_to_scrape]
        await asyncio.gather(*tasks)
        
        # Step 5: Re-index in Typesense
        print("Re-indexing in Typesense...")
        all_products = search_products(limit=100000)
        indexed = index_products(all_products)
        print(f"Indexed {indexed} products")
        
        # Update final stats
        automation_state["total_products"] = get_total_products()
        automation_state["scraping"]["is_running"] = False
        
    except Exception as e:
        print(f"Automation error: {e}")
        automation_state["scraping"]["errors"].append(str(e))
    
    finally:
        automation_state["is_running"] = False
        automation_state["scraping"]["is_running"] = False
        automation_state["discovery"]["is_running"] = False

def get_automation_status() -> Dict:
    """Get current automation status"""
    # Calculate runtime if running
    runtime = None
    if automation_state["started_at"]:
        runtime = int(time.time()) - automation_state["started_at"]
    
    return {
        **automation_state,
        "runtime_seconds": runtime,
        "runtime_formatted": format_duration(runtime) if runtime else None,
    }

def format_duration(seconds: int) -> str:
    """Format seconds as human readable duration"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}m {secs}s"
    else:
        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        return f"{hours}h {mins}m"
