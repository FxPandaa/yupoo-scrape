#!/bin/bash
# Self-hosted GitHub Actions Runner Setup Script
# Run this on your Ubuntu server (192.168.124.169)

set -e

RUNNER_VERSION="2.311.0"
REPO_URL="$1"  # Pass your GitHub repo URL as argument

if [ -z "$REPO_URL" ]; then
    echo "Usage: ./setup-runner.sh <github-repo-url>"
    echo "Example: ./setup-runner.sh https://github.com/username/yupoo-scraper"
    exit 1
fi

echo "=========================================="
echo "GitHub Actions Self-Hosted Runner Setup"
echo "=========================================="

# Create runner directory
mkdir -p ~/actions-runner
cd ~/actions-runner

# Download runner
echo "Downloading GitHub Actions Runner..."
curl -o actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -L \
    https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# Extract
echo "Extracting runner..."
tar xzf actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# Install dependencies
echo "Installing dependencies..."
sudo ./bin/installdependencies.sh

echo ""
echo "=========================================="
echo "Runner downloaded successfully!"
echo "=========================================="
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Go to your GitHub repository: $REPO_URL"
echo "2. Navigate to: Settings → Actions → Runners → New self-hosted runner"
echo "3. Copy the token from the configuration command"
echo "4. Run the configuration:"
echo ""
echo "   cd ~/actions-runner"
echo "   ./config.sh --url $REPO_URL --token YOUR_TOKEN_HERE"
echo ""
echo "5. Start the runner as a service:"
echo ""
echo "   sudo ./svc.sh install"
echo "   sudo ./svc.sh start"
echo ""
echo "6. Or run manually for testing:"
echo ""
echo "   ./run.sh"
echo ""
