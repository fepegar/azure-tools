We use `uv` for package managing.
Install uv with `curl -LsSf https://astral.sh/uv/install.sh | sh`, then install this project with `uv sync --all-extras --all-groups`.
If you want to run something, use the `uv run` prefix (e.g. `uv run python [args]` or `uv run pytest [args]`.
Before pushing your changes, run `uvx ruff check --diff` and `uvx ruff format --diff`.
