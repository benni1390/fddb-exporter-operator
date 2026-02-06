.PHONY: test build run-local lint helm-lint helm-package

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

helm-lint:
	docker run --rm -v $(CURDIR):/workspace -w /workspace alpine/helm:latest lint chart/fddb-exporter-operator

helm-package:
	docker run --rm -v $(CURDIR):/workspace -w /workspace alpine/helm:latest package chart/fddb-exporter-operator -d .charts
