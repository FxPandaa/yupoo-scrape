"""
Enhanced Yupoo Scraper with Weidian/Taobao Price Extraction
Supports: Yupoo SSR pages, Weidian, Taobao, 1688 price lookups
Image-based category detection
"""

import httpx
import asyncio
import re
import hashlib
import time
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
import json

from .database import (
    save_products_batch, detect_category, log_scrape_start, 
    log_scrape_complete, get_category_mappings
)
from .sellers import Seller, get_seller_yupoo_url

# User agent to avoid blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# Price extraction patterns
PRICE_PATTERNS = [
    r'[¥￥]\s*(\d+(?:\.\d{1,2})?)',           # ¥ or ￥ followed by number
    r'(\d+(?:\.\d{1,2})?)\s*[¥￥]',           # Number followed by ¥
    r'CNY\s*(\d+(?:\.\d{1,2})?)',             # CNY prefix
    r'(\d+(?:\.\d{1,2})?)\s*CNY',             # CNY suffix
    r'RMB\s*(\d+(?:\.\d{1,2})?)',             # RMB prefix
    r'(\d+(?:\.\d{1,2})?)\s*RMB',             # RMB suffix
    r'Yuan\s*(\d+(?:\.\d{1,2})?)',            # Yuan prefix
    r'(\d+(?:\.\d{1,2})?)\s*Yuan',            # Yuan suffix
    r'\$\s*(\d+(?:\.\d{1,2})?)',              # Dollar sign
    r'(\d+(?:\.\d{1,2})?)\s*\$',              # Dollar suffix
    r'(?:price|价格)[:\s]*(\d+(?:\.\d{1,2})?)', # Price label
]

# Brand detection patterns
BRAND_PATTERNS = {
    "nike": ["nike", "swoosh", "air max", "air force", "dunk", "blazer"],
    "adidas": ["adidas", "yeezy", "boost", "ultraboost", "nmd", "superstar"],
    "jordan": ["jordan", "aj1", "aj4", "aj11", "retro"],
    "supreme": ["supreme", "box logo", "bogo"],
    "off-white": ["off-white", "off white", "virgil"],
    "gucci": ["gucci", "gg"],
    "louis vuitton": ["louis vuitton", "lv", "monogram"],
    "dior": ["dior", "cd", "saddle"],
    "balenciaga": ["balenciaga", "triple s", "speed trainer"],
    "prada": ["prada", "re-nylon"],
    "fendi": ["fendi", "ff"],
    "burberry": ["burberry", "tb"],
    "stone island": ["stone island", "si", "compass"],
    "moncler": ["moncler", "maya"],
    "canada goose": ["canada goose", "cg"],
    "the north face": ["north face", "tnf", "nuptse"],
    "bape": ["bape", "bathing ape", "shark hoodie"],
    "palace": ["palace", "tri-ferg"],
    "stussy": ["stussy", "stüssy"],
    "chrome hearts": ["chrome hearts", "ch"],
    "fear of god": ["fear of god", "fog", "essentials"],
    "represent": ["represent"],
    "gallery dept": ["gallery dept"],
    "trapstar": ["trapstar"],
    "rick owens": ["rick owens", "drkshdw"],
    "acne studios": ["acne studios", "acne"],
    "ami": ["ami paris", "ami"],
    "arcteryx": ["arcteryx", "arc'teryx"],
    "palm angels": ["palm angels"],
    "vetements": ["vetements"],
    "rhude": ["rhude"],
    "amiri": ["amiri"],
    "casablanca": ["casablanca"],
    "hermes": ["hermes", "hermès", "birkin", "kelly"],
    "chanel": ["chanel", "cc"],
    "bottega veneta": ["bottega", "bv", "intrecciato"],
    "loewe": ["loewe", "puzzle"],
    "celine": ["celine", "céline"],
    "goyard": ["goyard"],
    "golden goose": ["golden goose", "ggdb"],
    "alexander mcqueen": ["mcqueen", "alexander mcqueen"],
    "common projects": ["common projects", "cp"],
    "valentino": ["valentino", "vltn"],
    "versace": ["versace", "medusa"],
    "givenchy": ["givenchy"],
    "ysl": ["ysl", "saint laurent", "yves saint laurent"],
    "thom browne": ["thom browne"],
    "loro piana": ["loro piana"],
    "zegna": ["zegna", "ermenegildo"],
    "rolex": ["rolex", "submariner", "datejust", "daytona"],
    "omega": ["omega", "speedmaster", "seamaster"],
    "cartier": ["cartier", "love", "juste un clou"],
    "vivienne westwood": ["vivienne westwood", "orb"],
}

def generate_product_id(seller: str, url: str) -> str:
    """Generate unique product ID from seller and URL"""
    unique_str = f"{seller}_{url}"
    return hashlib.md5(unique_str.encode()).hexdigest()[:16]

def extract_price(text: str) -> Optional[float]:
    """Extract price from text using multiple patterns"""
    if not text:
        return None
    
    for pattern in PRICE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                price = float(match.group(1))
                if 1 <= price <= 50000:  # Reasonable price range
                    return price
            except (ValueError, IndexError):
                continue
    
    return None

def detect_brand(title: str) -> Optional[str]:
    """Detect brand from product title"""
    title_lower = title.lower()
    
    for brand, keywords in BRAND_PATTERNS.items():
        for keyword in keywords:
            if keyword in title_lower:
                return brand.title()
    
    return None

def extract_purchase_links(html: str, base_url: str) -> Dict[str, str]:
    """Extract Weidian, Taobao, 1688 links from page"""
    links = {}
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all links on page
    for a in soup.find_all('a', href=True):
        href = a['href']
        
        # Weidian links
        if 'weidian.com' in href:
            links['weidian'] = href
        
        # Taobao links
        elif 'taobao.com' in href or 'tmall.com' in href:
            links['taobao'] = href
        
        # 1688 links
        elif '1688.com' in href:
            links['1688'] = href
    
    # Also check text content for links
    text_content = soup.get_text()
    
    # Weidian item pattern
    weidian_match = re.search(r'weidian\.com/item\.html\?itemID=(\d+)', text_content)
    if weidian_match and 'weidian' not in links:
        links['weidian'] = f"https://weidian.com/item.html?itemID={weidian_match.group(1)}"
    
    # Taobao item pattern
    taobao_match = re.search(r'item\.taobao\.com/item\.htm\?id=(\d+)', text_content)
    if taobao_match and 'taobao' not in links:
        links['taobao'] = f"https://item.taobao.com/item.htm?id={taobao_match.group(1)}"
    
    return links

async def fetch_weidian_price(client: httpx.AsyncClient, url: str) -> Optional[float]:
    """Fetch price from Weidian product page"""
    try:
        # Extract item ID
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        item_id = params.get('itemID', [None])[0] or params.get('itemId', [None])[0]
        
        if not item_id:
            return None
        
        # Try mobile API endpoint (more reliable)
        api_url = f"https://weidian.com/api/item/get?itemId={item_id}"
        
        response = await client.get(api_url, headers=HEADERS, timeout=10.0)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('result'):
                    item = data['result'].get('item', {})
                    price = item.get('price') or item.get('minPrice')
                    if price:
                        return float(price)
            except (json.JSONDecodeError, ValueError):
                pass
        
        # Fallback: scrape page directly
        response = await client.get(url, headers=HEADERS, timeout=10.0)
        if response.status_code == 200:
            price = extract_price(response.text)
            if price:
                return price
        
    except Exception as e:
        print(f"Error fetching Weidian price: {e}")
    
    return None

async def fetch_taobao_price(client: httpx.AsyncClient, url: str) -> Optional[float]:
    """Fetch price from Taobao product page"""
    try:
        # Extract item ID
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        item_id = params.get('id', [None])[0]
        
        if not item_id:
            return None
        
        # Try to get page (often blocked, but worth trying)
        response = await client.get(url, headers=HEADERS, timeout=10.0, follow_redirects=True)
        
        if response.status_code == 200:
            price = extract_price(response.text)
            if price:
                return price
        
    except Exception as e:
        print(f"Error fetching Taobao price: {e}")
    
    return None

# Purchase link patterns for extraction
PURCHASE_LINK_PATTERNS = {
    "weidian": [
        r'https?://(?:www\.)?weidian\.com/item\.html\?itemID=\d+',
        r'https?://shop\d+\.v\.weidian\.com/item\.html\?itemID=\d+',
        r'https?://(?:www\.)?weidian\.com/\?userid=\d+',
    ],
    "taobao": [
        r'https?://item\.taobao\.com/item\.htm\?[^"\s]+id=\d+',
        r'https?://(?:[\w]+\.)?taobao\.com/[^"\s]+',
        r'https?://(?:www\.)?tmall\.com/[^"\s]+',
    ],
    "1688": [
        r'https?://detail\.1688\.com/offer/\d+\.html',
        r'https?://(?:www\.)?1688\.com/[^"\s]+',
    ],
    "pandabuy": [
        r'https?://(?:www\.)?pandabuy\.com/product\?[^"\s]+',
    ],
    "superbuy": [
        r'https?://(?:www\.)?superbuy\.com/[^"\s]+',
    ],
    "wegobuy": [
        r'https?://(?:www\.)?wegobuy\.com/[^"\s]+',
    ],
    "cssbuy": [
        r'https?://(?:www\.)?cssbuy\.com/[^"\s]+',
    ],
}

def extract_all_purchase_links(html: str) -> Dict[str, str]:
    """Extract all purchase links from HTML content"""
    links = {}
    
    for platform, patterns in PURCHASE_LINK_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match and platform not in links:
                links[platform] = match.group(0)
                break
    
    return links

async def scrape_album_for_links(browser, album_url: str) -> Dict[str, any]:
    """
    Scrape a single Yupoo album page to find purchase links
    Returns dict with weidian_url, taobao_url, price, etc.
    """
    result = {
        "weidian_url": None,
        "taobao_url": None,
        "1688_url": None,
        "agent_url": None,
        "purchase_price": None,
        "purchase_platform": None,
    }
    
    try:
        page = await browser.new_page()
        await page.goto(album_url, wait_until='networkidle', timeout=20000)
        await page.wait_for_timeout(1000)
        
        html = await page.content()
        
        # Extract purchase links
        links = extract_all_purchase_links(html)
        
        if 'weidian' in links:
            result['weidian_url'] = links['weidian']
            result['purchase_platform'] = 'weidian'
        
        if 'taobao' in links:
            result['taobao_url'] = links['taobao']
            if not result['purchase_platform']:
                result['purchase_platform'] = 'taobao'
        
        if '1688' in links:
            result['1688_url'] = links['1688']
            if not result['purchase_platform']:
                result['purchase_platform'] = '1688'
        
        # Check for agent links
        for platform in ['pandabuy', 'superbuy', 'wegobuy', 'cssbuy']:
            if platform in links:
                result['agent_url'] = links[platform]
                break
        
        # Try to extract price from page content
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for price in description or title
        desc = soup.find('div', class_='showalbum__message')
        if desc:
            text = desc.get_text()
            price = extract_price(text)
            if price:
                result['purchase_price'] = price
        
        await page.close()
        
    except Exception as e:
        pass  # Silently fail for individual albums
    
    return result

# Playwright browser instance (singleton)
_browser = None
_playwright = None

async def get_browser():
    """Get or create Playwright browser instance"""
    global _browser, _playwright
    if _browser is None:
        from playwright.async_api import async_playwright
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
    return _browser

async def close_browser():
    """Close Playwright browser and cleanup resources"""
    global _browser, _playwright
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None

async def scrape_yupoo_page_playwright(url: str, seller_name: str) -> Tuple[List[Dict], Optional[str]]:
    """
    Scrape a Yupoo page using Playwright (JavaScript rendering)
    Returns: (products list, next page URL or None)
    """
    products = []
    next_page = None
    
    try:
        browser = await get_browser()
        page = await browser.new_page()
        
        # Set viewport and user agent
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        print(f"    Loading page with Playwright...")
        await page.goto(url, wait_until='networkidle', timeout=30000)
        
        # Wait for albums to load
        await page.wait_for_timeout(2000)
        
        # Get page content after JavaScript execution
        html = await page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        print(f"    Page length: {len(html)} chars (after JS)")
        
        # Find all album items - Yupoo uses showindex__children container
        albums = []
        
        # Method 1: Find showindex__children and get album items
        container = soup.find('div', class_='showindex__children')
        if container:
            albums = container.find_all('a', class_='album__main')
            if not albums:
                albums = container.find_all('a', href=True)
        
        # Method 2: Find categories page structure
        if not albums:
            container = soup.find('div', class_='categories__children')
            if container:
                albums = container.find_all('a', href=True)
        
        # Method 3: Find by class pattern
        if not albums:
            albums = soup.find_all('a', class_='album__main')
        
        # Method 4: Find any album links
        if not albums:
            albums = soup.find_all('a', href=re.compile(r'/albums/\d+'))
        
        print(f"    Found {len(albums)} album elements")
        
        for album in albums:
            try:
                href = album.get('href', '')
                if not href or '/albums/' not in href:
                    continue
                
                full_url = urljoin(url, href)
                
                # Get title
                title_elem = album.find(class_='album__title')
                title = title_elem.get_text(strip=True) if title_elem else None
                
                if not title:
                    # Try to get from all text in album
                    title = album.get_text(strip=True)
                    # Clean up - remove image count prefix like "11 "
                    title = re.sub(r'^\d+\s+', '', title)
                
                if not title:
                    title = "Unknown"
                
                # Get image URL - Yupoo loads images with data-src or data-origin-src
                image_url = None
                img = album.find('img')
                
                if img:
                    # Priority order for Yupoo images
                    for attr in ['data-origin-src', 'data-src', 'src']:
                        val = img.get(attr)
                        if val and not val.startswith('data:'):
                            image_url = val
                            break
                
                # Check for background-image style
                if not image_url:
                    # Check album__cover div
                    cover = album.find('div', class_='album__cover')
                    if cover:
                        style = cover.get('style', '')
                        bg_match = re.search(r'url\(["\']?([^"\')\s]+)["\']?\)', style)
                        if bg_match:
                            image_url = bg_match.group(1)
                
                # Fix URL
                if image_url:
                    if image_url.startswith('//'):
                        image_url = 'https:' + image_url
                    elif not image_url.startswith('http'):
                        image_url = urljoin(url, image_url)
                    # Get larger image
                    image_url = re.sub(r'_\d+x\d+', '_800x0x1', image_url)
                
                # Extract info from title
                price = extract_price(title)
                brand = detect_brand(title)
                category = detect_category(title)
                product_id = generate_product_id(seller_name, full_url)
                
                product = {
                    "id": product_id,
                    "seller": seller_name,
                    "title": title[:200] if title else "Unknown",
                    "url": full_url,
                    "image_url": image_url,
                    "price": price,
                    "price_currency": "CNY" if price else None,
                    "brand": brand,
                    "category": category,
                    "detected_category": category,
                    "scraped_at": int(time.time())
                }
                
                if len(products) < 3:
                    print(f"      Product: {title[:40]}... | Image: {'Yes' if image_url else 'No'}")
                
                products.append(product)
                
            except Exception as e:
                print(f"  Error parsing album: {e}")
                continue
        
        # Find next page
        next_link = soup.find('a', class_='pager__next')
        if next_link and next_link.get('href'):
            next_page = urljoin(url, next_link['href'])
        else:
            # Check for pagination numbers
            page_links = soup.find_all('a', href=re.compile(r'page=\d+'))
            if page_links:
                current_page = 1
                page_match = re.search(r'page=(\d+)', url)
                if page_match:
                    current_page = int(page_match.group(1))
                
                for link in page_links:
                    href = link.get('href', '')
                    match = re.search(r'page=(\d+)', href)
                    if match and int(match.group(1)) == current_page + 1:
                        next_page = urljoin(url, href)
                        break
        
        await page.close()
        
    except Exception as e:
        print(f"  Error scraping page: {e}")
        import traceback
        traceback.print_exc()
    
    return products, next_page

async def scrape_yupoo_page(url: str, seller_name: str) -> Tuple[List[Dict], Optional[str]]:
    """
    Scrape a single Yupoo page for products using Playwright
    Returns: (products list, next page URL or None)
    """
    # Use Playwright version for proper JS rendering
    return await scrape_yupoo_page_playwright(url, seller_name)

async def scrape_seller(seller: Seller, max_pages: int = 50) -> int:
    """
    Scrape all products from a seller using Playwright for JS rendering
    Returns: number of products found
    """
    print(f"\n{'='*60}")
    print(f"Scraping: {seller.name} ({seller.yupoo_user})")
    print(f"{'='*60}")
    
    log_id = log_scrape_start(seller.name)
    
    all_products = []
    pages_scraped = 0
    
    base_url = get_seller_yupoo_url(seller)
    current_url = base_url
    
    # Get shared Playwright browser
    browser = await get_browser()
    page = await browser.new_page()
    
    try:
        while current_url and pages_scraped < max_pages:
            pages_scraped += 1
            print(f"  Page {pages_scraped}: {current_url}")
            
            # Use Playwright to scrape (handles JavaScript rendering)
            products, next_page = await scrape_yupoo_page(current_url, seller.name)
            
            if products:
                print(f"    Found {len(products)} products")
                all_products.extend(products)
            else:
                print(f"    No products found")
                if pages_scraped == 1:
                    # First page has no products, seller might be inactive
                    break
            
            current_url = next_page
            
            # Small delay between pages
            await asyncio.sleep(0.5)
        
        # Try to fetch Weidian/Taobao prices for some products
        if all_products and seller.weidian_id:
            print(f"  Checking Weidian prices for {seller.name}...")
            weidian_base = f"https://weidian.com/?userid={seller.weidian_id}"
            
            # Add Weidian URL to products
            for product in all_products:
                product['weidian_url'] = weidian_base
                product['purchase_platform'] = 'weidian'
    finally:
        await page.close()
    
    # Save products to database
    if all_products:
        saved = save_products_batch(all_products)
        print(f"  Saved {saved} products to database")
    
    log_scrape_complete(
        log_id, 
        len(all_products), 
        pages_scraped, 
        "completed" if all_products else "no_products"
    )
    
    return len(all_products)

async def scrape_multiple_sellers(sellers: List[Seller], max_pages_per_seller: int = 50, concurrent_limit: int = 5) -> Dict[str, int]:
    """
    Scrape multiple sellers CONCURRENTLY for speed
    Returns: dict of seller -> product count
    """
    results = {}
    semaphore = asyncio.Semaphore(concurrent_limit)
    
    async def scrape_with_limit(seller: Seller) -> Tuple[str, int]:
        async with semaphore:
            try:
                count = await scrape_seller(seller, max_pages_per_seller)
                return (seller.name, count)
            except Exception as e:
                print(f"Error scraping {seller.name}: {e}")
                return (seller.name, 0)
    
    # Run all sellers concurrently (limited by semaphore)
    tasks = [scrape_with_limit(seller) for seller in sellers]
    completed = await asyncio.gather(*tasks)
    
    for name, count in completed:
        results[name] = count
    
    return results

async def quick_test_seller(seller: Seller) -> bool:
    """
    Quick test if a seller's Yupoo page is accessible
    Returns True if accessible (basic HTTP check, no JS rendering needed)
    """
    url = get_seller_yupoo_url(seller)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=HEADERS, timeout=10.0)
            # Just check if page loads - 200 status is enough
            return response.status_code == 200
            
        except Exception:
            pass
    
    return False

# Main scraping function for external use
async def _run_scraper_async(sellers: List[Seller], max_pages: int = 50) -> Dict[str, int]:
    """Run scraper with proper browser cleanup"""
    try:
        results = await scrape_multiple_sellers(sellers, max_pages)
        return results
    finally:
        # Always close browser when done
        await close_browser()

def run_scraper(sellers: List[Seller], max_pages: int = 50) -> Dict[str, int]:
    """Run the scraper (sync wrapper for async function)"""
    return asyncio.run(_run_scraper_async(sellers, max_pages))

def test_single_seller(seller: Seller) -> bool:
    """Test a single seller (sync wrapper)"""
    return asyncio.run(quick_test_seller(seller))
