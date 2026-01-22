.PHONY: install test lint format clean run dev

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt || echo "No dev requirements"

test:
	pytest

lint:
	flake8 app tests
	black --check app tests

format:
	black app tests
	isort app tests

clean:
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf *.egg-info

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
