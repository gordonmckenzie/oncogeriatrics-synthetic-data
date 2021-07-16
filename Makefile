.PHONY: run test

default: run

test:
	PYTHONPATH=. pytest -q tests/test_pgm.py

run:
	python run.py