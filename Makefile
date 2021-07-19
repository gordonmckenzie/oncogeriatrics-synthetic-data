.PHONY: run test

default: run

test:
	PYTHONPATH=. pytest -q tests/test_pgm.py --ignore=lib/ 

test_analysis:
	PYTHONPATH=. pytest -v tests/test_analysis.py::TestAnalysis::test_analysis --ignore=lib/

run:
	python run.py