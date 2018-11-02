#!/usr/bin/env python3
import setuptools
from tester.cli import DESC

setuptools.setup(
    name='tester',
    version='0.0.1',
    description=DESC,
    url='https://github.com/domsleee/tester',
    author='Dom Slee',
    author_email='domslee97@gmail.com',
    license='MIT',
    zip_safe=True,
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['tester=tester.cli:cli_entry']
    }
)
