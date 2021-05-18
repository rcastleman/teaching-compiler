PYTHON = python3.9 # just should be >= 3.7
TESTS = vm_tests \
	parser_tests \
	rasm_parser_tests \
	compiler_tests

.PHONY: test

# run all tests
test: 
	@for exec in $(TESTS); do \
		echo "Running $$exec"; \
		$(PYTHON) -m tests.$$exec; \
	done \