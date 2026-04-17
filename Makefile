.PHONY: backend-install backend-check backend-test frontend-install frontend-check frontend-test up down

backend-install:
	cd backend && pip install -r requirements-dev.txt

backend-check:
	cd backend && ruff check app tests && black --check app tests && mypy app

backend-test:
	cd backend && pytest --cov=app --cov-report=term-missing

frontend-install:
	cd frontend && npm install

frontend-check:
	cd frontend && npm run lint

frontend-test:
	cd frontend && npm run test

up:
	docker compose up --build -d

down:
	docker compose down
