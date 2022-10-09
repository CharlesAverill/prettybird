# makefile for poetry
.PHONY: help format install lint run test

help:
	@echo "make format: format python files"
	@echo "make install cc=[bc, cyg, gcc, msvc, osx, sun]: install prettybird in your env and use <cc> as the C compiler"
	@echo "make lint: lint python files"
	@echo "make run input=<file_to_compile>: compile <file_to_compile>"
	@echo "make test: run tests"

format:
	poetry run autopep8 --in-place prettybird/*.py -r

install:
	cd lib/bdf2ttf && make $(cc)-clean && make $(cc)
	poetry install

lint:
	poetry run flake8 prettybird/*.py --ignore=E501,W503
	poetry run mypy .

run:
	poetry run prettybird $(input)

test:
	poetry run pytest
