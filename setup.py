from setuptools import setup, find_packages
from mag import __version__

setup(
    name="mag",
    version=__version__,
    url="https://github.com/hcss-utils/MAG.git",
    author="htu",
    author_email="hcssukraine@gmail.com",
    description="MAG API wrapper",
    packages=find_packages(),
)
