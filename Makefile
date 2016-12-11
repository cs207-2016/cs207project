sdist:
	$(MAKE) -C ./src/timeseries sdist
	$(MAKE) -C ./src/rbtree sdist

test:
	PYTEST_ADDOPTS=' --cov-report term-missing'
	py.test
