********************************************************************************
Getting Started
********************************************************************************

Create an environment
=====================

.. raw:: html

    <div class="card">
        <div class="card-header">
            <ul class="nav nav-tabs card-header-tabs">
                <li class="nav-item">
                    <a class="nav-link active" data-toggle="tab" href="#windows">Windows</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" data-toggle="tab" href="#osx">OSX</a>
                </li>
            </ul>
        </div>
        <div class="card-body">
            <div class="tab-content">

.. raw:: html

    <div class="tab-pane active" id="windows">

In Anaconda Prompt:

.. code-block:: bash

    conda create -n fd -c conda-forge git python=3.7 COMPAS

.. raw:: html

    </div>
    <div class="tab-pane" id="osx">

In Terminal:

.. code-block:: bash

    conda create -n fd -c conda-forge git python=3.7 python.app COMPAS

.. raw:: html

    </div>
    </div>
    </div>
    </div>

Activate the environment
========================

.. code-block:: bash

    conda activate fd

Clone ``compas_fd``
======================

To clone ``compas_fd``, use your favourite Git GUI, or simply issue the following commands on the command line.

.. code-block:: bash

    git clone https://github.com/BlockResearchGroup/compas_fd.git

Install ``compas_fd``
========================

.. code-block:: bash

    cd compas_fd
    pip install -e .

Verify installation
===================

Start an interactive Python interpreter on the command line and import the installed packages.

.. code-block:: python

    >>> import compas
    >>> import compas_fd
    >>> exit()

Install in Rhino
================

Run the following command from the Anaconda Prompt (Windows) or the Terminal (OSX):

.. code-block:: bash

    python -m compas_rhino.install -p compas compas_rhino compas_fd

Install the Rhino UI
====================

Run the following command from the Anaconda Prompt (Windows) or the Terminal (OSX):

.. code-block:: bash

    python -m compas_rhino.install_plugin ui/Rhino/fd

