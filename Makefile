export PATH := $(HOME)/.local/bin:$(PATH)
UV ?= uv

.PHONY: demo-shots setup lint test research eval demo record

setup:
	$(UV) sync --extra dev

lint:
	$(UV) run ruff check src tests research
	$(UV) run ruff format --check src tests research
	$(UV) run mypy

test:
	$(UV) run pytest

research:
	$(UV) run python research/phase0/run_all.py

eval:
	$(UV) run python research/phase0/benign_fpr/run.py
	$(UV) run python research/phase0/screening_latency/run.py
	$(UV) run python research/phase0/split_order_sim/run.py
	$(UV) run python research/phase0/render_docs.py
	$(UV) run synthguard eval

demo:
	$(UV) run synthguard demo

demo-shots:
	$(UV) run --with pyyaml python demo/verify_shots.py

record:
	bash demo/record.sh
	bash demo/render.sh
