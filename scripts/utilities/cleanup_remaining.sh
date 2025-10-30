#!/bin/bash
# Enhanced Cleanup - Catch remaining obsolete files
# Phase 2 of documentation cleanup

set -e  # Exit on error

echo "🧹 Starting Phase 2 Cleanup - Remaining Files..."
echo ""

# Create additional archive directories
echo "📁 Ensuring archive directories exist..."
mkdir -p docs/archive/sprints
mkdir -p docs/archive/scripts
mkdir -p demos

# Archive remaining sprint files
echo "📦 Archiving remaining sprint files..."
[ -f "SPRINT_4_COMPLETE.md" ] && mv SPRINT_4_COMPLETE.md docs/archive/sprints/ && echo "  ✓ Archived SPRINT_4_COMPLETE.md"

# Option: Archive Sprint 10 files if Sprint 10 is complete
# Uncomment these if you want to archive Sprint 10 as well:
# [ -f "SPRINT_10_COMPLETE.md" ] && mv SPRINT_10_COMPLETE.md docs/archive/sprints/
# [ -f "SPRINT_10_PLAN.md" ] && mv SPRINT_10_PLAN.md docs/archive/sprints/

# Move deployment scripts to archive
echo "📦 Archiving deployment scripts..."
[ -f "deploy-backend-auto.sh" ] && mv deploy-backend-auto.sh docs/archive/scripts/ && echo "  ✓ Archived deploy-backend-auto.sh"
[ -f "deploy-railway.sh" ] && mv deploy-railway.sh docs/archive/scripts/ && echo "  ✓ Archived deploy-railway.sh"
[ -f "deploy-vercel.sh" ] && mv deploy-vercel.sh docs/archive/scripts/ && echo "  ✓ Archived deploy-vercel.sh"
[ -f "TEST_AFTER_DEPLOY.sh" ] && mv TEST_AFTER_DEPLOY.sh docs/archive/scripts/ && echo "  ✓ Archived TEST_AFTER_DEPLOY.sh"
[ -f "TEST_FIXED.sh" ] && mv TEST_FIXED.sh docs/archive/scripts/ && echo "  ✓ Archived TEST_FIXED.sh"
[ -f "quick-deploy.sh" ] && mv quick-deploy.sh docs/archive/scripts/ && echo "  ✓ Archived quick-deploy.sh"
[ -f "verify_deployment.sh" ] && mv verify_deployment.sh docs/archive/scripts/ && echo "  ✓ Archived verify_deployment.sh"

# Move streamlit docs to demos (if not already there)
echo "📦 Moving Streamlit docs to demos/..."
[ -f "STREAMLIT_DEMO.md" ] && mv STREAMLIT_DEMO.md demos/ && echo "  ✓ Moved STREAMLIT_DEMO.md to demos/"
[ -f "STREAMLIT_DEPLOYMENT.md" ] && mv STREAMLIT_DEPLOYMENT.md demos/ && echo "  ✓ Moved STREAMLIT_DEPLOYMENT.md to demos/"

# Archive docker-compose.pgbouncer.yml if not in use
if [ -f "docker-compose.pgbouncer.yml" ]; then
    echo "📦 Archiving unused docker-compose files..."
    mkdir -p docs/archive/docker
    mv docker-compose.pgbouncer.yml docs/archive/docker/ && echo "  ✓ Archived docker-compose.pgbouncer.yml"
fi

echo ""
echo "✅ Phase 2 cleanup complete!"
echo ""
echo "📊 Summary of files archived:"
ls -1 docs/archive/sprints/*.md 2>/dev/null | wc -l | xargs echo "  Sprint files total:"
ls -1 docs/archive/scripts/*.sh 2>/dev/null | wc -l | xargs echo "  Script files:"
ls -1 demos/*.md 2>/dev/null | wc -l | xargs echo "  Demo files:"
echo ""
echo "📝 Next steps:"
echo "  1. Review changes: git status"
echo "  2. Commit: git add -A && git commit -m 'chore: Phase 2 cleanup - archive remaining files'"
echo "  3. Push: git push origin main"
echo ""
echo "🎯 Your root directory should now be much cleaner!"

