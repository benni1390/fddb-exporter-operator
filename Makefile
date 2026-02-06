.PHONY: test build run-local lint

test:
	docker run --rm -v $(CURDIR):/workspace -w /workspace -e PYTHONPATH=/workspace python:3.11-slim \
		bash -c "pip install -r requirements.txt && pytest -v"

build:
	docker build -t fddb-exporter-operator:latest .

run-local:
	docker run --rm -v $(CURDIR):/workspace -w /workspace -e PYTHONPATH=/workspace python:3.11-slim \
		bash -c "pip install -r requirements.txt && kopf run fddb_operator.py --verbose"

lint:
	docker run --rm -v $(CURDIR):/workspace -w /workspace python:3.11-slim \
		bash -c "pip install -r requirements.txt pylint && pylint fddb_operator.py"
