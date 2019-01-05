
from setuptools import setup, find_packages

setup(
    name='clutrr',
    version='2.0.0',
    description='Compositional Language Understanding with Text-based Relational Reasoning',
    packages=find_packages(exclude=(
        'data', 'mturk')),
    include_package_data=True,
)
