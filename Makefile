.PHONY: install lock sync test lint typecheck

install sync:
	uv sync

lock:
	uv lock

test:
	uv run pytest -q

lint:
	uv run ruff check .

typecheck:
	uv run basedpyright

