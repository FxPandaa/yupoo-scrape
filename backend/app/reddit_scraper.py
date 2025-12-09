"""
Reddit Scraper for FashionReps Seller Discovery
Scrapes r/FashionReps, r/DesignerReps, r/RepLadies for new seller links
"""

import httpx
import re
import asyncio
from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# Subreddits to scrape for seller links
SUBREDDITS = [
    "FashionReps",
    "DesignerReps",
    "RepLadies",
    "Repsneakers",
    "QualityReps",
    "CoutureReps",
]

# Platform patterns
PLATFORM_PATTERNS = {
    "yupoo": [
        r'https?://(?:x\.)?(?:[\w-]+\.)?yupoo\.com/(?:photos/)?[\w-]+',
        r'(?:[\w-]+)\.x\.yupoo\.com',
    ],
    "weidian": [
        r'https?://(?:www\.)?weidian\.com/item\.html\?itemID=(\d+)',
        r'https?://(?:www\.)?weidian\.com/\?userid=(\d+)',
        r'https?://shop\d+\.v\.weidian\.com',
    ],
    "taobao": [
        r'https?://item\.taobao\.com/item\.htm\?.*?id=(\d+)',
        r'https?://(?:www\.)?taobao\.com/.*',
        r'https?://[\w]+\.taobao\.com',
    ],
    "1688": [
        r'https?://detail\.1688\.com/offer/(\d+)\.html',
        r'https?://(?:www\.)?1688\.com',
    ],
    "pandabuy": [
        r'https?://(?:www\.)?pandabuy\.com/product\?url=([^&\s]+)',
    ],
    "superbuy": [
        r'https?://(?:www\.)?superbuy\.com/en/page/buy\?url=([^&\s]+)',
    ],
    "cssbuy": [
        r'https?://(?:www\.)?cssbuy\.com',
    ],
    "wegobuy": [
        r'https?://(?:www\.)?wegobuy\.com',
    ],
}

@dataclass
class DiscoveredSeller:
    """A seller discovered from Reddit"""
    name: str
    yupoo_url: str
    yupoo_user: str
    source_subreddit: str
    source_url: str
    weidian_id: Optional[str] = None
    taobao_shop: Optional[str] = None
    mentioned_brands: List[str] = None
    upvotes: int = 0
    discovered_at: str = None
    
    def __post_init__(self):
        if self.mentioned_brands is None:
            self.mentioned_brands = []
        if self.discovered_at is None:
            self.discovered_at = datetime.now().isoformat()


class RedditSellerDiscovery:
    """Discover new sellers from Reddit rep communities"""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        }
        self.discovered_sellers: Dict[str, DiscoveredSeller] = {}
        self.known_yupoo_users: Set[str] = set()
    
    def set_known_sellers(self, yupoo_users: List[str]):
        """Set list of already known sellers to avoid duplicates"""
        self.known_yupoo_users = set(u.lower() for u in yupoo_users)
    
    async def fetch_subreddit_posts(self, subreddit: str, limit: int = 100, time_filter: str = "month") -> List[Dict]:
        """Fetch posts from a subreddit using Reddit's JSON API"""
        posts = []
        
        # Reddit JSON endpoints
        endpoints = [
            f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}",
            f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}",
            f"https://www.reddit.com/r/{subreddit}/top.json?t={time_filter}&limit={limit}",
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint in endpoints:
                try:
                    response = await client.get(endpoint, headers=self.headers, timeout=15.0)
                    if response.status_code == 200:
                        data = response.json()
                        if "data" in data and "children" in data["data"]:
                            for child in data["data"]["children"]:
                                post = child.get("data", {})
                                posts.append({
                                    "title": post.get("title", ""),
                                    "selftext": post.get("selftext", ""),
                                    "url": post.get("url", ""),
                                    "permalink": f"https://reddit.com{post.get('permalink', '')}",
                                    "upvotes": post.get("ups", 0),
                                    "subreddit": subreddit,
                                    "created_utc": post.get("created_utc", 0),
                                })
                    await asyncio.sleep(1)  # Rate limiting
                except Exception as e:
                    print(f"Error fetching r/{subreddit}: {e}")
        
        return posts
    
    def extract_yupoo_users(self, text: str) -> List[str]:
        """Extract Yupoo usernames from text"""
        users = set()
        
        # Pattern 1: x.yupoo.com format
        matches = re.findall(r'(?:https?://)?(\w+)\.x\.yupoo\.com', text, re.IGNORECASE)
        users.update(matches)
        
        # Pattern 2: yupoo.com/photos/username
        matches = re.findall(r'yupoo\.com/photos/(\w+)', text, re.IGNORECASE)
        users.update(matches)
        
        # Pattern 3: x.yupoo.com/photos/username
        matches = re.findall(r'x\.yupoo\.com/photos/(\w+)', text, re.IGNORECASE)
        users.update(matches)
        
        return list(users)
    
    def extract_weidian_ids(self, text: str) -> List[str]:
        """Extract Weidian shop/item IDs from text"""
        ids = set()
        
        # Shop ID
        matches = re.findall(r'weidian\.com/\?userid=(\d+)', text, re.IGNORECASE)
        ids.update(matches)
        
        # Item ID (can derive shop from this)
        matches = re.findall(r'weidian\.com/item\.html\?itemID=(\d+)', text, re.IGNORECASE)
        ids.update(matches)
        
        return list(ids)
    
    def extract_taobao_shops(self, text: str) -> List[str]:
        """Extract Taobao shop identifiers from text"""
        shops = set()
        
        matches = re.findall(r'([\w]+)\.taobao\.com', text, re.IGNORECASE)
        for m in matches:
            if m.lower() not in ['item', 'www', 'shop', 's']:
                shops.add(m)
        
        return list(shops)
    
    def extract_purchase_links(self, text: str) -> Dict[str, List[str]]:
        """Extract all purchase links from text"""
        links = {
            "weidian": [],
            "taobao": [],
            "1688": [],
            "pandabuy": [],
            "superbuy": [],
        }
        
        for platform, patterns in PLATFORM_PATTERNS.items():
            if platform in links:
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        # If pattern has groups, we get the group content
                        for m in matches:
                            if isinstance(m, tuple):
                                links[platform].extend([x for x in m if x])
                            else:
                                links[platform].append(m)
        
        return links
    
    def extract_mentioned_brands(self, text: str) -> List[str]:
        """Extract brand mentions from text"""
        brands = set()
        
        brand_keywords = [
            "nike", "adidas", "jordan", "yeezy", "supreme", "off-white",
            "gucci", "louis vuitton", "lv", "dior", "balenciaga", "prada",
            "fendi", "burberry", "stone island", "moncler", "canada goose",
            "north face", "bape", "palace", "chrome hearts", "fear of god",
            "essentials", "represent", "gallery dept", "trapstar", "rhude",
            "amiri", "rick owens", "bottega", "hermes", "chanel", "goyard",
            "celine", "loewe", "arcteryx", "palm angels", "vetements",
        ]
        
        text_lower = text.lower()
        for brand in brand_keywords:
            if brand in text_lower:
                brands.add(brand.title())
        
        return list(brands)
    
    async def discover_from_subreddit(self, subreddit: str) -> List[DiscoveredSeller]:
        """Discover new sellers from a subreddit"""
        print(f"  Scanning r/{subreddit}...")
        
        posts = await self.fetch_subreddit_posts(subreddit)
        new_sellers = []
        
        for post in posts:
            # Combine title and text for searching
            full_text = f"{post['title']} {post['selftext']} {post['url']}"
            
            # Find Yupoo links
            yupoo_users = self.extract_yupoo_users(full_text)
            
            for user in yupoo_users:
                user_lower = user.lower()
                
                # Skip if already known
                if user_lower in self.known_yupoo_users:
                    continue
                
                # Skip if already discovered in this session
                if user_lower in self.discovered_sellers:
                    continue
                
                # Extract additional info
                weidian_ids = self.extract_weidian_ids(full_text)
                taobao_shops = self.extract_taobao_shops(full_text)
                brands = self.extract_mentioned_brands(full_text)
                
                seller = DiscoveredSeller(
                    name=user.title(),
                    yupoo_url=f"https://{user}.x.yupoo.com/albums",
                    yupoo_user=user,
                    source_subreddit=subreddit,
                    source_url=post['permalink'],
                    weidian_id=weidian_ids[0] if weidian_ids else None,
                    taobao_shop=taobao_shops[0] if taobao_shops else None,
                    mentioned_brands=brands,
                    upvotes=post['upvotes'],
                )
                
                self.discovered_sellers[user_lower] = seller
                new_sellers.append(seller)
                
                print(f"    Found: {user} (upvotes: {post['upvotes']}, brands: {', '.join(brands[:3])})")
        
        return new_sellers
    
    async def discover_all(self) -> List[DiscoveredSeller]:
        """Discover sellers from all subreddits"""
        print("\n" + "="*60)
        print("Reddit Seller Discovery")
        print("="*60)
        
        all_sellers = []
        
        for subreddit in SUBREDDITS:
            try:
                sellers = await self.discover_from_subreddit(subreddit)
                all_sellers.extend(sellers)
                await asyncio.sleep(2)  # Rate limiting between subreddits
            except Exception as e:
                print(f"  Error scanning r/{subreddit}: {e}")
        
        print(f"\nTotal new sellers discovered: {len(all_sellers)}")
        return all_sellers


async def discover_new_sellers(known_users: List[str]) -> List[Dict]:
    """
    Main function to discover new sellers from Reddit
    Returns list of seller dicts ready to add to sellers.py
    """
    discovery = RedditSellerDiscovery()
    discovery.set_known_sellers(known_users)
    
    sellers = await discovery.discover_all()
    
    return [
        {
            "name": s.name,
            "yupoo_user": s.yupoo_user,
            "weidian_id": s.weidian_id,
            "taobao_shop": s.taobao_shop,
            "categories": [],
            "brands": s.mentioned_brands,
            "source": f"reddit:r/{s.source_subreddit}",
            "upvotes": s.upvotes,
        }
        for s in sellers
    ]


# Standalone test
if __name__ == "__main__":
    import asyncio
    
    async def test():
        sellers = await discover_new_sellers([])
        for s in sellers[:10]:
            print(f"- {s['name']}: {s['yupoo_user']} (brands: {s['brands']})")
    
    asyncio.run(test())
