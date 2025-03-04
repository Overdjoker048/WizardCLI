from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="WizzardCLI",
    version="1.3.1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="A simple and efficient command-line tool written in Python",
    author="Overdjoker048",
    author_email="overdrawdescartes@gmail.com",
    url="https://github.com/Overdjoker048/WizzardCLI",
    packages=find_packages(),
    install_requires=[
        "colorama", "Pympler", "pywin32"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
