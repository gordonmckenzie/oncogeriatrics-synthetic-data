.PHONY: run test

default: run

test:
	PYTHONPATH=. pytest -q tests/test_pgm.py --ignore=lib/* 

test_analysis:
	PYTHONPATH=. pytest -v tests/test_analysis.py::TestAnalysis::test_analysis --ignore=lib/

test_utils:
	PYTHONPATH=. pytest -v tests/test_utils.py::TestUtils --ignore=lib/ --capture=tee-sys

test_pgm:
	PYTHONPATH=. pytest -v tests/test_pgm.py::TestPGM --ignore=lib/ --capture=tee-sys

test_prescribing:
	PYTHONPATH=. pytest -v tests/test_prescribing.py::TestPrescribing --ignore=lib/ --capture=tee-sys

test_MPI:
	mpiexec --oversubscribe -np 4 python mpi.py

test_oracles:
	PYTHONPATH=. pytest -v tests/test_oracles.py::TestOracles --ignore=lib/ --capture=tee-sys

run:
	python run.py