from setuptools import setup, find_packages

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
    package_dir={'': 'mermaid_py'},
    packages=find_packages(where='mermaid_py'),
    install_requires=['requests', 'dataclasses-json', 'pytest'],
)
