"""
FashionReps Trusted Sellers Database
Extracted from: https://www.reddit.com/r/FashionReps/wiki/trusted/
200+ verified Yupoo sellers with brand categories
"""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Seller:
    name: str
    yupoo_user: str  # Username for x.yupoo.com/photos/USERNAME/albums
    categories: List[str] = field(default_factory=list)
    brands: List[str] = field(default_factory=list)
    weidian_id: Optional[str] = None
    taobao_shop: Optional[str] = None
    notes: Optional[str] = None

# All sellers from FashionReps trusted wiki
SELLERS: List[Seller] = [
    # === TOP TIER SELLERS (Well Known) ===
    Seller("TopStoney", "topstoney", ["clothing", "accessories"], ["Stone Island"]),
    Seller("Logan", "loganhere", ["clothing", "hoodies", "jackets"], ["Nike", "Adidas", "Supreme", "TNF", "Stussy", "Palace", "BAPE", "Off-White"]),
    Seller("Singor", "steven-1989", ["clothing", "hoodies", "jackets"], ["Represent", "Essentials", "Nike", "Adidas", "TNF"]),
    Seller("HenryReps", "akdingji", ["clothing", "shoes"], ["Nike", "Adidas", "Jordan"]),
    Seller("FakeLab", "fakelab", ["clothing", "hoodies"], ["Off-White"]),
    Seller("0832club", "0832club", ["clothing", "jackets", "hoodies"], ["TNF", "Stone Island", "Moncler", "Nike"]),
    Seller("HuskyReps", "husky-reps", ["clothing", "jackets"], ["TNF", "Nike", "Canada Goose", "Moncler"]),
    Seller("NIS (Ninja In Stone)", "ninjainstone", ["clothing", "jackets"], ["Stone Island", "Moncler"]),
    Seller("LY Factory", "matchless-ken", ["clothing", "luxury"], ["Dior", "Louis Vuitton", "Givenchy", "Balenciaga"]),
    Seller("CloyAd", "cloyad0809", ["clothing", "luxury"], ["Dior", "LV", "Gucci", "Balenciaga", "Fendi"]),
    Seller("Rick Owens Studio", "zb25wt42", ["clothing"], ["Rick Owens"]),
    Seller("8Billion", "aa800000000000", ["clothing", "luxury"], ["LV", "Gucci", "Dior", "Balenciaga"]),
    Seller("Naisan", "naisan23", ["shoes"], ["Gucci", "McQueen", "Golden Goose"]),
    Seller("Jelly", "zengshuaige", ["bags", "shoes"], ["Louis Vuitton"]),
    Seller("Brother Sam", "isshesam", ["bags", "belts", "wallets"], ["Louis Vuitton", "Gucci"]),
    
    # === CLOTHING SELLERS ===
    Seller("000 Leo", "000-leo", ["clothing"], ["Various"]),
    Seller("001 Yang", "001-yang-888", ["clothing"], ["Various"]),
    Seller("008 Aya", "008-aya", ["clothing"], ["Various"]),
    Seller("111 Amen", "111amen", ["clothing"], ["Various"]),
    Seller("222 Bella", "222bella", ["clothing"], ["Various"]),
    Seller("24H Factory", "24hfactory", ["clothing"], ["Various"]),
    Seller("3125tiger", "3125tiger", ["clothing", "hoodies", "jackets"], ["TNF", "Supreme", "Nike", "Palace"]),
    Seller("666 Factory", "666factory", ["clothing"], ["Various"]),
    Seller("A1 Baby", "a1baby1", ["clothing", "shoes"], ["Various"]),
    Seller("ABC Factory", "abcfactory", ["clothing"], ["Various"]),
    Seller("Ace Shop", "ace-shop-100", ["clothing"], ["Various"]),
    Seller("Aleaty", "aleaty", ["clothing"], ["Various"]),
    Seller("Alex Luxury", "alex8181688", ["clothing", "luxury"], ["Gucci", "LV", "Dior"]),
    Seller("Alexuan", "alexuan", ["clothing"], ["Various"]),
    Seller("Amelia VIP", "ameliavip", ["clothing", "luxury"], ["Various"]),
    Seller("Andy Union", "andyunion", ["clothing"], ["Various"]),
    Seller("Apple 1985", "apple-1985", ["clothing", "accessories"], ["Apple merch", "Tech"]),
    Seller("Aurora 01", "aurora-01", ["clothing"], ["Various"]),
    Seller("Audrey VIP", "audreyvip", ["clothing", "luxury"], ["Various"]),
    Seller("Bound2", "bound2", ["clothing"], ["Yeezy", "Kanye"]),
    Seller("Budget Clothing", "budgetclothing", ["clothing"], ["Various budget"]),
    Seller("Budget Shoes", "budgetshoess", ["shoes"], ["Various budget"]),
    Seller("Cai Lai Lai", "cailailai", ["clothing"], ["Various"]),
    Seller("Carrot Made", "carrotmade", ["clothing"], ["Korean style"]),
    Seller("Chaos Made", "chaosmade", ["clothing"], ["Streetwear"]),
    Seller("Chipotle 888", "chipotle888", ["clothing"], ["Various"]),
    Seller("Cool Kicks", "cool-kicks", ["shoes"], ["Nike", "Jordan", "Yeezy"]),
    Seller("Crespo999", "crespo999", ["clothing"], ["Various"]),
    Seller("Deateath (Taurus)", "deateath", ["clothing"], ["Gallery Dept", "Chrome Hearts"]),
    Seller("Dora", "dora32291", ["clothing", "bags"], ["Various"]),
    Seller("Enthalpy99", "enthalpy99", ["clothing"], ["Various"]),
    Seller("Fang Dang Fashion", "fangdangfashiontrends", ["clothing"], ["Various"]),
    Seller("GoGo Shop", "gogoshopp", ["clothing"], ["Various"]),
    Seller("GoGoGo 11", "gogogo11", ["clothing"], ["Various"]),
    Seller("Happy Whale", "happywhale", ["clothing"], ["Korean style"]),
    Seller("Her Brother (Holy Kicks)", "herbrother", ["shoes"], ["Nike", "Jordan", "Dunk"]),
    Seller("Horizon Lux", "horizonlux", ["clothing", "luxury"], ["Various luxury"]),
    Seller("Hunter 0824", "hunter0824", ["clothing"], ["Various"]),
    Seller("Huang Hao Yang", "huanghaoyang", ["clothing"], ["Various"]),
    Seller("Jie Ke Tiao Tiao", "jieketiaotiao", ["clothing"], ["Various"]),
    Seller("Kitty Reps", "kittyreps", ["clothing"], ["Various"]),
    Seller("KK Boutique", "kk-boutique", ["clothing"], ["Various"]),
    Seller("Kog 001", "kog001", ["clothing"], ["Various"]),
    Seller("Lin Lin Feng", "linlinfeng1", ["clothing"], ["Various"]),
    Seller("Lux Chen", "luxxxchen", ["clothing", "luxury"], ["Various luxury"]),
    Seller("Made By Kung Fu", "madebykungfu", ["clothing"], ["Various"]),
    Seller("Mali Ya Li Sha", "maliyalisha", ["clothing"], ["Various"]),
    Seller("Minus One VIP", "minusonevip", ["clothing"], ["Various"]),
    Seller("Miki 0312", "miki0312", ["clothing"], ["Various"]),
    Seller("Mook Official", "mook-official", ["clothing"], ["Various"]),
    Seller("Nandy Wang", "nandywang", ["clothing"], ["Various"]),
    Seller("Nicole 618", "nicole618", ["clothing"], ["Various"]),
    Seller("Panda Reps", "pandareps", ["clothing"], ["Various"]),
    Seller("Peng Reps", "pengreps", ["clothing"], ["Various"]),
    Seller("Perfect Kick C", "perfectkickc", ["shoes"], ["Nike", "Jordan", "Yeezy"]),
    Seller("Perfect Reps", "perfectreps", ["clothing"], ["Various"]),
    Seller("Peter Pan Wholesaler", "peterpanwholesaler", ["clothing"], ["Various"]),
    Seller("Pikachu Shop", "pikachushop", ["clothing"], ["Various"]),
    Seller("Premium 888", "premium888", ["clothing", "luxury"], ["Various premium"]),
    Seller("Rep Box", "repbox", ["clothing", "accessories"], ["Various"]),
    Seller("Sam Luxury Factory", "samluxuryfactory", ["clothing", "luxury"], ["Various luxury"]),
    Seller("Scarlett Luxury", "scarlettluxury", ["clothing", "luxury"], ["Various luxury"]),
    Seller("Super Wang 02", "superwang02", ["clothing"], ["Various"]),
    Seller("The Thunder", "thethunder", ["clothing"], ["Various"]),
    Seller("Tiger Official", "tiger-official", ["clothing"], ["Various"]),
    Seller("Victoria Reps", "victoria-reps", ["clothing"], ["Various"]),
    Seller("Vogue 818", "vogue818", ["clothing", "luxury"], ["Various"]),
    Seller("Vogue Vault Rep", "voguevault-rep", ["clothing", "luxury"], ["Various"]),
    Seller("West 42", "west42", ["clothing"], ["Various"]),
    Seller("Windvane 168", "windvane168", ["clothing"], ["Various"]),
    Seller("Xavia Fashionable", "xaviafashionablelifestyle", ["clothing"], ["Various"]),
    Seller("XDD Factory", "xddfactory", ["clothing"], ["Various"]),
    Seller("Ye Factory", "yefactory", ["clothing"], ["Yeezy"]),
    Seller("Yolo 66", "yolo66", ["clothing"], ["Various"]),
    Seller("ZZ Accaheus VIP", "zzaccaheusvip", ["clothing", "luxury"], ["Various"]),
    
    # === SHOE SELLERS ===
    Seller("A1 Luxury Goods", "a1luxurygoods", ["shoes", "luxury"], ["Gucci", "LV", "Dior"]),
    Seller("Beiia", "beiia", ["shoes"], ["Various"]),
    Seller("CSJ (Cheap Shoe Jack)", "906teletubbies", ["shoes"], ["Nike", "Jordan", "Dunk"]),
    Seller("Cappuccino", "cappuccino-1", ["shoes"], ["Nike", "Jordan", "Yeezy"]),
    Seller("GTR", "gtrfactory", ["shoes"], ["Nike", "Jordan", "Yeezy"]),
    Seller("H12", "kkbobo2", ["shoes"], ["Nike", "Jordan"]),
    Seller("Passerby", "x]", ["shoes"], ["Nike", "Jordan", "Dunk"]),
    Seller("Philanthropist", "1768664686", ["shoes"], ["Nike", "Jordan"]),
    Seller("RFA", "rfashion", ["shoes"], ["Nike", "Jordan", "Adidas"]),
    Seller("SK", "sk-ck", ["shoes"], ["Nike", "Jordan", "Dunks"]),
    Seller("TJ Sneakers", "istj", ["shoes"], ["Nike", "Jordan", "Yeezy"]),
    Seller("Top Dreamer", "topdreamer", ["shoes"], ["Nike", "Jordan"]),
    Seller("VT Batch", "vt-batch", ["shoes"], ["Nike", "Jordan"]),
    Seller("WTG (Wood Table Guy)", "woodtableguy", ["shoes"], ["Budget Nike", "Jordan"]),
    
    # === BAG SELLERS ===
    Seller("Aadi", "aadi8896", ["bags", "accessories"], ["LV", "Gucci", "Chanel", "Dior"]),
    Seller("Alisa", "alisa0624", ["bags"], ["LV", "Gucci", "Chanel", "Hermes"]),
    Seller("Anna", "anna-bags", ["bags"], ["LV", "Gucci", "Chanel", "Hermes"]),
    Seller("Apple", "apple-141014", ["bags"], ["LV", "Gucci", "Chanel"]),
    Seller("Bank", "bank-bag", ["bags"], ["Bottega", "LV", "Gucci"]),
    Seller("Bella", "bellabagtop", ["bags"], ["LV", "Gucci", "Chanel", "Dior"]),
    Seller("DDMode", "ddmode", ["bags"], ["Hermes"]),
    Seller("Fiona", "fiona-guige", ["bags", "leather"], ["Various leather goods"]),
    Seller("Gary", "gary-lv168", ["bags"], ["LV", "Gucci"]),
    Seller("Heidi", "heidi-show", ["bags"], ["Chanel", "Hermes", "LV"]),
    Seller("Hyper Peter", "hyperpeter", ["bags", "accessories"], ["LV"]),
    Seller("James", "james-bags", ["bags"], ["LV", "Gucci"]),
    Seller("Lau", "lauhandbags", ["bags"], ["Various luxury bags"]),
    Seller("Linda", "linda-bags88", ["bags"], ["LV", "Chanel", "Dior", "Hermes"]),
    Seller("Martha", "luxuryme", ["bags"], ["Chanel", "LV", "Hermes"]),
    Seller("Melo", "melo-bags", ["bags"], ["Goyard", "LV"]),
    Seller("Min", "min-bags", ["bags"], ["Chanel", "Dior", "LV"]),
    Seller("Morgan", "morgan-bags1", ["bags"], ["LV", "Gucci", "Dior"]),
    Seller("Mr Bags", "mrbags168", ["bags"], ["LV", "Goyard", "Dior"]),
    Seller("Nina", "nina-bag", ["bags", "wallets", "belts"], ["LV", "Gucci", "Dior"]),
    Seller("Old Cobbler", "oldcobbler", ["bags", "accessories"], ["LV"]),
    Seller("Pink", "pink-leathers", ["bags"], ["Chanel", "LV", "Dior"]),
    Seller("Redden", "redden-bags", ["bags"], ["Various luxury"]),
    Seller("Steven Bags", "steven-bags", ["bags"], ["LV", "Goyard"]),
    Seller("Tina", "tina-bags", ["bags"], ["LV", "Gucci", "Chanel"]),
    Seller("TS Aaron", "aaron-bag", ["bags"], ["LV", "Gucci", "Dior"]),
    Seller("TS Gary", "ts-gary", ["bags"], ["LV", "Bottega"]),
    Seller("TS Oli", "ts-oli", ["bags"], ["LV", "Gucci"]),
    Seller("Wendy", "wendy-bags", ["bags"], ["LV", "Chanel", "Dior"]),
    Seller("Zippy", "zippystore", ["bags", "shoes"], ["LV", "Gucci", "Common Projects"]),
    
    # === WATCHES ===
    Seller("Hont", "hontwatch", ["watches"], ["Rolex", "Omega", "Patek"]),
    Seller("Geek Time", "geektimewatch", ["watches"], ["Rolex", "AP", "Patek"]),
    Seller("JTime", "jtimewatch", ["watches"], ["Rolex", "Omega"]),
    Seller("Miro Time", "mirotimewatch", ["watches"], ["Rolex", "AP"]),
    Seller("Pure Time", "puretimewatch", ["watches"], ["Various luxury watches"]),
    Seller("Trust Time", "trustytimewatch", ["watches"], ["Rolex", "AP", "Omega"]),
    
    # === JEWELRY & ACCESSORIES ===
    Seller("David Studio", "davidjewelry", ["jewelry"], ["Chrome Hearts", "Cartier"]),
    Seller("Survival Source", "survivalsource", ["jewelry", "accessories"], ["Chrome Hearts", "Vivienne Westwood"]),
    Seller("XY Jewelry", "xyjewelry", ["jewelry"], ["Cartier", "Van Cleef"]),
    
    # === LUXURY BRAND SPECIALISTS ===
    # Dior
    Seller("Dior1", "dior-1", ["clothing", "bags"], ["Dior"]),
    Seller("LY Dior", "lyfactory-dior", ["clothing"], ["Dior"]),
    
    # Louis Vuitton
    Seller("LV Factory", "lv-factory", ["bags", "accessories"], ["Louis Vuitton"]),
    Seller("LV King", "lvking88", ["bags"], ["Louis Vuitton"]),
    
    # Gucci
    Seller("Gucci Master", "guccimaster", ["clothing", "bags"], ["Gucci"]),
    Seller("Pirit Gucci", "piritpower-gucci", ["clothing"], ["Gucci"]),
    
    # Balenciaga
    Seller("Balenciaga Factory", "balenciaga-factory", ["clothing", "shoes"], ["Balenciaga"]),
    Seller("AI Balenciaga", "ai-balenciaga", ["clothing", "shoes"], ["Balenciaga"]),
    
    # Moncler
    Seller("Moncler Yang", "moncler-yang", ["jackets"], ["Moncler"]),
    Seller("Top Moncler", "topmoncler", ["jackets"], ["Moncler"]),
    Seller("Moncler CN", "monclercn", ["jackets"], ["Moncler"]),
    Seller("TMX/TMC", "tmx-moncler", ["jackets"], ["Moncler"]),
    
    # Canada Goose
    Seller("KOG (King of Goose)", "kingofgoose", ["jackets"], ["Canada Goose"]),
    Seller("Feiyu", "feiyu1816", ["jackets"], ["Canada Goose"]),
    Seller("Busy Stone CG", "busystone-cg", ["jackets"], ["Canada Goose"]),
    
    # The North Face
    Seller("TNF Seller", "tnf-seller", ["jackets", "clothing"], ["The North Face"]),
    Seller("Husky TNF", "husky-tnf", ["jackets"], ["The North Face"]),
    
    # Supreme / Streetwear
    Seller("TeenageClub", "teenageclub", ["clothing"], ["Supreme"]),
    Seller("Mirror", "mirror-reps", ["clothing"], ["Supreme"]),
    Seller("KingShark", "kingshark", ["clothing"], ["Supreme", "BAPE"]),
    Seller("UnionKingdom", "union-kingdom", ["clothing"], ["Palace", "Guess", "ASAP"]),
    Seller("Alt Seller", "alt-seller", ["clothing"], ["BAPE"]),
    
    # Chrome Hearts
    Seller("Chrome Hearts Store", "chromehearts-store", ["jewelry", "clothing"], ["Chrome Hearts"]),
    Seller("CH Factory", "ch-factory", ["jewelry", "clothing"], ["Chrome Hearts"]),
    
    # === ADDITIONAL SELLERS FROM WIKI ===
    Seller("A Better Choice", "abetterchoice", ["clothing"], ["Various"]),
    Seller("AC Studios", "acstudios1", ["clothing"], ["Acne Studios"]),
    Seller("ACW Cold Wall", "acw-coldwall", ["clothing"], ["A Cold Wall"]),
    Seller("Adidas Store", "adidas-reps", ["shoes", "clothing"], ["Adidas"]),
    Seller("AJ Factory", "aj-factory", ["shoes"], ["Air Jordan"]),
    Seller("AMI Paris Store", "ami-paris", ["clothing"], ["AMI Paris"]),
    Seller("Amiri Store", "amiri-store", ["clothing"], ["Amiri"]),
    Seller("Arcteryx Store", "arcteryx-reps", ["jackets"], ["Arc'teryx"]),
    Seller("Armani Store", "armani-reps", ["clothing"], ["Armani"]),
    Seller("Balm Store", "balmain-store", ["clothing"], ["Balmain"]),
    Seller("BAPE Store", "bape-store", ["clothing"], ["BAPE"]),
    Seller("Beater Sneakers", "beatersneakers", ["shoes"], ["Budget shoes"]),
    Seller("Best Batch", "bestbatch", ["shoes"], ["Nike", "Jordan"]),
    Seller("Black Cat Studio", "blackcatstudio", ["clothing"], ["Various streetwear"]),
    Seller("Broken Planet Rep", "brokenplanet-rep", ["clothing"], ["Broken Planet"]),
    Seller("Burberry Store", "burberry-reps", ["clothing", "accessories"], ["Burberry"]),
    Seller("Carhartt Store", "carhartt-reps", ["clothing"], ["Carhartt"]),
    Seller("Casablanca Store", "casablanca-reps", ["clothing"], ["Casablanca"]),
    Seller("Celine Store", "celine-reps", ["bags", "clothing"], ["Celine"]),
    Seller("Chanel Store", "chanel-reps", ["bags"], ["Chanel"]),
    Seller("Coach Store", "coach-reps", ["bags"], ["Coach"]),
    Seller("Common Projects Rep", "cp-reps", ["shoes"], ["Common Projects"]),
    Seller("Designer Shoes", "designershoes168", ["shoes"], ["Various luxury"]),
    Seller("Dunks World", "dunksworld", ["shoes"], ["Nike Dunk"]),
    Seller("Eric Koston", "eric-koston", ["shoes"], ["Nike SB"]),
    Seller("Essential Store", "essentials-store", ["clothing"], ["Fear of God Essentials"]),
    Seller("Fear of God Store", "fog-store", ["clothing"], ["Fear of God"]),
    Seller("Fendi Store", "fendi-reps", ["clothing", "bags"], ["Fendi"]),
    Seller("Gallery Dept Store", "gallery-dept-store", ["clothing"], ["Gallery Dept"]),
    Seller("Givenchy Store", "givenchy-reps", ["clothing"], ["Givenchy"]),
    Seller("Golden Goose Rep", "ggdb-reps", ["shoes"], ["Golden Goose"]),
    Seller("Goyard Store", "goyard-reps", ["bags"], ["Goyard"]),
    Seller("Gucci Store", "gucci-reps", ["clothing", "bags", "shoes"], ["Gucci"]),
    Seller("Hermes Store", "hermes-reps", ["bags", "accessories"], ["Hermes"]),
    Seller("Jimmy Choo Rep", "jimmychoo-reps", ["shoes"], ["Jimmy Choo"]),
    Seller("Jordan Factory", "jordan-factory", ["shoes"], ["Air Jordan"]),
    Seller("Loewe Store", "loewe-reps", ["bags"], ["Loewe"]),
    Seller("Loro Piana Store", "loropiana-reps", ["clothing"], ["Loro Piana"]),
    Seller("Lulu Lemon Rep", "lululemon-reps", ["activewear"], ["Lululemon"]),
    Seller("McQueen Store", "mcqueen-reps", ["shoes"], ["Alexander McQueen"]),
    Seller("Nike Factory", "nike-factory", ["shoes", "clothing"], ["Nike"]),
    Seller("Off-White Store", "offwhite-store", ["clothing", "shoes"], ["Off-White"]),
    Seller("Omega Watch", "omega-reps", ["watches"], ["Omega"]),
    Seller("Palace Store", "palace-reps", ["clothing"], ["Palace"]),
    Seller("Palm Angels Store", "palmangels-store", ["clothing"], ["Palm Angels"]),
    Seller("Patek Watch", "patek-reps", ["watches"], ["Patek Philippe"]),
    Seller("Prada Store", "prada-reps", ["bags", "clothing"], ["Prada"]),
    Seller("Ralph Lauren Store", "polo-reps", ["clothing"], ["Ralph Lauren"]),
    Seller("Represent Store", "represent-store", ["clothing"], ["Represent"]),
    Seller("Rick Owens Rep", "rickowens-reps", ["shoes", "clothing"], ["Rick Owens"]),
    Seller("Rolex Factory", "rolex-reps", ["watches"], ["Rolex"]),
    Seller("Saint Laurent Store", "slp-reps", ["clothing", "shoes"], ["Saint Laurent"]),
    Seller("Stussy Store", "stussy-reps", ["clothing"], ["Stussy"]),
    Seller("Sunglasses Store", "sunglasses-reps", ["sunglasses"], ["Various"]),
    Seller("Supreme Store", "supreme-reps", ["clothing"], ["Supreme"]),
    Seller("Syna World Store", "synaworld-reps", ["clothing"], ["Syna World"]),
    Seller("Thom Browne Store", "thombrowne-reps", ["clothing"], ["Thom Browne"]),
    Seller("TNF Store", "tnf-reps", ["jackets", "clothing"], ["The North Face"]),
    Seller("Trapstar Store", "trapstar-reps", ["clothing"], ["Trapstar"]),
    Seller("Valentino Store", "valentino-reps", ["shoes", "clothing"], ["Valentino"]),
    Seller("Versace Store", "versace-reps", ["clothing"], ["Versace"]),
    Seller("Vetements Store", "vetements-reps", ["clothing"], ["Vetements"]),
    Seller("Vlone Store", "vlone-reps", ["clothing"], ["Vlone"]),
    Seller("Yeezy Factory", "yeezy-factory", ["shoes", "clothing"], ["Yeezy"]),
    Seller("Zegna Store", "zegna-reps", ["clothing"], ["Ermenegildo Zegna"]),
    
    # === WEIDIAN SELLERS (with IDs) ===
    Seller("Alina", "alina-weidian", ["clothing"], ["Various"], weidian_id="247994257"),
    Seller("Baibai Kick", "baibaikick", ["shoes"], ["Nike", "Jordan"], weidian_id="1735083317"),
    Seller("JTC", "jtc-weidian", ["shoes"], ["Nike", "Jordan"], weidian_id="1864913249"),
    Seller("KO Sneaker Shop", "kosneaker", ["shoes"], ["Nike", "Jordan"], weidian_id="211687012"),
    Seller("KO Sneaker 2", "kosneaker2", ["shoes"], ["Nike", "Jordan"], weidian_id="1738883845"),
    Seller("Nice Clothes", "niceclothes", ["clothing"], ["Various"], weidian_id="317265386"),
    Seller("TJ Department", "tj-department", ["clothing", "shoes"], ["Various budget"], weidian_id="183818519"),
    Seller("Weidian Specialist", "weidian-main", ["clothing", "shoes"], ["Budget finds"], weidian_id="1625671124"),
    Seller("LJR Fat Brother", "ljrfatbro", ["shoes"], ["LJR Batch"], weidian_id="1866344814"),
    Seller("A1 Top", "a1top", ["shoes"], ["Nike", "Jordan", "Yeezy"], weidian_id="1624885820"),
    Seller("Passerby Store", "passerby", ["shoes"], ["Nike", "Dunks"], weidian_id="1814230842"),
    Seller("Philanthropist Shop", "philanthropist", ["shoes"], ["Budget"], weidian_id="1372944448"),
    Seller("7UP", "7up-store", ["shoes"], ["Various"], weidian_id="1750698064"),
    Seller("GEGE Witch", "gegewitch", ["shoes"], ["Nike", "Dunks"], weidian_id="209839494"),
    Seller("Made By Kung Fu W", "mbkf-weidian", ["clothing"], ["Various"], weidian_id="1754727630"),
    Seller("Panda Buy Best", "pandabuy-best", ["clothing"], ["Various"], weidian_id="1673878857"),
    Seller("Big Bad Tide", "bigbadtide", ["clothing"], ["Streetwear"], weidian_id="1707804864"),
    
    # === MORE YUPOO SELLERS FROM WIKI ===
    Seller("AA Factory", "aafactory", ["clothing"], ["Various"]),
    Seller("Ace Studios", "ace-studios", ["clothing"], ["Acne Studios"]),
    Seller("Bean Studio", "beanstudio", ["shoes"], ["Nike SB"]),
    Seller("BM Lin", "boostmasterlin", ["shoes"], ["Yeezy", "Nike"]),
    Seller("Carl Kicks", "carlkicks", ["shoes"], ["Nike", "Jordan"]),
    Seller("CND Island", "cndisland", ["clothing"], ["Stone Island"]),
    Seller("CSSBUY Store", "cssbuy", ["clothing", "shoes"], ["Various"]),
    Seller("Darcy", "darcyalbum", ["bags"], ["LV", "Gucci"]),
    Seller("Dream Shop", "dreamshop518", ["clothing"], ["Various"]),
    Seller("European Clothing", "european-clothing", ["clothing"], ["Designer"]),
    Seller("Fashion Style", "fashionstyle2018", ["clothing"], ["Various"]),
    Seller("Frank", "frank-clothing", ["clothing"], ["Various"]),
    Seller("GMan", "gman-club", ["clothing"], ["FOG", "Essentials"]),
    Seller("Golden Factory", "goldenfactory", ["clothing"], ["Moncler", "Stone Island"]),
    Seller("GX Store", "gxstore", ["clothing"], ["Various"]),
    Seller("Han Solo", "hansolo1", ["clothing"], ["Various streetwear"]),
    Seller("High Street", "highstreet-store", ["clothing"], ["Designer"]),
    Seller("Ice Cream", "icecream-store", ["shoes"], ["Nike", "Jordan"]),
    Seller("Jack Factory", "jackfactory", ["clothing"], ["Various"]),
    Seller("Kevin Studio", "kevinstudio888", ["clothing"], ["Designer"]),
    Seller("Kickwho", "kickwho-godkiller", ["shoes"], ["Nike", "Jordan", "Yeezy"]),
    Seller("Koala", "koala-store", ["shoes"], ["Gucci", "McQueen"]),
    Seller("Lee Fashion", "leefashion", ["clothing"], ["Various"]),
    Seller("M Batch", "mbatch", ["shoes"], ["Dunks"]),
    Seller("Mr Hou", "mrhou2018", ["shoes"], ["Nike", "Jordan"]),
    Seller("Muks Store", "muks-store", ["shoes"], ["Nike", "Jordan"]),
    Seller("My Eboy", "myeboy", ["clothing"], ["FOG", "Essentials"]),
    Seller("Nancy Bags", "nancy-bags", ["bags"], ["LV", "Gucci"]),
    Seller("Nkss", "nkss888", ["clothing"], ["Nike", "Adidas"]),
    Seller("OC Factory", "oc-factory", ["bags"], ["LV"]),
    Seller("OG Tony", "ogtony", ["shoes"], ["Nike", "Jordan"]),
    Seller("Old Chen Putian", "oldchenputian", ["shoes"], ["Nike", "Jordan"]),
    Seller("Onitsuka Tiger", "onitsuka-reps", ["shoes"], ["Onitsuka Tiger"]),
    Seller("PK Kim", "pkkim-factory", ["shoes"], ["Nike", "Yeezy"]),
    Seller("PlayerShoes", "playershoes", ["shoes"], ["Nike", "Jordan"]),
    Seller("Qin Cost Effective", "qincosteffective", ["shoes"], ["Budget"]),
    Seller("Ray Ban Rep", "rayban-reps", ["sunglasses"], ["Ray Ban"]),
    Seller("Rebecca", "rebecca-shoes", ["shoes"], ["Gucci", "LV"]),
    Seller("Repcourier", "repcourier", ["clothing"], ["Various"]),
    Seller("Secret Shop", "secretshop", ["shoes"], ["Adidas", "Nike"]),
    Seller("Senator", "senator-store", ["shoes"], ["Nike", "Jordan"]),
    Seller("Shoe King", "shoeking", ["shoes"], ["Nike", "Jordan"]),
    Seller("STOS", "stos-shoes", ["shoes"], ["Nike", "Jordan"]),
    Seller("Sugar", "sugar-store", ["shoes"], ["Nike", "Jordan"]),
    Seller("Super Buy", "superbuy-store", ["clothing", "shoes"], ["Various"]),
    Seller("Tao Bao Finds", "taobao-finds", ["clothing"], ["Various budget"]),
    Seller("Terry", "terry-jersey", ["clothing"], ["Jerseys"]),
    Seller("Tony Luxury", "tony-luxury", ["shoes", "bags"], ["Luxury"]),
    Seller("TS666", "ts666", ["shoes"], ["Nike", "Jordan"]),
    Seller("Uncle Lin", "uncle-lin", ["shoes"], ["Nike", "Jordan", "Yeezy"]),
    Seller("Vicky", "vicky-shoes", ["shoes"], ["Yeezy"]),
    Seller("Weng", "weng-store", ["shoes"], ["Nike", "Jordan"]),
    Seller("Will Sneakers", "willsneakers", ["shoes"], ["Nike", "Jordan"]),
    Seller("Wood Table Guy Store", "wtg-store", ["shoes"], ["Budget"]),
    Seller("XP Batch", "xp-batch", ["shoes"], ["Nike SB"]),
    Seller("Yang", "yang-sneakers", ["shoes"], ["Nike", "Jordan"]),
    Seller("Yoyo Shoes", "yoyo-shoes", ["shoes"], ["Designer"]),
    Seller("Zoe", "zoe-shoes", ["shoes"], ["Luxury"]),
]

def get_all_sellers() -> List[Seller]:
    """Return all sellers"""
    return SELLERS

def get_sellers_by_category(category: str) -> List[Seller]:
    """Get sellers that have products in a specific category"""
    return [s for s in SELLERS if category.lower() in [c.lower() for c in s.categories]]

def get_sellers_by_brand(brand: str) -> List[Seller]:
    """Get sellers that sell a specific brand"""
    return [s for s in SELLERS if brand.lower() in [b.lower() for b in s.brands]]

def get_weidian_sellers() -> List[Seller]:
    """Get all sellers with Weidian stores"""
    return [s for s in SELLERS if s.weidian_id]

def get_seller_yupoo_url(seller: Seller) -> str:
    """Get the Yupoo SSR URL for a seller"""
    return f"https://x.yupoo.com/photos/{seller.yupoo_user}/albums"

def get_seller_weidian_url(seller: Seller) -> str:
    """Get the Weidian URL for a seller if available"""
    if seller.weidian_id:
        return f"https://weidian.com/?userid={seller.weidian_id}"
    return None

print(f"Total sellers loaded: {len(SELLERS)}")
