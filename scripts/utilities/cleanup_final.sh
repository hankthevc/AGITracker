#!/bin/bash
# Final Cleanup - Remove ALL remaining obsolete files
# Phase 3 of documentation cleanup

set -e  # Exit on error

echo "🧹 Starting Phase 3 (Final) Cleanup..."
echo ""

# Ensure directories exist
mkdir -p docs/archive/status
mkdir -p docs/archive/sprints
mkdir -p scripts/utilities

# Archive obsolete status files
echo "📦 Archiving obsolete status/completion files..."
[ -f "PHASE_1_COMPLETE.txt" ] && mv PHASE_1_COMPLETE.txt docs/archive/status/ && echo "  ✓ Archived PHASE_1_COMPLETE.txt"

# Archive Sprint 10 files (since Sprint 10 is complete)
echo "📦 Archiving completed Sprint 10 files..."
[ -f "SPRINT_10_COMPLETE.md" ] && mv SPRINT_10_COMPLETE.md docs/archive/sprints/ && echo "  ✓ Archived SPRINT_10_COMPLETE.md"
[ -f "SPRINT_10_PLAN.md" ] && mv SPRINT_10_PLAN.md docs/archive/sprints/ && echo "  ✓ Archived SPRINT_10_PLAN.md"

# Move cleanup scripts to utilities (keep them but not in root)
echo "📦 Moving utility scripts to scripts/utilities/..."
[ -f "cleanup_docs.sh" ] && mv cleanup_docs.sh scripts/utilities/ && echo "  ✓ Moved cleanup_docs.sh"
[ -f "cleanup_remaining.sh" ] && mv cleanup_remaining.sh scripts/utilities/ && echo "  ✓ Moved cleanup_remaining.sh"

# Remove obsolete deployment artifact
echo "🗑️  Removing obsolete deployment artifacts..."
[ -f ".railway-trigger" ] && git rm -f .railway-trigger && echo "  ✓ Removed .railway-trigger" || echo "  • .railway-trigger not found (already removed)"

echo ""
echo "✅ Phase 3 (Final) cleanup complete!"
echo ""
echo "📊 Root directory status:"
echo "  Files in root: $(git ls-files | grep -E '^[^/]+$' | wc -l | xargs)"
echo ""
echo "📝 Remaining root files should now be only:"
echo "  - Essential config files (.gitignore, .dockerignore, etc.)"
echo "  - Core documentation (README, ROADMAP, QUICKSTART, etc.)"
echo "  - Review deliverables (CODE_REVIEW_2025, etc.)"
echo "  - Build/deploy files (Dockerfile, Makefile, package.json, etc.)"
echo ""
echo "Next: git add -A && git commit -m 'chore: Final cleanup - archive remaining obsolete files'"

