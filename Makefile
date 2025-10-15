.PHONY: bootstrap dev migrate seed seed-content seed-dev-fixtures test lint typecheck e2e build clean backfill

bootstrap:
	@echo "🚀 Bootstrapping AGI Signpost Tracker..."
	npm install
	cd services/etl && python -m venv .venv && . .venv/bin/activate && pip install -e .
	@echo "✅ Bootstrap complete. Run 'make dev' to start."

dev:
	@echo "🔧 Starting development environment..."
	docker-compose -f docker-compose.dev.yml up

migrate:
	@echo "📊 Running database migrations..."
	cd infra/migrations && alembic upgrade head

migrate-create:
	@echo "📝 Creating new migration..."
	@read -p "Enter migration name: " name; \
	cd infra/migrations && alembic revision --autogenerate -m "$$name"

seed:
	@echo "🌱 Seeding database..."
	cd scripts && python seed.py

seed-content:
	@echo "📚 Seeding rich educational content..."
	cd scripts && python extract_roadmap_predictions.py
	cd scripts && python seed_rich_content.py
	cd scripts && python write_pace_analyses.py
	@echo "✅ Content seeding complete."

seed-dev-fixtures:
	@echo "🧪 Seeding development fixtures..."
	@echo "⚠️  This adds synthetic test data - use only in dev/test environments!"
	DEV_FIXTURE_INPUTS=true cd scripts && python seed_dev_fixtures.py
	@echo "✅ Dev fixtures seeded. Run 'curl -X POST http://localhost:8000/v1/recompute' to update index."

test:
	@echo "🧪 Running tests..."
	npm test
	cd services/etl && . .venv/bin/activate && pytest

lint:
	@echo "🔍 Running linters..."
	npm run lint
	cd services/etl && . .venv/bin/activate && ruff check .

typecheck:
	@echo "📝 Running type checks..."
	npm run typecheck
	cd services/etl && . .venv/bin/activate && mypy app/

e2e:
	@echo "🎭 Running E2E tests..."
	npm run e2e

build:
	@echo "🏗️  Building for production..."
	npm run build

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf node_modules apps/*/node_modules packages/*/node_modules
	rm -rf apps/*/.next apps/*/dist packages/*/dist
	rm -rf services/etl/.venv services/etl/__pycache__
	@echo "✅ Clean complete."

backfill:
	@echo "🔄 Running backfill for all connectors..."
	@echo "   Using fixtures (SCRAPE_REAL=false) by default"
	@echo "   Set BACKFILL_REAL=true to use live scraping"
	@if [ "$(BACKFILL_REAL)" = "true" ]; then \
		echo "⚠️  Live scraping enabled (BACKFILL_REAL=true)"; \
		export SCRAPE_REAL=true; \
	else \
		echo "✓ Using fixtures (safer for initial setup)"; \
		export SCRAPE_REAL=false; \
	fi; \
	cd scripts && python -c "import sys; sys.path.insert(0, '../services/etl'); \
		from app.tasks.fetch_swebench import fetch_swebench; \
		from app.tasks.fetch_osworld import fetch_osworld_task; \
		from app.tasks.fetch_webarena import fetch_webarena_task; \
		from app.tasks.fetch_gpqa import fetch_gpqa_task; \
		from app.tasks.seed_inputs import seed_inputs_task; \
		from app.tasks.security_maturity import security_maturity_task; \
		print('📊 1/6 Fetching SWE-bench...'); fetch_swebench(); \
		print('📊 2/6 Fetching OSWorld...'); fetch_osworld_task(); \
		print('📊 3/6 Fetching WebArena...'); fetch_webarena_task(); \
		print('📊 4/6 Fetching GPQA...'); fetch_gpqa_task(); \
		print('📊 5/6 Seeding Inputs...'); seed_inputs_task(); \
		print('📊 6/6 Computing Security Maturity...'); security_maturity_task(); \
		print('✅ Backfill complete')"
	@echo "✅ All connectors backfilled. Run 'make seed' if needed."

