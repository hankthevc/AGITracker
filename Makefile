.PHONY: bootstrap dev migrate seed seed-content test lint e2e build clean

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

