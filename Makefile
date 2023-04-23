test:
	echo "Running unit tests"
	python -m pytest tests -vv

lint:
	echo "Running formaters and linters"
	black .
	isort --skip .local --skip .poetry --skip .venv --profile black .
