from setuptools import setup
from src.cli import DESC

setup(
    name='tester',
    version='0.0.1',
    description=DESC,
    url='https://github.com/domsleee/tester',
    author='Dom Slee',
    author_email='domslee97@gmail.com',
    license='MIT',
    packages=['src'],
    zip_safe=True,
    entry_points={
        'console_scripts': ['tester=src.cli:main']
    }
)
