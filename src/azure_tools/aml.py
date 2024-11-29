import tempfile
import time
import zipfile
from pathlib import Path
from typing import List
from typing import Optional

import typer
from azureml.core import Run
from azureml.core import Workspace
from azureml.exceptions import ServiceException
from humanize import naturalsize
from loguru import logger
from rich import print

from .progress import BarlessProgress
from .progress import BarProgress


def get_workspace(config_path: Path) -> Workspace:
    with BarlessProgress() as progress:
        task = progress.add_task("Getting workspace", total=1)
        workspace = Workspace.from_config(str(config_path))
        progress.update(task, advance=1)
    return workspace


def get_run(workspace: Workspace,  run_id: str) -> Run:
    with BarlessProgress() as progress:
        task = progress.add_task(f'Getting run "{run_id}"', total=1)
        try:
            run = workspace.get_run(run_id)
        except ServiceException as e:
            msg = f'Run "{run_id}" not found in workspace "{workspace.name}"'
            logger.error(msg)
            raise RuntimeError(msg) from e
        progress.update(task, advance=1)
    print(
        f'Found run with display name: "{run.display_name}"'
        f' in experiment "{run.experiment.name}"'
    )
    return run


def get_files_to_download(run: Run, aml_path: Optional[Path]) -> List[Path]:
    with BarlessProgress() as progress:
        task = progress.add_task(f'Getting files in run "{run.id}"', total=1)
        run_filepaths = [Path(p) for p in run.get_file_names()]
        progress.update(task, advance=1)
    if aml_path is None:
        return run_filepaths
    files_to_download = [p for p in run_filepaths if str(p).startswith(str(aml_path))]
    if not files_to_download:
        logger.error(f'No files found in run "{run.id}" matching "{aml_path}"')
        raise typer.Abort()
    return files_to_download


def download_files(
    run: Run,
    files_to_download: List[Path],
    out_dir: Optional[Path],
    dry_run: bool = False,
    force: bool = False,
    convert_logs: bool = False,
) -> None:
    if out_dir is None:
        out_dir = Path(run.id)
    num_files_to_download = len(files_to_download)
    single_file = num_files_to_download == 1
    progress_class = BarlessProgress if single_file else BarProgress
    message = '' if single_file else f'Downloading {num_files_to_download} files'
    downloaded_bytes = 0
    start = time.time()
    with progress_class(transient=True) as progress:
        task = progress.add_task(message, total=num_files_to_download)
        for found_run_filepath in files_to_download:
            out_path = out_dir / found_run_filepath
            if 'log' in str(out_path) and out_path.suffix == '.txt' and convert_logs:
                out_path = out_path.with_suffix('.log')
            progress.update(
                task,
                description=f'Downloading "{found_run_filepath}"',
            )
            if dry_run:
                progress.log(f'Would download "{found_run_filepath}" to "{out_path}"')
                progress.update(task, advance=1)
                continue
            if out_path.exists() and not force:
                logger.warning(
                    f'Skipping "{out_path}" as it already exists.'
                    ' Use --force to overwrite'
                )
                progress.update(task, advance=1)
                continue
            out_path.parent.mkdir(parents=True, exist_ok=True)
            run.download_file(found_run_filepath, out_path)
            filesize = out_path.stat().st_size
            downloaded_bytes += filesize
            elapsed = time.time() - start
            bytes_per_second = int(round(downloaded_bytes / elapsed))
            size_human = naturalsize(filesize)
            speed_human = naturalsize(bytes_per_second)
            progress.log(f'Downloaded "{out_path}" ({size_human}) [{speed_human}/s]')
            progress.update(task, advance=1)


def download_snapshot(run: Run, out_dir: Optional[Path]) -> None:
    if out_dir is None:
        out_dir = Path(tempfile.gettempdir(), f'snapshot_{run.id}')

    with BarlessProgress() as progress:
        task = progress.add_task(f'Downloading snapshot from"{run.id}"', total=1)
        zip_path = run.restore_snapshot(path=str(out_dir))
        progress.update(task, advance=1)
    unzip(Path(zip_path), out_dir)


def unzip(zip_path: Path, out_dir: Path) -> None:
    with BarlessProgress() as progress:
        task = progress.add_task(f'Unzipping "{zip_path}"', total=1)
        out_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(out_dir)
        progress.update(task, advance=1)
    print(f'Unzipped snapshot to "{out_dir}"')
