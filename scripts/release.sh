#!/bin/bash

CURRENT_RELEASE=$(fgrep __version__ setup.py | sed '/^__version__/!d' | sed "s/^__version__\ *=\ *'\([0-9.]\+\)'$/\1/")
NEXT_RELEASE=$1

if [ "${NEXT_RELEASE}" == "" ]; then
    echo Missing next release parameter
    exit 1
fi

find . -type f -name "*.py" -exec sed -i "s/^__version__.*$/__version__    = '${NEXT_RELEASE}'/g" {} \;
find . -type f -name "*.html" -exec sed -i "s/^__version__.*$/__version__    = '${NEXT_RELEASE}'/g" {} \;

python3 setup.py sdist
twine upload dist/*
git tag ${NEXT_RELEASE}
git push origin --tags