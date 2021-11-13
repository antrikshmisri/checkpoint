Getting Started with Checkpoint CLI Tool
========================================

The following article explains the basics of the Checkpoint CLI tool
as well as how to use the CLI tool.

****************************
What is Checkpoint CLI Tool?
****************************

Checkpoint CLI Tool is a command line interface (CLI) tool that allows you to perform the following actions:

* Create restore points in your project locally/headlessly
* Jump back and forth between restore points without worrying about changed files
* Delete unwanted restore points
* Exporting the project snapshot based on the restore points
* Simple, clutter-free yet modern looking user interface
* Modifying the tool to use custom user interface

************************
What is a restore point?
************************

A restore point in checkpoint is essentially a snapshot of the project at a specific point in time.
This is represented as a directory with the name of the restore point. The checkpoint initialized directory contains a .checkpoint directory,
which contains all the restore points and related information. The directory structure of .checkpoint is as follows:


::

    Target Directory
    │   .config
    │   crypt.key
    ├───v1.0
    │       .metadata
    │       v1.0.json
    ├───v1.1
    │      .metadata
    │       v1.1.json
    └───v1.2
            .metadata
            v1.2.json


Each restore point has a few files that hold certain information about the restore point. These files are:

* .metadata: This file contains the metadata of the restore point which includes all root directories and files present inside them.
* .json: This file contains all files present in the target directory and the hash associated with them.

The .checkpoint directory contains some files that are used to store some global information about the project. These files are:

* .config: This file contains the configuration of the project which includes current checkpoint, all checkpoints etc.
* crypt.key: This file contains the encryption key used to encrypt/decrypt the project files.


*****************************
Using the Checkpoint CLI Tool
*****************************

Checkpoint provides a command line interface (CLI) tool as well as a user interface (TBD) following is a quick overview of the CLI tool:

Initializing the project with checkpoint
----------------------------------------

.. code-block:: bash

    $ checkpoint --path=<path> --action=init --name=<name> --ignore-dirs=<dirs>

Creating a restore point/checkpoint
-----------------------------------

.. code-block:: bash

    $ checkpoint --path=<path> --action=create --name=<name> --ignore-dirs=<dirs>

Jumping to a restore point/checkpoint
-------------------------------------

.. code-block:: bash

    $ checkpoint --path=<path> --action=restore --name=<name>

Deleting a restore point/checkpoint
-----------------------------------

.. code-block:: bash

    $ checkpoint --path=<path> --action=delete --name=<name>

Version of the tool
-------------------

.. code-block:: bash

    $ checkpoint --action=version --path=<path>

Running GUI version of the tool (TBD)
-------------------------------------

.. code-block:: bash

    $ checkpoint --run-ui
