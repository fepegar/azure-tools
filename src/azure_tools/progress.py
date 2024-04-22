from rich.progress import BarColumn
from rich.progress import MofNCompleteColumn
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.progress import TimeElapsedColumn


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
