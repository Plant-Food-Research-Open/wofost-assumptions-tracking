# WOFOST Assumptions Tracking

[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Lint](https://github.com/Plant-Food-Research-Open/wofost-assumptions-tracking/actions/workflows/lint.yaml/badge.svg?branch=main)](https://github.com/Plant-Food-Research-Open/wofost-assumptions-tracking/actions/workflows/lint.yaml)
[![Test](https://github.com/Plant-Food-Research-Open/wofost-assumptions-tracking/actions/workflows/test.yaml/badge.svg?branch=main)](https://github.com/Plant-Food-Research-Open/wofost-assumptions-tracking/actions/workflows/test.yaml)
[![Build](https://github.com/Plant-Food-Research-Open/wofost-assumptions-tracking/actions/workflows/build.yaml/badge.svg?branch=main)](https://github.com/Plant-Food-Research-Open/wofost-assumptions-tracking/actions/workflows/build.yaml)
[![CodeQL Advanced](https://github.com/Plant-Food-Research-Open/wofost-assumptions-tracking/actions/workflows/codeql.yaml/badge.svg?branch=main)](https://github.com/Plant-Food-Research-Open/wofost-assumptions-tracking/actions/workflows/codeql.yaml)

*Assumptions tracking for WOFOST Potato using behaviour-driven development and model cards.*

# Table of contents

- [WOFOST Assumptions Tracking](#wofost-assumptions-tracking)
- [Table of contents](#table-of-contents)
- [Introduction](#introduction)
- [Quickstart](#quickstart)
- [Python Environment](#python-environment)
  - [behave](#behave)
- [Data](#data)
- [Communication](#communication)
- [Contributions and Support](#contributions-and-support)
- [License](#license)

# Introduction

This repository contains code examples for assumptions tracking of WOFOST Potato using behaviour driven development. The overall motivation behind this demonstration is to synthesise the behavior-driven development (BDD) testing approach that is more commonly used within agile software development with the calibration of mechanistic simulation models. The aim is to demonstrate how BDD can enable and facilitate communication among different disciplines using a common human-readable language. This is particularly important within highly technical scientific domains where cross-disciplinary communication may be more challenging.

BDD was chosen as it (at least in theory) facilitates collaboration and communication within multidisciplinary projects. Namely, it encourages business analysts and developers to collaborate in specifying the behaviour of software, via the use of user stories. These user stories should be written to a formal document. For this demonstration, these documents are written in the popular Gherkin syntax. Model assumptions can be documented in Gherkin, and would be recorded by business analysts as user stories.

# Quickstart

First, run the following code to install all dependencies:

```
poetry install --no-interaction
```

Secondly, execute the following to run the behaviour tests:

```
behave --verbose --summary
```

# Python Environment

## behave

[The behave package was used to implement all BDD tests.](https://behave.readthedocs.io/en/stable/index.html) These tests have been written using Gherkin syntax. [For more information on Gherkin, click here.](https://cucumber.io/docs/gherkin/reference/)

* [Feature files containing human-readable Gherkin can be found here.](features)
* [The implementation of the scenario steps can be found here.](features/steps)

# Data

* [All relevant datasets and files can be found here.](data)
* [The potato data were originally retrieved from here.](https://github.com/ajwdewit/pcse_notebooks/tree/master/data)

# Communication

Please refer to the following links:

- [GitHub Discussions] for questions.
- [GitHub Issues] for bug reports and feature requests.

[GitHub Discussions]: https://github.com/Plant-Food-Research-Open/wofost-assumptions-tracking/discussions
[GitHub issues]: https://github.com/Plant-Food-Research-Open/wofost-assumptions-tracking/issues

# Contributions and Support

Contributions are more than welcome. For general guidelines on how to contribute to this project, take a look at [CONTRIBUTING.md](https://github.com/Plant-Food-Research-Open/wofost-assumptions-tracking/tree/main/CONTRIBUTING.md).

For our community code of conduct, please also view [CODE_OF_CONDUCT.md](https://github.com/Plant-Food-Research-Open/wofost-assumptions-tracking/tree/main/CODE_OF_CONDUCT.md).

# License

This work is published under the Apache License (see [LICENSE](https://github.com/Plant-Food-Research-Open/wofost-assumptions-tracking/tree/main/LICENSE)).
