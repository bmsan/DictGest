import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="dataclass_serdes",
    version="0.0.1",
    author="bmsan",
    author_email="compressedsan@gmail.com",
    description=(
        "Dictionary to dataclass loading"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=("tests",)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    url="https://github.com/bmsan/dataclass-serdes",
)