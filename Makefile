init:
	pip install -r requirements.txt

test:
	PYTEST_ADDOPTS=' --cov-report term-missing'
	py.test
