# Makefile for Virtual Assistant Project

.PHONY: help install dev test lint format clean db-up db-down db-migrate db-upgrade db-downgrade

# Default target
help:
	@echo "Virtual Assistant Project Management"
	@echo ""
	@echo "Usage:"
	@echo "  make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install     Install all dependencies"
	@echo "  dev         Run development server"
	@echo "  test        Run tests"
	@echo "  lint        Run code linting"
	@echo "  format      Format code"
	@echo "  clean       Clean up temporary files"
	@echo "  db-up       Start database containers"
	@echo "  db-down     Stop database containers"
	@echo "  db-migrate  Create new migration"
	@echo "  db-upgrade  Apply database migrations"
	@echo "  db-downgrade  Revert database migrations"

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -r requirements-virtual-assistant.txt
	pip install -r requirements-dev.txt
	@echo "All dependencies installed successfully"

# Run development server
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test:
	pytest tests/ -v --cov=app --cov-report=html

# Run code linting
lint:
	flake8 app/ tests/
	pylint app/ tests/
	mypy app/ tests/

# Format code
format:
	black app/ tests/
	isort app/ tests/

# Clean up temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -rf .mypy_cache
	@echo "Cleaned up temporary files"

# Database operations
db-up:
	docker-compose up -d postgres redis

db-down:
	docker-compose down

db-migrate:
	alembic revision --autogenerate -m "$(m)"

db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

# Docker operations
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Production deployment
deploy:
	@echo "Building and deploying production containers..."
	docker-compose -f docker-compose.prod.yml up --build -d

# Backup database
backup:
	@echo "Creating database backup..."
	@mkdir -p backups
	docker-compose exec postgres pg_dump -U assistant virtual_assistant > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup completed successfully"

# Restore database
restore:
	@if [ -z "$(file)" ]; then \
		echo "Usage: make restore file=backups/backup_file.sql"; \
		exit 1; \
	fi
	@echo "Restoring database from $(file)..."
	docker-compose exec postgres psql -U assistant -d virtual_assistant -f /backups/$(file)
	@echo "Restore completed successfully"