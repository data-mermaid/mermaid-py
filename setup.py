from setuptools import setup, find_packages
from os.path import basename
from os.path import splitext
from glob import glob

# Load the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='mermaid-py',
    version='0.0.1',
    license='LICENSE.txt',
    description='Through mermaid-py you can access data from MERMAID directly in Python.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    install_requires=['requests'],
)
