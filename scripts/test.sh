#!/bin/bash

pip3 install black bandit pydocstyle yamllint pytest flake8 -U
black --check --diff netdoc/schemas/
black netdoc/schemas/
bandit --recursive netdoc/schemas/ --configfile .bandit.yml
flake8 netdoc/schemas/ --config .flake8
pydocstyle netdoc/schemas/
pytest
