from setuptools import setup, find_packages

setup(
    name='NeuroProcessing',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        "numpy","pandas","pathlib2","pathlib",
        "openpyxl","matplotlib"
    ],
    # MANIFEST.in を使うために必要
    include_package_data=True,
    python_requires=">=3.7"
)