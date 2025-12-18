Quickstart
==========

First, run the following code to install all dependencies:

.. code-block:: bash

    poetry install --no-interaction

Secondly, execute the following to run the behaviour tests:

.. code-block:: bash

    behave --verbose --summary

Python Environment
==================

behave
------

`The behave package was used to implement all BDD tests. <https://behave.readthedocs.io/en/stable/index.html>`_
These tests have been written using Gherkin syntax. `For more information on Gherkin, click here. <https://cucumber.io/docs/gherkin/reference/>`_

* Feature files containing human-readable Gherkin can be found here: :file:`features`
* The implementation of the scenario steps can be found here: :file:`features/steps`

Data
====

* The potato data were originally retrieved from here: `https://github.com/ajwdewit/pcse_notebooks/tree/master/data`_
