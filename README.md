# Yupoo Search Engine

Search 200+ FashionReps trusted sellers in one place.

## Features

- 🔍 **Fast Search** - Typesense-powered full-text search
- 👥 **200+ Sellers** - All trusted sellers from FashionReps wiki
- 💰 **Real Prices** - Extracts prices from Yupoo titles
- 🏷️ **Brand Detection** - Automatic brand identification
- 📁 **Category Detection** - Auto-categorizes products (bags, shoes, etc.)
- 🛒 **Purchase Links** - Direct links to Weidian/Taobao
- 🖼️ **Image Gallery** - Visual product browsing
- 🚀 **CI/CD Pipeline** - Automatic deployments with GitHub Actions

## CI/CD Setup with Self-Hosted Runner

### 1. Create GitHub Repository

```bash
cd yupoo-scraper
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/yupoo-scraper.git
git push -u origin main
```

### 2. Setup Self-Hosted Runner on Ubuntu Server

SSH into your server and run:

```bash
# Download and extract runner
mkdir -p ~/actions-runner && cd ~/actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf actions-runner-linux-x64-2.311.0.tar.gz

# Install dependencies
sudo ./bin/installdependencies.sh
```

### 3. Configure Runner

1. Go to your GitHub repo → Settings → Actions → Runners → New self-hosted runner
2. Copy the token from the configure command
3. Run on your server:

```bash
cd ~/actions-runner
./config.sh --url https://github.com/YOUR_USERNAME/yupoo-scraper --token YOUR_TOKEN
```

### 4. Install as Service

```bash
sudo ./svc.sh install
sudo ./svc.sh start
```

### 5. Deploy Automatically

Now every push to `main` branch will automatically:
1. Stop existing containers
2. Copy new code to deployment directory
3. Build and start containers
4. Run health checks
5. Show deployment info

## Manual Deployment

```bash
# Copy files to server
scp -r * student@192.168.124.169:~/yupoo-search/

# SSH and deploy
ssh student@192.168.124.169
cd yupoo-search
docker compose up --build -d
```

## Access the App

- **Frontend:** http://192.168.124.169:3000
- **API:** http://192.168.124.169:8000
- **Typesense:** http://192.168.124.169:8108

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search` | GET | Search products |
| `/api/stats` | GET | Get statistics |
| `/api/sellers` | GET | List all sellers |
| `/api/scrape/start` | POST | Start scraping |
| `/api/scrape/status` | GET | Get scrape status |

### Search Parameters

- `q` - Search query
- `seller` - Filter by seller name
- `category` - Filter by category
- `brand` - Filter by brand
- `min_price` - Minimum price
- `max_price` - Maximum price
- `page` - Page number
- `per_page` - Results per page (max 100)

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│      API        │────▶│   Typesense     │
│   (Next.js)     │     │   (FastAPI)     │     │   (Search)      │
│   Port 3000     │     │   Port 8000     │     │   Port 8108     │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │     SQLite      │
                        │   (Database)    │
                        └─────────────────┘
```

## Sellers Included

The system includes 200+ sellers from FashionReps trusted wiki:

**Top Sellers:**
- TopStoney (Stone Island)
- Logan (Nike, Adidas, Supreme)
- Singor (Represent, Essentials)
- FakeLab (Off-White)
- 0832club (TNF, Moncler)
- And 195+ more...

**Categories:**
- Clothing (hoodies, jackets, t-shirts)
- Shoes (sneakers, boots)
- Bags (handbags, backpacks)
- Accessories (belts, hats, jewelry)
- Watches

## License

For personal use only.
