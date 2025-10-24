.PHONY: dev api ui test report install clean help

help:
	@echo "QA Coach - Makefile targets"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Run API and Streamlit in parallel (requires start-process)"
	@echo "  make api        - Run FastAPI server"
	@echo "  make ui         - Run Streamlit dashboard"
	@echo "  make test       - Run pytest tests"
	@echo "  make report     - Generate Coach Effect report"
	@echo "  make clean      - Clean generated files"
	@echo "  make lint       - Run ruff linter"
	@echo "  make format     - Format code with black"

install:
	pip install -r requirements.txt
	@if not exist .env copy .env.example .env

dev:
	@echo "Starting API and Streamlit..."
	@echo "API will run on http://localhost:8000"
	@echo "Streamlit will run on http://localhost:8501"
	@powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd $(PWD); uvicorn app.api:app --reload --port 8000'"
	@timeout /t 3 /nobreak > nul
	streamlit run app/dashboard.py

api:
	uvicorn app.api:app --reload --port 8000 --host 0.0.0.0

ui:
	streamlit run app/dashboard.py

test:
	pytest -v tests/

report:
	python reports/aggregations.py

lint:
	ruff check .

format:
	black .

clean:
	if exist data\runs rmdir /s /q data\runs
	if exist data\reports rmdir /s /q data\reports
	if exist __pycache__ rmdir /s /q __pycache__
	if exist .pytest_cache rmdir /s /q .pytest_cache
	for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	for /d /r %%d in (.pytest_cache) do @if exist "%%d" rmdir /s /q "%%d"

seed:
	python scripts/seed_synthetic.py
