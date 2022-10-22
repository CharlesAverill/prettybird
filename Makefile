# makefile for poetry
.PHONY: help format install lint run test vtest

help:
	@echo "make format: format python files"
	@echo "make install: install prettybird in your env"
	@echo "make lint: lint python files"
	@echo "make run input=<file_to_compile>: compile <file_to_compile> to a bitmap TTF file"
	@echo "make test: run tests"
	@echo "make vtest: run tests with verbose output"

format:
	poetry run black $$(find prettybird -name "*.py")
	poetry run autopep8 --in-place $$(find prettybird -name "*.py")

install:
	poetry install
	poetry run pre-commit install

lint:
	poetry run flake8 --ignore=E501,W503 $$(find prettybird -name "*.py")
	poetry run mypy .

run:
	poetry run prettybird $(input) --format=SVG

test:
	poetry run pytest

vtest:
	poetry run pytest -vv
