import os
import time
from pathlib import Path
from typing import Optional

import typer
from azureml.core import Run
from azureml.core import Workspace
from dotenv import load_dotenv
from humanize import naturalsize
from rich import print
from rich.progress import BarColumn
from rich.progress import MofNCompleteColumn
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TaskProgressColumn
from rich.progress import TextColumn
from rich.progress import TimeElapsedColumn


app = typer.Typer()


@app.command()
def download(
    run_id: str = typer.Option(
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
) -> None:
    workspace = get_workspace()
    run = get_run(workspace, run_id)
    files_to_download = get_files_to_download(run, aml_path)
    download_files(run, files_to_download, out_dir, dry_run=dry_run, force=force)


@app.command()
def other(

) -> None:
    return


def get_workspace() -> Workspace:
    load_dotenv()
    name = os.environ["WORKSPACE_NAME"]
    with BarlessProgress() as progress:
        task = progress.add_task(f'Getting workspace "{name}"', total=1)
        workspace = Workspace(
            os.environ["SUBSCRIPTION_ID"],
            os.environ["RESOURCE_GROUP"],
            name,
        )
        progress.update(task, advance=1)
    return workspace


def get_run(workspace: Workspace,  run_id: str) -> Run:
    with BarlessProgress() as progress:
        task = progress.add_task(f'Getting run "{run_id}"', total=1)
        run = workspace.get_run(run_id)
        progress.update(task, advance=1)
    print(f'Found run with display name: "{run.display_name}" in experiment "{run.experiment.name}"')
    return run


def get_files_to_download(run: Run, aml_path: Path | None) -> list[Path]:
    with BarlessProgress() as progress:
        task = progress.add_task(f'Getting files in run "{run.id}"', total=1)
        run_filepaths = [Path(p) for p in run.get_file_names()]
        progress.update(task, advance=1)
    if aml_path is None:
        return run_filepaths
    files_to_download = [p for p in run_filepaths if str(p).startswith(str(aml_path))]
    if not files_to_download:
        print(f'No files found in run "{run.id}" matching "{aml_path}"')
        raise typer.Exit(code=1)
    return files_to_download


def download_files(
    run: Run,
    files_to_download: list[Path],
    out_dir: Path | None,
    dry_run: bool = False,
    force: bool = False,
) -> None:
    if out_dir is None:
        out_dir = Path(run.id)
    num_files_to_download = len(files_to_download)
    single_file = num_files_to_download == 1
    progress_class = BarlessProgress if single_file else BarProgress
    message = '' if single_file else  f'Downloading {num_files_to_download} files'
    downloaded_bytes = 0
    start = time.time()
    with progress_class(transient=True) as progress:
        task = progress.add_task(message, total=num_files_to_download)
        for found_run_filepath in files_to_download:
            out_path = out_dir / found_run_filepath
            progress.update(
                task,
                description=f'Downloading "{found_run_filepath}"',
            )
            if dry_run:
                progress.log(f'Would download "{found_run_filepath}" to "{out_path}"')
                progress.update(task, advance=1)
                continue
            if out_path.exists() and not force:
                progress.log(f'"{out_path}" already exists. Skipping')
                progress.update(task, advance=1)
                continue
            out_path.parent.mkdir(parents=True, exist_ok=True)
            run.download_file(found_run_filepath, out_path)
            filesize = out_path.stat().st_size
            downloaded_bytes += filesize
            elapsed = time.time() - start
            bytes_per_second = int(round(downloaded_bytes / elapsed))
            progress.log(f'Downloaded "{out_path}" ({naturalsize(filesize)}) [{naturalsize(bytes_per_second)}/s]')
            progress.update(task, advance=1)


class BarlessProgress(Progress):
    def __init__(self, *args, **kwargs):
        columns = [
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
        ]
        super().__init__(*columns, *args, **kwargs)


class BarProgress(Progress):
    def __init__(self, *args, **kwargs):
        columns = [
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TimeElapsedColumn(),
        ]
        super().__init__(*columns, *args, **kwargs)


if __name__ == "__main__":
    app()
