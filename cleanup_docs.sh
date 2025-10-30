#!/bin/bash
# Documentation Cleanup Script
# Removes 80+ obsolete status/summary files and organizes documentation

set -e  # Exit on error

echo "🧹 Starting AGI Tracker Documentation Cleanup..."
echo ""

# Create archive directories
echo "📁 Creating archive directories..."
mkdir -p docs/archive/sprints
mkdir -p docs/archive/phases
mkdir -p docs/archive/deployments
mkdir -p docs/archive/status
mkdir -p .cursor/prompts

# Archive sprint documentation
echo "📦 Archiving sprint summaries..."
mv SPRINT_7_*.md docs/archive/sprints/ 2>/dev/null || true
mv SPRINT_8_*.md docs/archive/sprints/ 2>/dev/null || true
mv SPRINT_9_*.md docs/archive/sprints/ 2>/dev/null || true
mv SPRINT_10_TASK_*.md docs/archive/sprints/ 2>/dev/null || true
# Keep SPRINT_10_COMPLETE.md and SPRINT_10_PLAN.md in root

# Archive phase documentation
echo "📦 Archiving phase summaries..."
mv PHASE_0_*.md docs/archive/phases/ 2>/dev/null || true
mv PHASE_1_*.md docs/archive/phases/ 2>/dev/null || true
mv PHASE_2_*.md docs/archive/phases/ 2>/dev/null || true
mv PHASE_3_*.md docs/archive/phases/ 2>/dev/null || true
mv PHASE_4_*.md docs/archive/phases/ 2>/dev/null || true

# Archive deployment documentation
echo "📦 Archiving deployment docs..."
mv DEPLOYMENT_*.md docs/archive/deployments/ 2>/dev/null || true
mv RAILWAY_*.md docs/archive/deployments/ 2>/dev/null || true
mv VERCEL_*.md docs/archive/deployments/ 2>/dev/null || true
mv P0_P1_*.md docs/archive/deployments/ 2>/dev/null || true
mv DEVOPS_*.md docs/archive/deployments/ 2>/dev/null || true

# Move agent prompts
echo "📦 Moving agent prompts to .cursor/..."
mv AGENT_*.md .cursor/prompts/ 2>/dev/null || true

# Archive status files
echo "📦 Archiving status files..."
mv CONTINUE_HERE.md docs/archive/status/ 2>/dev/null || true
mv START_HERE.md docs/archive/status/ 2>/dev/null || true
mv NEXT_STEPS*.md docs/archive/status/ 2>/dev/null || true
mv NEXT_5_STEPS.md docs/archive/status/ 2>/dev/null || true
mv TASK_COMPLETE.txt docs/archive/status/ 2>/dev/null || true
mv DEMO_READY.md docs/archive/status/ 2>/dev/null || true
mv PRODUCTION_READY.md docs/archive/status/ 2>/dev/null || true
mv PROGRESS_SUMMARY.md docs/archive/status/ 2>/dev/null || true
mv IMPLEMENTATION_*.md docs/archive/status/ 2>/dev/null || true
mv END_OF_SESSION_STATUS.md docs/archive/status/ 2>/dev/null || true
mv FINAL_STATUS.md docs/archive/status/ 2>/dev/null || true
mv HANDOFF_TO_AGENT.md docs/archive/status/ 2>/dev/null || true
mv BLOCKED.md docs/archive/status/ 2>/dev/null || true
mv DEPLOY_NOW.md docs/archive/status/ 2>/dev/null || true

# Archive audit files (superseded by docs/code-audit.md files)
echo "📦 Archiving audit summaries..."
mv AUDIT_*.md docs/archive/status/ 2>/dev/null || true
mv CODE_AUDIT_*.md docs/archive/status/ 2>/dev/null || true
mv CODEBASE_REVIEW_FINDINGS.md docs/archive/status/ 2>/dev/null || true
mv RETRACTION_SYSTEM_VERIFICATION.md docs/archive/status/ 2>/dev/null || true

# Archive monitoring/verification files
mv MONITORING_SETUP.md docs/archive/status/ 2>/dev/null || true
mv VERIFICATION_CHECKLIST.md docs/archive/status/ 2>/dev/null || true

# Archive PR/misc files
mv PR_SUMMARY.md docs/archive/status/ 2>/dev/null || true
mv DOCUMENTATION_SPRINT_COMPLETE.md docs/archive/status/ 2>/dev/null || true

# Consolidate quickstart files
echo "📄 Consolidating quickstart documentation..."
if [ -f "QUICK_START_DEVOPS.md" ] || [ -f "README_DEPLOYMENT.md" ]; then
    echo "" >> QUICKSTART.md
    echo "---" >> QUICKSTART.md
    echo "" >> QUICKSTART.md
    [ -f "QUICK_START_DEVOPS.md" ] && cat QUICK_START_DEVOPS.md >> QUICKSTART.md
    [ -f "README_DEPLOYMENT.md" ] && cat README_DEPLOYMENT.md >> QUICKSTART.md
    rm -f QUICK_START*.md README_DEPLOYMENT.md
fi

# Delete obsolete code files
echo "🗑️  Removing obsolete code files..."
rm -f Dockerfile.old
rm -f fetch_real_news_now.py

# Move demo files
echo "📦 Moving demo files..."
mkdir -p demos
[ -f "streamlit_app.py" ] && mv streamlit_app.py demos/ 2>/dev/null || true
[ -f "STREAMLIT_*.md" ] && mv STREAMLIT_*.md demos/ 2>/dev/null || true

# Move fixtures
echo "📦 Moving sample data to fixtures..."
[ -f "REAL_NEWS_SAMPLE.json" ] && mv REAL_NEWS_SAMPLE.json infra/fixtures/ 2>/dev/null || true

# Create summary report
echo ""
echo "✅ Documentation cleanup complete!"
echo ""
echo "📊 Summary:"
echo "  - Sprint docs archived: $(ls docs/archive/sprints/*.md 2>/dev/null | wc -l) files"
echo "  - Phase docs archived: $(ls docs/archive/phases/*.md 2>/dev/null | wc -l) files"
echo "  - Deployment docs archived: $(ls docs/archive/deployments/*.md 2>/dev/null | wc -l) files"
echo "  - Status files archived: $(ls docs/archive/status/*.md 2>/dev/null | wc -l) files"
echo "  - Agent prompts moved: $(ls .cursor/prompts/*.md 2>/dev/null | wc -l) files"
echo ""
echo "📁 Organized structure:"
echo "  /docs/archive/sprints/     - Historical sprint summaries"
echo "  /docs/archive/phases/      - Historical phase summaries"
echo "  /docs/archive/deployments/ - Deployment troubleshooting history"
echo "  /docs/archive/status/      - Session status snapshots"
echo "  /.cursor/prompts/          - AI agent instructions"
echo "  /demos/                    - Demo apps (Streamlit)"
echo ""
echo "📝 Next steps:"
echo "  1. Review consolidated QUICKSTART.md"
echo "  2. Update README.md if needed"
echo "  3. Commit changes: git add -A && git commit -m 'chore: Archive obsolete documentation'"
echo "  4. Push to GitHub: git push origin main"
echo ""
echo "🎉 Your repository is now much cleaner!"

