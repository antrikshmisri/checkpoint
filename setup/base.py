from subprocess import Popen, PIPE

from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, BarColumn
from rich.markdown import Markdown


class SetupBase:
    """Base class for `installer` and `uninstaller`"""

    def __init__(self, title, description):
        self.title = title
        self.description = description

        self._task_map = {}
        self._task_id_map = {}
        self._progress = Progress(
            SpinnerColumn(), TextColumn("{task.description}"), BarColumn(), TimeElapsedColumn())

        _start_msg_markdown = Markdown(
            f"# {self.title}\n *{self.description}*")

        self._progress.console.log(
            _start_msg_markdown, justify="center", markup=True)

    def start(self):
        """Start the setup"""
        self._progress.start()

        for task_name, callback in self._task_map.items():
            callback(self, task_name)

        if self._progress.finished:
            print(f"[green]{self.title} has finished successfully![/]")
        else:
            print(f"[red]{self.title} has failed![/]")

        self._progress.stop()

    def add_task(self, task_name, total, callback=lambda SetupBase, task_name: None):
        """Add a task to the setup"""
        self._task_map[task_name] = callback

        _current_task_id = self._progress.add_task(
            description=task_name,
            total=total,
            start=True
        )

        self._task_id_map[task_name] = _current_task_id

    def get_task_id(self, task_name):
        """Get the task id for a task"""
        return self._task_id_map[task_name]

    def _run_command(self, command):
        """Run a command and return the `returncode`, `stdout` and `stderr`

        Parameters
        ----------
        command: str
            Command to run
        """
        _process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        _process.wait()

        _result_dict = {
            "returncode": _process.returncode,
            "stdout": _process.stdout.read().decode("utf-8"),
            "stderr": _process.stderr.read().decode("utf-8")
        }

        return _result_dict

    def log(self, message):
        """Log a message to the console"""
        self._progress.console.log(message)
