
TEST_DIR := ./tests/

MOD1 := reader
MOD2 := writer

.PHONY: tests

%.py: 
	python3 $@

tests: $(TEST_DIR)$(MOD1)_tests.py $(TEST_DIR)$(MOD2)_tests.py