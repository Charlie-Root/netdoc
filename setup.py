"""
Install with: python3 setup.py install
Develop with: python3 setup.py develop
Make it available on PIP with:
    python3 setup.py sdist
    pip3 install twine
    twine upload dist/*
"""

__author__     = 'Andrea Dainese'
__contact__    = 'andrea@adainese.it'
__copyright__  = 'Copyright 2022, Andrea Dainese'
__license__    = 'GPLv3'
__date__       = '2022-09-07'
__version__    = '0.9.8'

from setuptools import find_packages, setup

setup(
    name='netdoc',
    version=__version__,
    description='Network Documentation plugin for NetBox',
    url='https://github.com/dainok/netdoc',
    author='Andrea Dainese',
    author_email='andrea.dainese@pm.me',
    license='GNU v3.0',
    install_requires=['python-slugify', 'nornir==3.3.0', 'nornir_utils==0.2.0', 'nornir_netmiko==0.1.2', 'ipaddress', 'macaddress', 'ouilookup'],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
    ],
    project_urls={
        'Source': 'https://github.com/dainok/netdoc',
    },
)
