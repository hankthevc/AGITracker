#!/bin/bash

# ========================================================
# Environment Variable Validation Script
# ========================================================
#
# This script validates that all required environment
# variables are set for the AGI Signpost Tracker.
#
# Usage:
#   ./scripts/validate-env.sh [--service=<service>] [--env=<env>]
#
# Options:
#   --service=<service>  Validate for specific service (api, web, etl, all)
#   --env=<env>          Environment to validate (dev, prod, test)
#
# Examples:
#   ./scripts/validate-env.sh                    # Validate all for dev
#   ./scripts/validate-env.sh --service=api      # Validate API only
#   ./scripts/validate-env.sh --env=prod         # Validate for production
#
# ========================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE="all"
ENV="dev"
ERRORS=0
WARNINGS=0

# Parse arguments
for arg in "$@"; do
  case $arg in
    --service=*)
      SERVICE="${arg#*=}"
      shift
      ;;
    --env=*)
      ENV="${arg#*=}"
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
  ((ERRORS++))
}

print_warning() {
  echo -e "${YELLOW}⚠️  $1${NC}"
  ((WARNINGS++))
}

print_info() {
  echo -e "${BLUE}ℹ️  $1${NC}"
}

check_var() {
  local var_name=$1
  local required=$2
  local description=$3
  
  if [ -z "${!var_name}" ]; then
    if [ "$required" = "true" ]; then
      print_error "$var_name is not set - $description"
    else
      print_warning "$var_name is not set (optional) - $description"
    fi
  else
    # Redact sensitive values in output
    local display_value="${!var_name}"
    if [[ $var_name == *"KEY"* ]] || [[ $var_name == *"SECRET"* ]] || [[ $var_name == *"PASSWORD"* ]] || [[ $var_name == *"TOKEN"* ]]; then
      display_value="***REDACTED***"
    fi
    print_success "$var_name is set ($display_value)"
  fi
}

validate_url() {
  local var_name=$1
  local value="${!var_name}"
  
  if [ -n "$value" ]; then
    if [[ $value =~ ^https?:// ]]; then
      print_success "$var_name is a valid URL"
    else
      print_error "$var_name is not a valid URL: $value"
    fi
  fi
}

validate_numeric() {
  local var_name=$1
  local value="${!var_name}"
  
  if [ -n "$value" ]; then
    if [[ $value =~ ^[0-9]+$ ]]; then
      print_success "$var_name is numeric: $value"
    else
      print_error "$var_name is not numeric: $value"
    fi
  fi
}

# ========================================================
# Main Validation
# ========================================================

print_header "Environment Variable Validation"
echo ""
print_info "Service: $SERVICE"
print_info "Environment: $ENV"
echo ""

# Try to load .env if it exists
if [ -f ".env" ]; then
  print_info "Loading .env file..."
  set -a
  source .env
  set +a
else
  print_warning ".env file not found - checking system environment"
fi

echo ""

# ========================================================
# Database Configuration
# ========================================================

if [[ "$SERVICE" == "all" ]] || [[ "$SERVICE" == "api" ]] || [[ "$SERVICE" == "etl" ]]; then
  print_header "Database Configuration"
  
  check_var "DATABASE_URL" "true" "PostgreSQL connection string"
  validate_url "DATABASE_URL"
  
  # Validate DATABASE_URL format
  if [ -n "$DATABASE_URL" ]; then
    if [[ $DATABASE_URL == postgres* ]] || [[ $DATABASE_URL == postgresql* ]]; then
      print_success "DATABASE_URL has correct protocol"
    else
      print_error "DATABASE_URL must start with postgres:// or postgresql://"
    fi
  fi
  
  echo ""
fi

# ========================================================
# Redis Configuration
# ========================================================

if [[ "$SERVICE" == "all" ]] || [[ "$SERVICE" == "api" ]] || [[ "$SERVICE" == "etl" ]]; then
  print_header "Redis Configuration"
  
  check_var "REDIS_URL" "true" "Redis connection string for Celery"
  validate_url "REDIS_URL"
  
  # Validate REDIS_URL format
  if [ -n "$REDIS_URL" ]; then
    if [[ $REDIS_URL == redis* ]]; then
      print_success "REDIS_URL has correct protocol"
    else
      print_error "REDIS_URL must start with redis://"
    fi
  fi
  
  echo ""
fi

# ========================================================
# API Keys & Secrets
# ========================================================

if [[ "$SERVICE" == "all" ]] || [[ "$SERVICE" == "api" ]] || [[ "$SERVICE" == "etl" ]]; then
  print_header "API Keys & Secrets"
  
  check_var "OPENAI_API_KEY" "true" "OpenAI API key for LLM analysis"
  
  # Validate OpenAI API key format
  if [ -n "$OPENAI_API_KEY" ]; then
    if [[ $OPENAI_API_KEY == sk-* ]]; then
      print_success "OPENAI_API_KEY has correct format (sk-*)"
    else
      print_warning "OPENAI_API_KEY may be invalid (should start with sk-)"
    fi
  fi
  
  check_var "ADMIN_API_KEY" "$([[ $ENV == prod ]] && echo true || echo false)" "Admin API key for protected endpoints"
  
  # Warn if API key is weak
  if [ -n "$ADMIN_API_KEY" ]; then
    key_length=${#ADMIN_API_KEY}
    if [ $key_length -lt 32 ]; then
      print_warning "ADMIN_API_KEY is short ($key_length chars). Recommend 32+ characters."
    else
      print_success "ADMIN_API_KEY has sufficient length ($key_length chars)"
    fi
  fi
  
  check_var "ANTHROPIC_API_KEY" "false" "Anthropic API key for multi-model analysis"
  
  echo ""
fi

# ========================================================
# Application Configuration
# ========================================================

if [[ "$SERVICE" == "all" ]] || [[ "$SERVICE" == "api" ]] || [[ "$SERVICE" == "etl" ]]; then
  print_header "Application Configuration"
  
  check_var "ENVIRONMENT" "false" "Environment name (dev, staging, production)"
  
  if [ -n "$ENVIRONMENT" ]; then
    if [[ "$ENVIRONMENT" =~ ^(dev|development|staging|production|prod|test)$ ]]; then
      print_success "ENVIRONMENT has valid value: $ENVIRONMENT"
    else
      print_warning "ENVIRONMENT has unexpected value: $ENVIRONMENT"
    fi
  fi
  
  check_var "LOG_LEVEL" "false" "Logging level (debug, info, warning, error)"
  
  if [ -n "$LOG_LEVEL" ]; then
    if [[ "$LOG_LEVEL" =~ ^(debug|info|warning|error|critical)$ ]]; then
      print_success "LOG_LEVEL has valid value: $LOG_LEVEL"
    else
      print_warning "LOG_LEVEL has unexpected value: $LOG_LEVEL"
    fi
  fi
  
  check_var "LLM_BUDGET_DAILY_USD" "false" "Daily LLM budget in USD (default: 20)"
  validate_numeric "LLM_BUDGET_DAILY_USD"
  
  check_var "SCRAPE_REAL" "false" "Enable real scraping (true/false, default: false)"
  
  if [ -n "$SCRAPE_REAL" ]; then
    if [[ "$SCRAPE_REAL" =~ ^(true|false|True|False|1|0)$ ]]; then
      print_success "SCRAPE_REAL has valid boolean value: $SCRAPE_REAL"
    else
      print_warning "SCRAPE_REAL should be true/false: $SCRAPE_REAL"
    fi
  fi
  
  echo ""
fi

# ========================================================
# CORS Configuration
# ========================================================

if [[ "$SERVICE" == "all" ]] || [[ "$SERVICE" == "api" ]]; then
  print_header "CORS Configuration"
  
  check_var "CORS_ORIGINS" "$([[ $ENV == prod ]] && echo true || echo false)" "Allowed CORS origins (comma-separated)"
  
  if [ -n "$CORS_ORIGINS" ]; then
    IFS=',' read -ra ORIGINS <<< "$CORS_ORIGINS"
    for origin in "${ORIGINS[@]}"; do
      origin=$(echo "$origin" | xargs) # Trim whitespace
      if [[ $origin =~ ^https?:// ]]; then
        print_success "CORS origin is valid: $origin"
      else
        print_warning "CORS origin may be invalid: $origin"
      fi
    done
  fi
  
  echo ""
fi

# ========================================================
# Frontend Configuration
# ========================================================

if [[ "$SERVICE" == "all" ]] || [[ "$SERVICE" == "web" ]]; then
  print_header "Frontend Configuration (Next.js)"
  
  check_var "NEXT_PUBLIC_API_URL" "$([[ $ENV == prod ]] && echo true || echo false)" "Public API base URL"
  validate_url "NEXT_PUBLIC_API_URL"
  
  check_var "NEXT_PUBLIC_SENTRY_DSN" "false" "Sentry DSN for error tracking"
  
  echo ""
fi

# ========================================================
# Railway Configuration (Production)
# ========================================================

if [[ "$ENV" == "prod" ]] && [[ "$SERVICE" == "all" ]]; then
  print_header "Railway Configuration (Production Only)"
  
  check_var "RAILWAY_ENVIRONMENT" "false" "Railway environment name"
  check_var "RAILWAY_PROJECT_ID" "false" "Railway project ID"
  check_var "PORT" "false" "Server port (Railway assigns dynamically)"
  
  echo ""
fi

# ========================================================
# Vercel Configuration (Production)
# ========================================================

if [[ "$ENV" == "prod" ]] && [[ "$SERVICE" == "web" ]]; then
  print_header "Vercel Configuration (Production Only)"
  
  check_var "VERCEL_URL" "false" "Vercel deployment URL"
  check_var "VERCEL_ENV" "false" "Vercel environment"
  
  echo ""
fi

# ========================================================
# Summary
# ========================================================

print_header "Validation Summary"

echo ""
echo "Service: $SERVICE"
echo "Environment: $ENV"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  print_success "All environment variables are properly configured!"
  exit 0
elif [ $ERRORS -eq 0 ]; then
  print_warning "$WARNINGS warning(s) found (non-critical)"
  echo ""
  print_info "Warnings indicate missing optional variables or recommendations."
  print_info "Review warnings above for details."
  exit 0
else
  print_error "$ERRORS error(s) and $WARNINGS warning(s) found"
  echo ""
  print_error "Critical environment variables are missing!"
  print_info "Set missing variables in .env file or export them:"
  echo ""
  echo "  export VARIABLE_NAME=\"value\""
  echo "  or"
  echo "  echo 'VARIABLE_NAME=value' >> .env"
  echo ""
  exit 1
fi

