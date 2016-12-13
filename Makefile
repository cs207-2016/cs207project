sdist:
	$(MAKE) -C ./src/timeseries sdist
	$(MAKE) -C ./src/rbtree sdist
	$(MAKE) -C ./src.dbserver sdist

test:
	export PYTEST_ADDOPTS=' --cov-report term-missing'
	py.test

install:
	$(MAKE) sdist
	pip install ./dist/*.tar.gz

init:
	./init.sh
