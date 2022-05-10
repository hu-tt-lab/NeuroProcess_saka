from setuptools import setup, find_packages

setup(
    name='NeuroProcessing',
    version='0.0',
    packages=find_packages(),
    # MANIFEST.in を使うために必要
    include_package_data=True
)