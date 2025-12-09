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

async def scrape_yupoo_page(client: httpx.AsyncClient, url: str, seller_name: str) -> Tuple[List[Dict], Optional[str]]:
    """
    Scrape a single Yupoo page for products
    Returns: (products list, next page URL or None)
    """
    products = []
    next_page = None
    
    try:
        response = await client.get(url, headers=HEADERS, timeout=30.0)
        
        if response.status_code == 404:
            print(f"  Page not found: {url}")
            return [], None
        
        if response.status_code != 200:
            print(f"  HTTP {response.status_code} for {url}")
            return [], None
        
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        # DEBUG: Print page structure
        print(f"    Page length: {len(html)} chars")
        
        # Method 1: Find all album links with album__main class
        albums = soup.find_all('a', class_='album__main')
        
        # Method 2: Find showindex__children container
        if not albums:
            container = soup.find('div', class_='showindex__children')
            if container:
                albums = container.find_all('a', href=True)
        
        # Method 3: Find categories__children container  
        if not albums:
            container = soup.find('div', class_='categories__children')
            if container:
                albums = container.find_all('a', href=True)
        
        # Method 4: Find any links to albums
        if not albums:
            albums = soup.find_all('a', href=re.compile(r'/albums/\d+'))
        
        # Method 5: Find album items by class patterns
        if not albums:
            albums = soup.find_all(['a', 'div'], class_=re.compile(r'album|showindex__item|categories__item'))
        
        print(f"    Found {len(albums)} album elements")
        
        for album in albums:
            try:
                # Get URL - handle both <a> tags and containers with <a> inside
                href = None
                if album.name == 'a':
                    href = album.get('href', '')
                else:
                    link = album.find('a', href=True)
                    if link:
                        href = link.get('href', '')
                
                if not href or '/albums/' not in href:
                    continue
                
                full_url = urljoin(url, href)
                
                # Get title from multiple sources
                title = None
                
                # Try specific Yupoo title classes
                for title_class in ['album__title', 'showindex__title', 'text', 'title']:
                    title_elem = album.find(class_=title_class)
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        break
                
                # Try span with text
                if not title:
                    span = album.find('span')
                    if span:
                        title = span.get_text(strip=True)
                
                # Try title/alt attributes
                if not title:
                    title = album.get('title', '') or album.get('alt', '')
                
                # Try img alt
                if not title:
                    img = album.find('img')
                    if img:
                        title = img.get('alt', '') or img.get('title', '')
                
                if not title:
                    title = "Unknown"
                
                # Get image URL - check all possible attributes
                image_url = None
                img = album.find('img')
                
                if img:
                    # Yupoo image attributes in priority order
                    for attr in ['data-origin-src', 'data-src', 'data-original', 'data-lazy', 'src']:
                        image_url = img.get(attr)
                        if image_url and image_url != '' and 'data:image' not in image_url:
                            break
                    
                    # Also check style attribute for background image
                    if not image_url:
                        style = img.get('style', '')
                        bg_match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
                        if bg_match:
                            image_url = bg_match.group(1)
                
                # Check for background-image in album element itself
                if not image_url:
                    style = album.get('style', '')
                    bg_match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
                    if bg_match:
                        image_url = bg_match.group(1)
                
                # Check for image in nested div
                if not image_url:
                    img_div = album.find('div', class_=re.compile(r'image|thumb|cover|photo'))
                    if img_div:
                        nested_img = img_div.find('img')
                        if nested_img:
                            for attr in ['data-origin-src', 'data-src', 'src']:
                                image_url = nested_img.get(attr)
                                if image_url:
                                    break
                
                # Fix URL format
                if image_url:
                    if image_url.startswith('//'):
                        image_url = 'https:' + image_url
                    elif not image_url.startswith('http'):
                        image_url = urljoin(url, image_url)
                    
                    # Upgrade thumbnail to larger size
                    image_url = re.sub(r'_\d+x\d+', '_800x0x1', image_url)
                
                # Extract price from title
                price = extract_price(title)
                
                # Detect brand
                brand = detect_brand(title)
                
                # Detect category
                category = detect_category(title)
                
                # Generate product ID
                product_id = generate_product_id(seller_name, full_url)
                
                product = {
                    "id": product_id,
                    "seller": seller_name,
                    "title": title,
                    "url": full_url,
                    "image_url": image_url,
                    "price": price,
                    "price_currency": "CNY" if price else None,
                    "brand": brand,
                    "category": category,
                    "detected_category": category,
                    "scraped_at": int(time.time())
                }
                
                # Log first few products for debugging
                if len(products) < 3:
                    print(f"      Product: {title[:50]}... | Image: {image_url[:50] if image_url else 'None'}...")
                
                products.append(product)
                
            except Exception as e:
                print(f"  Error parsing album: {e}")
                continue
        
        # Find next page
        pagination = soup.find('div', class_='pagination') or soup.find('ul', class_='pagination')
        if pagination:
            next_link = pagination.find('a', class_='next') or pagination.find('a', text=re.compile(r'Next|下一页|»'))
            if next_link and next_link.get('href'):
                next_page = urljoin(url, next_link['href'])
        
        # Alternative pagination check
        if not next_page:
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
        
    except Exception as e:
        print(f"  Error scraping page: {e}")
    
    return products, next_page

async def scrape_seller(seller: Seller, max_pages: int = 50) -> int:
    """
    Scrape all products from a seller
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
    
    async with httpx.AsyncClient() as client:
        while current_url and pages_scraped < max_pages:
            pages_scraped += 1
            print(f"  Page {pages_scraped}: {current_url}")
            
            products, next_page = await scrape_yupoo_page(client, current_url, seller.name)
            
            if products:
                print(f"    Found {len(products)} products")
                all_products.extend(products)
            else:
                print(f"    No products found")
                if pages_scraped == 1:
                    # First page has no products, seller might be inactive
                    break
            
            current_url = next_page
            
            # Rate limiting
            await asyncio.sleep(0.5)
        
        # Try to fetch Weidian/Taobao prices for some products
        if all_products and seller.weidian_id:
            print(f"  Checking Weidian prices for {seller.name}...")
            weidian_base = f"https://weidian.com/?userid={seller.weidian_id}"
            
            # Add Weidian URL to products
            for product in all_products:
                product['weidian_url'] = weidian_base
                product['purchase_platform'] = 'weidian'
    
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

async def scrape_multiple_sellers(sellers: List[Seller], max_pages_per_seller: int = 50) -> Dict[str, int]:
    """
    Scrape multiple sellers
    Returns: dict of seller -> product count
    """
    results = {}
    
    for seller in sellers:
        try:
            count = await scrape_seller(seller, max_pages_per_seller)
            results[seller.name] = count
        except Exception as e:
            print(f"Error scraping {seller.name}: {e}")
            results[seller.name] = 0
        
        # Rate limiting between sellers
        await asyncio.sleep(1)
    
    return results

async def quick_test_seller(seller: Seller) -> bool:
    """
    Quick test if a seller's Yupoo page is accessible
    Returns True if accessible and has products
    """
    url = get_seller_yupoo_url(seller)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=HEADERS, timeout=10.0)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check for albums
                has_albums = (
                    soup.find('div', class_='showindex__children') or
                    soup.find('a', class_='album__main') or
                    soup.find('a', href=re.compile(r'/albums/\d+'))
                )
                
                return bool(has_albums)
            
        except Exception:
            pass
    
    return False

# Main scraping function for external use
def run_scraper(sellers: List[Seller], max_pages: int = 50) -> Dict[str, int]:
    """Run the scraper (sync wrapper for async function)"""
    return asyncio.run(scrape_multiple_sellers(sellers, max_pages))

def test_single_seller(seller: Seller) -> bool:
    """Test a single seller (sync wrapper)"""
    return asyncio.run(quick_test_seller(seller))
