<span align="center"> 
 
  # Checkpoint

</span>
<br />

<span align="center">

<div>
 
[![checkpoint logo](https://github.com/antrikshmisri/checkpoint/blob/master/docs/_static/logo.png?raw=true)](http://checkpoint.antriksh.live/)

</div>
<br />

[![pip install pycheckpoint](https://raw.githubusercontent.com/antrikshmisri/DATA/34bf992f0f7f6e265d33b193e460ec073579551b/imgs/pip-install-pycheckpoint.svg)](https://github.com/antrikshmisri/checkpoint)

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/) [![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)
  
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/db5e64ce3b644109afe0c6ed96f266b8)](https://www.codacy.com/gh/antrikshmisri/checkpoint/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=antrikshmisri/checkpoint&amp;utm_campaign=Badge_Grade) ![codecov.io](https://codecov.io/github/antrikshmisri/checkpoint/coverage.svg?branch=master) [![Maintainability](https://api.codeclimate.com/v1/badges/d530dec72a679fe43d46/maintainability)](https://codeclimate.com/github/antrikshmisri/checkpoint/maintainability)


[![GitHub release](https://img.shields.io/github/release/antrikshmisri/checkpoint)](https://GitHub.com/Naereen/StrapDown.js/releases/) [![Downloads](https://pepy.tech/badge/pycheckpoint)](https://pepy.tech/project/pycheckpoint)


[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

 
<div>
 
<b> Checkpoint is a tool that helps you to create restore points for your project <br/>
Unlike other tools like git, checkpoint makes the whole process as simple as a few click <br/>
Plus, there is no need for a remote repository, checkpoint does everything locall <br/>
</b>

</div>
 
</span>
<br />


## How does it work?

Checkpoint provides multiple `Sequence` classes that have memeber functions which execute based on their order in the sequence. These sequences are used to perform all the sequentional operations that are required to create a restore point. Some of these sequences are:

* `IOSequence`: This sequence is used to perfrom all the input/output sequentional operations.
* `CLISequence`: This sequence is used to perform all the CLI operations which includes parsing the arguments, determining the action and performing the action.

Checkpoint also supports custom sequences that can be used to initialize checkpoint in different environments. For example, if checkpoint isto be initialized in a UI enviroment a sequence for UI can be created and passed to the `Checkpoint` constructor.

**Detailed documentation can be found [here](http://checkpoint.antriksh.live/)**

## How to use checkpoint?

To run checkpoint in UI environment, run the following command:

##### Run checkpoint in UI environment
```bash
checkpoint --run-ui
```

The following is an example of how to use checkpoint in a CLI environment.

##### Initialize checkpoint in the target project
```bash
checkpoint --action=init --path=path/to/project 
```
*After initialization a `.checkpoint` directory is created in the target project. If the project is git initialized, this directory should be added to the git ignore file.*

##### Creating a restore point
```bash
checkpoint --name=restore_point_name --action=create --path=path/to/project
```

##### Jumping to a restore point
```bash
checkpoint --name=restore_point_name --action=restore --path=path/to/project
```

##### Deleting a restore point
```bash
checkpoint --name=restore_point_name --action=delete --path=path/to/project
```

##### Version of checkpoint
```bash
checkpoint --name=restore_point_name --action=version --path=path/to/project
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
pip install -r requirements/default.txt
```
##### 4. Install checkpoint as a local project.
```bash
pip install .
```
##### 5. Run the tests
```bash
pip intall -r requirements/test.txt
pytest -v checkpoint/tests/
```

## Code of Conduct

Please go through the code of conduct before contributing to this project which can be found [here](./CODE_OF_CONDUCT.md). 


## Screenshots

<img width="749" alt="Screenshot 2021-11-09 222450" src="https://user-images.githubusercontent.com/54466356/140969067-6e845c1a-dc7d-4985-a0e1-d47583eb0523.png">


<img width="746" alt="Screenshot 2021-11-09 222154" src="https://user-images.githubusercontent.com/54466356/140968797-ab4fa175-0692-4fdf-937b-5cfb88a8a2ab.png">


