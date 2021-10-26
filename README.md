# checkpoint
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/db5e64ce3b644109afe0c6ed96f266b8)](https://www.codacy.com/gh/antrikshmisri/checkpoint/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=antrikshmisri/checkpoint&amp;utm_campaign=Badge_Grade) ![codecov.io](https://codecov.io/github/antrikshmisri/checkpoint/coverage.svg?branch=master) [![GitHub release](https://img.shields.io/github/release/antrikshmisri/checkpoint)](https://GitHub.com/Naereen/StrapDown.js/releases/) [![Downloads](https://pepy.tech/badge/pycheckpoint)](https://pepy.tech/project/pycheckpoint) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)


[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)




## Create restore points for your project locally

Checkpoint is a tool that helps you to create restore points for your project. This is very similar to git tagging, the only difference between these two is that checkpoint doesn't require the project to be git initialized. It also doesn't require you to have a git remote. 

## How does it work?

Checkpoint provides multiple `Sequence` classes that have memeber functions which execute based on their order in the sequence. These sequences are used to perform all the sequentional operations that are required to create a restore point. Some of these sequences are:

* `IOSequence`: This sequence is used to perfrom all the input/output sequentional operations.
* `CLISequence`: This sequence is used to perform all the CLI operations which includes parsing the arguments, determining the action and performing the action.

Checkpoint also supports custom sequences that can be used to initialize checkpoint in different environments. For example, if checkpoint isto be initialized in a UI enviroment a sequence for UI can be created and passed to the `Checkpoint` constructor.

## How to use checkpoint?

Currently, checkpoint can only be used in a CLI environment. The following is an example of how to use checkpoint in a CLI environment.

##### Initialize checkpoint in the target project
```bash
checkpoint --action=init --path=path/to/project 
```
*After initialization a `.checkpoint` directory is created in the target project. If the project is git initialized, this directory should be added to the git ignore file.*

##### Creating a restore point
```bash
checkpoint --name=restore_point_name --action=create --path=path/to/project
```

##### Restoring a restore point
```bash
checkpoint --name=restore_point_name --action=restore --path=path/to/project
```

##### Deleting a restore point
```bash
checkpoint --name=restore_point_name --action=delete --path=path/to/project
```

## Installation

`pip install pycheckpoint`
### Development

##### 1. Get the source code by cloning from remote repository.
```bash
git clone https://github.com/antrikshmisri/checkpoint.git
```

##### 2. Create and activate a virtual environment.
```bash
python -m venv venv
source venv/bin/activate
```

##### 3. Get the dependencies
```bash
pip install -r requirements.txt
```
##### 4. Install checkpoint as a local project.
```bash
pip install .
```
##### 5. Run the tests
```bash
pytest -v checkpoint/tests/
```

## Code of Conduct

Please go through the code of conduct before contributing to this project which can be found [here](./CODE_OF_CONDUCT.md). 


## Screenshots
<img width="746" alt="Screenshot 2021-10-24 225447" src="https://user-images.githubusercontent.com/54466356/138605625-0ac01b1e-5bb7-425c-b39f-6f5eca683ffb.png">
<img width="746" alt="Screenshot 2021-10-24 225716" src="https://user-images.githubusercontent.com/54466356/138605628-33d36bfb-cd5f-4239-b611-73d4b3900b77.png">


