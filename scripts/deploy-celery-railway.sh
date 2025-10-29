#!/bin/bash

# ========================================================
# Railway Celery Workers Deployment Script
# ========================================================
# 
# This script automates the deployment of Celery workers
# and beat scheduler to Railway.
#
# Prerequisites:
# 1. Railway CLI installed (https://docs.railway.app/develop/cli)
# 2. Railway account with project created
# 3. Environment variables configured
#
# Usage:
#   ./scripts/deploy-celery-railway.sh [--dry-run]
#
# Options:
#   --dry-run    Show what would be deployed without executing
#
# ========================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_DIR="$PROJECT_DIR/services/etl"
DRY_RUN=false

# Parse arguments
for arg in "$@"; do
  case $arg in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
  esac
done

# ========================================================
# Helper Functions
# ========================================================

print_header() {
  echo -e "${BLUE}========================================${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}========================================${NC}"
}

print_success() {
  echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
  echo -e "${RED}❌ $1${NC}"
}

print_warning() {
  echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
  echo -e "${BLUE}ℹ️  $1${NC}"
}

check_command() {
  if ! command -v $1 &> /dev/null; then
    print_error "$1 is not installed"
    echo "Install from: $2"
    exit 1
  fi
}

run_command() {
  local description=$1
  shift
  local command="$@"
  
  if [ "$DRY_RUN" = true ]; then
    print_info "[DRY RUN] Would execute: $command"
  else
    print_info "Executing: $description"
    eval $command
    if [ $? -eq 0 ]; then
      print_success "$description completed"
    else
      print_error "$description failed"
      exit 1
    fi
  fi
}

# ========================================================
# Pre-flight Checks
# ========================================================

print_header "Pre-flight Checks"

# Check if Railway CLI is installed
check_command railway "https://docs.railway.app/develop/cli"

# Check if logged in to Railway
if ! railway whoami &> /dev/null; then
  print_error "Not logged in to Railway"
  echo "Run: railway login"
  exit 1
fi
print_success "Railway CLI authenticated"

# Check if in correct directory
if [ ! -f "$PROJECT_DIR/README.md" ]; then
  print_error "Script must be run from project root or scripts directory"
  exit 1
fi
print_success "Working directory verified"

# Check if .env file exists (for reference)
if [ ! -f "$PROJECT_DIR/.env" ]; then
  print_warning ".env file not found - ensure Railway environment variables are set"
else
  print_success "Local .env found (for reference)"
fi

# ========================================================
# Project Configuration
# ========================================================

print_header "Railway Project Configuration"

# Try to detect Railway project
if [ -f ".railway" ]; then
  print_success "Railway project linked"
  railway status
else
  print_warning "Railway project not linked"
  print_info "Linking project..."
  
  # List available projects
  echo ""
  echo "Available Railway projects:"
  railway list
  echo ""
  
  read -p "Enter Railway Project ID (from secrets or Railway dashboard): " PROJECT_ID
  
  if [ -z "$PROJECT_ID" ]; then
    print_error "Project ID required"
    exit 1
  fi
  
  run_command "Link Railway project" "railway link $PROJECT_ID"
fi

# ========================================================
# Environment Variables Check
# ========================================================

print_header "Environment Variables Check"

REQUIRED_VARS=(
  "DATABASE_URL"
  "REDIS_URL"
  "OPENAI_API_KEY"
  "ADMIN_API_KEY"
)

OPTIONAL_VARS=(
  "ENVIRONMENT"
  "LOG_LEVEL"
  "CORS_ORIGINS"
  "LLM_BUDGET_DAILY_USD"
  "SCRAPE_REAL"
)

print_info "Checking required environment variables..."
echo ""
echo "The following variables should be set in Railway:"
echo ""

for var in "${REQUIRED_VARS[@]}"; do
  echo "  [REQUIRED] $var"
done

echo ""
for var in "${OPTIONAL_VARS[@]}"; do
  echo "  [OPTIONAL] $var"
done

echo ""
print_warning "Verify these are set in Railway dashboard under each service's Variables tab"
echo ""

read -p "Have you verified all environment variables are set? (y/n): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
  print_info "Please set environment variables in Railway dashboard first"
  print_info "Visit: https://railway.app/project/YOUR_PROJECT_ID/settings"
  exit 1
fi

print_success "Environment variables confirmed"

# ========================================================
# Deploy Services
# ========================================================

print_header "Deploying Celery Worker"

echo ""
print_info "Service: agi-tracker-celery-worker"
print_info "Root Directory: services/etl"
print_info "Start Command: celery -A app.celery_app worker --loglevel=info --concurrency=2"
echo ""

if [ "$DRY_RUN" = true ]; then
  print_info "[DRY RUN] Would deploy Celery worker"
else
  read -p "Deploy Celery Worker? (y/n): " deploy_worker
  if [[ $deploy_worker =~ ^[Yy]$ ]]; then
    run_command "Deploy Celery worker" \
      "railway up --service agi-tracker-celery-worker"
    
    print_info "Waiting for deployment to complete..."
    sleep 15
    
    print_info "Checking worker logs..."
    railway logs --service agi-tracker-celery-worker --limit 30
  else
    print_warning "Skipped Celery worker deployment"
  fi
fi

echo ""
print_header "Deploying Celery Beat Scheduler"

echo ""
print_info "Service: agi-tracker-celery-beat"
print_info "Root Directory: services/etl"
print_info "Start Command: celery -A app.celery_app beat --loglevel=info"
echo ""

if [ "$DRY_RUN" = true ]; then
  print_info "[DRY RUN] Would deploy Celery beat"
else
  read -p "Deploy Celery Beat? (y/n): " deploy_beat
  if [[ $deploy_beat =~ ^[Yy]$ ]]; then
    run_command "Deploy Celery beat scheduler" \
      "railway up --service agi-tracker-celery-beat"
    
    print_info "Waiting for deployment to complete..."
    sleep 15
    
    print_info "Checking beat logs..."
    railway logs --service agi-tracker-celery-beat --limit 30
  else
    print_warning "Skipped Celery beat deployment"
  fi
fi

# ========================================================
# Verification
# ========================================================

print_header "Deployment Verification"

echo ""
print_info "Verifying service status..."
echo ""

if [ "$DRY_RUN" = false ]; then
  # List all services
  railway status
  
  echo ""
  print_success "Deployment complete!"
  echo ""
  print_info "Next steps:"
  echo "  1. Check logs: railway logs --service agi-tracker-celery-worker --follow"
  echo "  2. Verify beat: railway logs --service agi-tracker-celery-beat --follow"
  echo "  3. Monitor health: curl <API_URL>/v1/admin/tasks/health -H 'x-api-key: <KEY>'"
  echo ""
else
  print_info "[DRY RUN] Deployment verification skipped"
fi

# ========================================================
# Post-Deployment Instructions
# ========================================================

if [ "$DRY_RUN" = false ]; then
  print_header "Post-Deployment Instructions"
  
  echo ""
  echo "🔍 Monitor Services:"
  echo "   railway logs --service agi-tracker-celery-worker --follow"
  echo "   railway logs --service agi-tracker-celery-beat --follow"
  echo ""
  echo "📊 Check Task Health:"
  echo "   curl https://YOUR_API_URL/v1/admin/tasks/health \\"
  echo "     -H 'x-api-key: YOUR_ADMIN_KEY'"
  echo ""
  echo "🔄 Redeploy a Service:"
  echo "   railway up --service SERVICE_NAME"
  echo ""
  echo "📈 View Dashboard:"
  echo "   https://railway.app/project/YOUR_PROJECT_ID"
  echo ""
  echo "💰 Estimated Cost:"
  echo "   - Celery Worker: ~$5-10/month"
  echo "   - Celery Beat: ~$2-5/month"
  echo "   - Total: ~$7-15/month"
  echo ""
fi

print_success "Script completed successfully!"

