
TEST_DIR := ./tests/

MOD1 := reader
MOD2 := writer

.PHONY: tests

%.py: 
	python3 $@

tests:
	python3 tests/writer_tests.py