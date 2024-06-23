# Define the shell to use
SHELL := /bin/bash

# Mark targets as phony to avoid conflicts with files of the same name
.PHONY: all test run clean dependencies

# Define the default target
all: dependencies test

dependencies:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

test:
	@echo "Running tests..."
	python -m unittest discover -s tests

run: test
	@echo "Running the application..."
	export PYTHONPATH="/Users/thibodebras/dev/colruyt-tracker:$(PYTHONPATH)"
	python scraper/main.py

clean:
	@echo "Cleaning up..."
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
