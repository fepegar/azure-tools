from pathlib import Path
from typing import List
from typing import Optional

import typer

from .aml import download_files
from .aml import download_snapshot
from .aml import get_files_to_download
from .aml import get_run
from .aml import get_workspace

app = typer.Typer(
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)


@app.command(no_args_is_help=True)
def download(
    config_path: Path = typer.Option(
        ...,
        '--config',
        '-c',
    ),
    run_ids: List[str] = typer.Option(
        ...,
        '--run-id',
        '-r',
    ),
    aml_path: Optional[Path] = typer.Option(
        None,
        '--source-aml-path',
        '-s',
    ),
    out_dir: Optional[Path] = typer.Option(
        None,
        '--out-dir',
        '-d',
    ),
    dry_run: bool = typer.Option(
        False,
        '--dry-run',
        '-n',
    ),
    force: bool = typer.Option(
        False,
        '--force',
        '-f',
    ),
    convert_logs: bool = typer.Option(
        False,
        '--convert-logs',
        '-l',
        help='Convert .txt files to .log files if "log" is in their path',
    ),
) -> None:
    workspace = get_workspace(config_path)
    for run_id in run_ids:
        run = get_run(workspace, run_id)
        files_to_download = get_files_to_download(run, aml_path)
        download_files(
            run,
            files_to_download,
            out_dir,
            dry_run=dry_run,
            force=force,
            convert_logs=convert_logs,
        )


@app.command(no_args_is_help=True)
def snapshot(
    config_path: Path = typer.Option(
        ...,
        '--config',
        '-c',
    ),
    run_ids: List[str] = typer.Option(
        ...,
        '--run-id',
        '-r',
    ),
    out_dir: Optional[Path] = typer.Option(
        None,
        '--out-dir',
        '-d',
    ),
) -> None:
    workspace = get_workspace(config_path)
    for run_id in run_ids:
        run = get_run(workspace, run_id)
        download_snapshot(run, out_dir=out_dir)


if __name__ == "__main__":
    app()
