# makefile for poetry
.PHONY: help format install lint run test

help:
	@echo "make format: format python files"
	@echo "make install: install prettybird in your env"
	@echo "make lint: lint python files"
	@echo "make run input=<file_to_compile>: compile <file_to_compile>"
	@echo "make test: run tests"

format:
	poetry run autopep8 --in-place prettybird/*.py -r

install:
	poetry install

lint:
	poetry run flake8 prettybird/*.py
	poetry run mypy .

run:
	poetry run prettybird $(input)

test:
	poetry run pytest