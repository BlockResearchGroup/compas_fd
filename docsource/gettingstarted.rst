********************************************************************************
Getting Started
********************************************************************************

``compas_fofin`` uses ``cvxpy`` and ``cplex`` in some of its algorithms.
We will make these optional dependencies in the future,
but in the meantime please follow the instructions below to get these properly installed.

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

Make sure to install the Visual Studio C++ compiler for Python 2.7
or the Visual Studio build tools for Python 3, as instructued in the `CVXPY docs <https://www.cvxpy.org/install/index.html>`_

Afterwards, in Anaconda Prompt:

.. code-block:: bash

    conda create -n fofin python=3.6 pip
    conda activate fofin
    pip install cvxpy
    conda install -c ibmdecisionoptimization cplex
    conda install -c conda-forge COMPAS
    pip install git+https://github.com/BlockResearchGroup/compas_fofin.git#egg=compas_fofin

.. raw:: html

    </div>
    <div class="tab-pane" id="osx">

In Terminal:

.. code-block:: bash

    conda create -n fofin python=3.6 pip python.app
    conda activate fofin
    pip install cvxpy
    conda install -c ibmdecisionoptimization cplex
    conda install -c conda-forge COMPAS
    pip install git+https://github.com/BlockResearchGroup/compas_fofin.git#egg=compas_fofin

.. raw:: html

    </div>
    </div>
    </div>
    </div>
