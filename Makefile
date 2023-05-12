profile:
	echo "Switching aws profile"
	export AWS_PROFILE=enchanted-potato

test:
	echo "Running unit tests"
	python -m pytest tests -vv

lint:
	echo "Running formaters and linters"
	black .
	isort --skip .local --skip .poetry --skip .venv --profile black .

lambda-function:
	echo "Creating lambda layers"
	cd tf && \
	rm -rf lambda_function.zip packages && \
	mkdir packages	&& \
	cd packages	&& \
	python3 -m venv venv &&	\
	source venv/bin/activate && \
	mkdir python && \
	cd python && \
	pip install --platform manylinux2014_aarch64 --only-binary=:all: pandas pymysql -t . && \
	cp ../../lambda_helper.py . && \
	rm -rf *dist-info && \
	cd .. && \
	zip -r lambda_layer.zip python && \
	cd .. && \
	zip -r lambda_function.zip lambda_handler.py
