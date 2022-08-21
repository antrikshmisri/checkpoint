import os
import json
from subprocess import check_call, PIPE, Popen, CalledProcessError
from functools import partial
from urllib.request import urlretrieve

from shutil import rmtree

from setup.base import SetupBase


class Installer(SetupBase):
    """Class to install the application"""

    def __init__(self, title, description):
        """Constructor for the installer class

        Parameters
        ----------
        title : str
            The title of the installer
        description : str
            The description of the installer
        """
        super(Installer, self).__init__(
            title=title,
            description=description
        )

        self._os_info_map = {}
        self.prequisite_dependencies = []
        self._application_components = []

        self._process_os_info()

    def _process_os_info(self):
        """Process the OS info and add it to the os info map"""
        # determine which universal package manager to use for the current OS
        _os_name = os.name
        _os_package_manager_map = {
            "nt": ["winget"],
            "posix": ["apt", "yum", "dnf", "pacman", "zypper", "brew"],
            "darwin": ["brew"],
            "linux": ["apt"]
        }
        _pkg_manager_install_command_map = {
            "apt": "sudo apt install",
            "yum": "sudo yum install",
            "dnf": "sudo dnf install",
            "pacman": "sudo pacman -S",
            "zypper": "sudo zypper install",
            "brew": "brew install"
        }

        _pkg_manager_uninstall_command_map = {
            "apt": "sudo apt remove",
            "yum": "sudo yum remove",
            "dnf": "sudo dnf remove",
            "pacman": "sudo pacman -R",
            "zypper": "sudo zypper remove",
            "brew": "brew uninstall"
        }

        _pkg_manager_update_command_map = {
            "apt": "sudo apt update",
            "yum": "sudo yum update",
            "dnf": "sudo dnf update",
            "pacman": "sudo pac --noconfirm -Sy",
            "zypper": "sudo zypper update",
            "brew": "brew update"
        }

        self._os_info_map["os_name"] = _os_name

        # determine which package manager to use if current OS is posix by installing a small test package
        if _os_name in _os_package_manager_map:

            if len(_os_package_manager_map[_os_name]) > 0:
                for _package_manager in _os_package_manager_map[_os_name]:
                    if self._test_package_manager(_package_manager):
                        self._os_info_map["package_manager"] = _package_manager
                        break
                    else:
                        continue

                if "package_manager" not in self._os_info_map:
                    raise Exception(f"No package manager found for {_os_name}")
            else:
                self._os_info_map["package_manager"] = _os_package_manager_map[_os_name][0]

        self._os_info_map["install"] = _pkg_manager_install_command_map[self._os_info_map["package_manager"]]
        self._os_info_map["uninstall"] = _pkg_manager_uninstall_command_map[self._os_info_map["package_manager"]]
        self._os_info_map["update"] = _pkg_manager_update_command_map[self._os_info_map["package_manager"]]

        self.log(
            f"Installer Config: {json.dumps(self._os_info_map, indent=4)}")

    def _test_package_manager(self, package_manager):
        """Test if a package manager is compatible with current OS

        Parameters
        ----------
        package_manager : str
            The package manager to test

        Returns
        -------
        bool
            True if compatible, False otherwise
        """
        _package_manager_alias_map = {
            "apt": "apt-get",
            "yum": "yum",
            "dnf": "dnf",
            "pacman": "pacman",
            "zypper": "zypper",
            "brew": "brew"
        }

        if package_manager in _package_manager_alias_map:
            package_manager = _package_manager_alias_map[package_manager]

        # check if package manaager is available on current OS
        _package_manager_test_command = {
            "apt": "apt-get --version",
            "yum": "yum --version",
            "dnf": "dnf --version",
            "pacman": "pacman --version",
            "zypper": "zypper --version",
            "brew": "brew --version"
        }

        if package_manager in _package_manager_test_command:
            _command = _package_manager_test_command[package_manager]
        else:
            _command = package_manager

        try:
            check_call(
                _command, shell=True, stdout=PIPE, stderr=PIPE)
        except CalledProcessError:
            return False

        return True

    def install_dependecy(self, dependency, dep_check_command=None):
        """Install a dependency

        Parameters
        ----------
        dependency : str
            The dependency to install
        dep_check_command : str, optional
            Command to check if the dependency is already installed
        """
        dep_check_command = dep_check_command or ""

        _return_dict = self._run_command(dep_check_command)
        _returncode = _return_dict["returncode"]

        if _returncode == 0:
            self.log(
                f"{dependency} is already installed, skipping...")

            return

        _commands = [
            self._os_info_map["update"],
            f"{self._os_info_map['install']} {dependency}"
        ]

        for _command in _commands:
            _return_dict = self._run_command(_command)

            _returncode = _return_dict["returncode"]
            _stderr = _return_dict["stderr"]

            if _returncode != 0:
                self.log(
                    f"[red]Failed to install {dependency}[/]")

                self.log(
                    f"[red]{_stderr}[/]")

                raise Exception(f"Failed to install {dependency}")
            else:
                self.log(
                    f"[green]{dependency} installed![/]")

    def uninstall_dependency(self, dependency):
        """Uninstall a dependency

        Parameters
        ----------
        dependency : str
            The dependency to uninstall
        """
        _commands = [
            f"{self._os_info_map['uninstall']} {dependency}"
        ]

        for _command in _commands:
            _return_dict = self._run_command(_command)

            _returncode = _return_dict["returncode"]
            _stderr = _return_dict["stderr"]

            if _returncode != 0:
                self.log(
                    f"[red]Failed to uninstall {dependency}[/]")

                self.log(
                    f"[red]{_stderr}[/]")

                raise Exception(f"Failed to uninstall {dependency}")
            else:
                self.log(
                    f"[green]{dependency} uninstalled![/]")

    def add_prequisite_dependency(self, dependency):
        """Add prequisite dependency to the setup

        Parameters
        ----------
        dependency : str
            The dependency to add
        """
        self.prequisite_dependencies.append(dependency)

    def add_application_component(self, component):
        """Add application component to the setup

        Parameters
        ----------
        component: dict
            The component to add, should include the following keys:
                - name: the name of the component
                - package_manager_installable: whether the component is installable by the package manager
                - install_command: the command to install the component
                - install_url: the url to download the component
        """
        self._application_components.append(component)


def _install_prequisite_dependencies(installer, task_name, prequisite_dependencies):
    """Install prequisite dependencies

    Parameters
    ----------
    installer : :class: `install.Installer`
        The installer object
    task_name : str
        The task name
    prequisite_dependencies : list of str
        The prequisite dependencies
    """
    _dep_check_command_map = {
        "python@3.8": "python3 --version"
    }

    task_id = installer.get_task_id(task_name)
    for _dependency in prequisite_dependencies:
        installer.add_prequisite_dependency(_dependency)

    for _dependency in installer.prequisite_dependencies:
        installer._progress.update(
            task_id, description=f"Installing {_dependency}")

        installer.install_dependecy(
            _dependency, _dep_check_command_map.get(_dependency, None))

        installer._progress.update(task_id, advance=1)

    installer._progress.update(
        task_id, description="Prequisite dependencies installed!")


def _post_installation_commands(installer, task_name, post_install_commands):
    """Run commands after prequisite dependencies have been installed.

    Parameters
    ----------
    installer: :class: `install.Installer`
        The installer object
    taks_name: str
        The task name
    post_install_commands : list of str
        The post install commands
    """
    task_id = installer.get_task_id(task_name)

    for _command in post_install_commands:
        installer._progress.update(
            task_id, description=f"Running {_command}")

        _process = Popen(
            _command, shell=True, stdout=PIPE, stderr=PIPE)
        _process.wait()

        if _process.returncode != 0:
            installer.log(
                f"[red]Failed to run {_command}[/]")

            installer.log(
                f"[red]{_process.stderr.read().decode('utf-8')}[/]")

            raise Exception(f"Failed to run {_command}")
        else:
            installer.log(
                f"[green]{_command} completed![/]")

        installer.log(
            f"[green]{_command}: Post install command completed[/]")

        installer._progress.update(task_id, advance=1)


def _install_application_components(installer, task_name, component_dependencies):
    task_id = installer.get_task_id(task_name)

    def _handle_external_installation(component):
        """Handle external installation of application component

        Parameters
        ----------
        component: dict
            The component to be installed
        task_name: str
            The task name
        component_dependencies: list of dict
            The list of components that are dependencies of the component
        """
        _download_url = component["install_url"]
        _user_directory = os.path.expanduser("~")
        _installation_path = os.path.join(
            _user_directory, ".checkpoint")

        if not os.path.exists(_installation_path):
            os.makedirs(_installation_path)

        # download the component to the installation path using urlretrieve
        _download_path = os.path.join(
            _installation_path, os.path.basename(_download_url))

        if not os.path.exists(_download_path):
            urlretrieve(_download_url, _download_path)

    def _handle_command_installation(component):
        """Handle command installation of application component

        Parameters
        ----------
        component: dict
            The component to be installed
        """
        _command = component["install_command"]
        _return_dict = installer._run_command(_command)

        _returncode = _return_dict["returncode"]
        _stderr = _return_dict["stderr"]
        _stdout = _return_dict["stdout"]

        installer.log(
            _stdout)

        if _returncode != 0:
            installer.log(
                f"[red]{_stderr}[/]")

            raise Exception(f"Failed to install {component['name']}")

    def _determine_install_type(component):
        """Determine what type of installation is required for the component

        Parameters
        ----------
        component: dict
            The component to be installed

        Returns
        -------
        str
            The type of installation required
        """
        if component["package_manager_installable"]:
            return "package_manager"
        elif component["install_command"]:
            return "command"
        elif component["install_url"]:
            return "external"
        else:
            raise ValueError("Couldn't determine intallation strategy")

    _install_strategy2method = {
        "package_manager": installer.install_dependecy,
        "command": _handle_command_installation,
        "external": _handle_external_installation
    }

    # install application components
    for _component in component_dependencies:
        installer._progress.update(
            task_id, description=f"Installing {_component['name']}")

        _strat = _determine_install_type(_component)

        if _strat == "package_manager":
            installer.install_dependecy(_component["name"])
        else:
            _install_strategy2method[_strat](_component)

        installer._progress.update(task_id, advance=1)

    installer._progress.update(
        task_id, description="Application components installed!")

    installer._progress.update(task_id, advance=1)

    def _remove_prequisite_deps():
        """Remove prerequisite dependencies"""
        installer._progress.update(
            task_id, description="Removing prerequisite dependencies"
        )

        for _dependency in installer.prequisite_dependencies:
            installer.uninstall_dependency(_dependency)

        installer._progress.update(task_id, advance=1)

    # skip venv cleanup for now
    # _remove_venv()
    _remove_prequisite_deps()

    installer._progress.update(
        task_id, description="Post installation cleanup complete!")


def _post_install_cleanup(installer, task_name):
    """Remove any artifacts left post-installation

    Parameters
    ----------
    installer: :class: `install.Installer`
        The installer object
    task_name: str
        Name of the task
    """
    task_id = installer.get_task_id(task_name)

    def _remove_venv():
        """Remove the virtual environment"""
        installer._progress.update(
            task_id, description="Removing virutal environment"
        )

        _venv_path = os.path.join(
            os.path.join(os.path.abspath(os.path.dirname(__file__))),
            "venv"
        )

        installer.log(
            f"[green]Removing {_venv_path}[/]")

        if os.path.exists(_venv_path):
            rmtree(_venv_path)

        installer._progress.update(task_id, advance=1)


def install():
    installer = Installer(title="Install checkpoint",
                          description="Your installation is starting, it may take a while...")

    _prequisite_deps = [
        "python@3.8"
    ]

    _post_install_commands = [
        "python3 -m pip install --upgrade pip"
    ]

    _component_deps = [
        {
            "name": "Checkpoint CLI Tool",
            "package_manager_installable": False,
            "install_command": "pip3 install git+https://github.com/antrikshmisri/checkpoint.git@master",
            "install_url": None,
        },
        {
            "name": "Checkpoint GUI",
            "package_manager_installable": False,
            "install_command": None,
            "install_url": "https://github.com/antrikshmisri/checkpoint/releases/download/v1.3/checkpoint.exe"
        }
    ]

    installer.add_task(task_name="Installing prequisite dependencies",
                       callback=partial(
                           _install_prequisite_dependencies, prequisite_dependencies=_prequisite_deps),
                       total=len(_prequisite_deps))

    installer.add_task(task_name="Running post-installation commands",
                       callback=partial(
                           _post_installation_commands, post_install_commands=_post_install_commands),
                       total=len(_post_install_commands))

    installer.add_task(task_name="Installing application components",
                       callback=partial(
                           _install_application_components, component_dependencies=_component_deps),
                       total=len(_component_deps))

    # installer.add_task(task_name="Performing post-installation cleanup",
    #                    callback=_post_install_cleanup, total=1)

    installer.start()


if __name__ == "__main__":
    install()
