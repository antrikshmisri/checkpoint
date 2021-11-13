Setting up checkpoint in development environment
================================================

The below article explains how to setup/install checkpoint in a development environment.

*******************************
Installing checkpoint from PyPI
*******************************

Below is the command to install checkpoint from PyPI.

.. code-block:: bash

    pip install checkpoint

.. code-block:: bash

    conda install -c conda-forge checkpoint



*************************************
Installing latest development version
*************************************

Below is the command to install the latest development version of checkpoint from github.

Installing dev version for checkpoint CLI
-----------------------------------------

.. code-block:: bash

    pip install git+https://github.com/antrikshmisri/checkpoint.git@master

Installing dev version for checkpoint UI
-----------------------------------------

.. code-block:: bash

    pip install git+https://github.com/antrikshmisri/checkpoint.git@ui



*************************************************
Checkpoint in development environment setup steps
*************************************************

* Get the source code by cloning from remote repository.

    .. code-block:: bash

        git clone https://github.com/antrikshmisri/checkpoint.git

* Create and activate a virtual environment.

    .. code-block:: bash

        python -m venv venv
        source venv/bin/activate

* Get the dependencies.

    .. code-block:: bash

        pip install -r requirements/default.txt

* Install checkpoint as a local project.

    .. code-block:: bash

        pip install .

* Run the tests.

    .. code-block:: bash

        pip intall -r requirements/test.txt
        pytest -v checkpoint/tests/