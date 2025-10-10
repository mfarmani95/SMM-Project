# ----------------------------
# 📦 SMM-Toolkit Makefile
# ----------------------------

PYTHON := python
PIP := pip

# Default target
help:
	@echo "Usage:"
	@echo "  make install        Install the package in editable mode"
	@echo "  make dev            Install dev dependencies"
	@echo "  make test           Run pytest"
	@echo "  make format         Format code with Black"
	@echo "  make lint           Run static checks with Ruff"
	@echo "  make build          Build the package"
	@echo "  make upload-test    Upload to TestPyPI"
	@echo "  make upload         Upload to PyPI"
	@echo "  make clean          Remove build artifacts"

install:
	$(PIP) install -e .

dev:
	$(PIP) install -r requirements-dev.txt

test:
	pytest -v

format:
	black src tests

lint:
	ruff check src tests

build:
	$(PYTHON) -m build

upload-test:
	twine upload --repository testpypi dist/*

upload:
	twine upload dist/*

clean:
	rm -rf build dist *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
