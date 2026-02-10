PYTHON = python3
PIP = pip
VENV = .venv
BIN = $(VENV)/bin

.PHONY: install run debug clean lint lint-strict build

install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/$(PIP) install --upgrade pip
	$(BIN)/$(PIP) install flake8 mypy mlx-2.2-py3-none-any.whl setuptools wheel
	@if [ -f requirements.txt ]; then $(BIN)/$(PIP) install -r requirements.txt; fi

# Build the mazegen package
build:
	$(BIN)/$(PYTHON) setup.py sdist bdist_wheel
	mv dist/*.whl .
	mv dist/*.tar.gz .
	rm -rf dist build *.egg-info

run:
	$(BIN)/$(PYTHON) a_maze_ing.py config.txt

debug:
	$(BIN)/$(PYTHON) -m pdb a_maze_ing.py config.txt

clean:
	rm -rf $(VENV)
	rm -rf .mypy_cache
	rm -rf build dist *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	$(BIN)/flake8 . --exclude=$(VENV)
	$(BIN)/mypy . --exclude $(VENV) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
