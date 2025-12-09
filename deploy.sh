#!/bin/bash
# Deploy Yupoo Search Engine to Ubuntu Server

set -e

echo "==================================="
echo "Yupoo Search Engine Deployment"
echo "==================================="

# Create data directory
mkdir -p data

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build and start
echo "Building and starting services..."
docker-compose up --build -d

# Wait for services
echo "Waiting for services to start..."
sleep 10

# Check health
echo ""
echo "Checking service health..."
echo ""

# Check Typesense
if curl -s http://localhost:8108/health | grep -q "ok"; then
    echo "✅ Typesense is running"
else
    echo "❌ Typesense is not responding"
fi

# Check API
if curl -s http://localhost:8000/ | grep -q "status"; then
    echo "✅ API is running"
else
    echo "❌ API is not responding"
fi

# Check Frontend
if curl -s http://localhost:3000 | grep -q "html"; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "==================================="
echo "Deployment complete!"
echo "==================================="
echo ""
echo "Frontend: http://localhost:3000"
echo "API:      http://localhost:8000"
echo "Typesense: http://localhost:8108"
echo ""
echo "To start scraping, use the 'Scrape All' button in the UI"
echo "or call: curl -X POST http://localhost:8000/api/scrape/start"
echo ""
