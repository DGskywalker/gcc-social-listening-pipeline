# ==============================================================================
# GCC Social Listening Pipeline - Automation Makefile
# ==============================================================================

PYTHON = .venv/bin/python
PYTEST = .venv/bin/pytest
JUPYTER = .venv/bin/jupyter

.PHONY: help install run test validate notebook preview serve clean

help:
	@echo "GCC Social Listening Pipeline Commands:"
	@echo "  make install         Install virtual environment and dependencies"
	@echo "  make run             Execute full end-to-end pipeline (ingestion -> S3 -> tagging -> dashboard)"
	@echo "  make test            Run complete test suite (with moto S3 & mocks)"
	@echo "  make validate        Evaluate model against 150 gold items & generate docs/VALIDATION.md"
	@echo "  make notebook        Execute notebooks/take_home.ipynb headlessly"
	@echo "  make preview         Regenerate dashboard screenshot preview for README.md"
	@echo "  make serve           Launch local web server for dashboard at http://localhost:8000"
	@echo "  make clean           Remove temporary cache files and logs"

install:
	uv pip install -r requirements.txt

run:
	$(PYTHON) run_pipeline.py --all

test:
	$(PYTEST) -v tests/

validate:
	$(PYTHON) scripts/validate_model.py

notebook:
	$(JUPYTER) nbconvert --to notebook --execute --inplace notebooks/take_home.ipynb

preview:
	$(PYTHON) scripts/generate_dashboard_preview.py

serve:
	@echo "Opening GCC Social Listening Dashboard at http://localhost:8000/dashboard/index.html ..."
	cd dashboard && $(PYTHON) -m http.server 8000

clean:
	rm -rf .cache logs/*.log local_storage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
