from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="PyScreenUtils",
    version="0.1.0",
    author="KrisTHL181",
    author_email="KrisTHL181@outlook.com",
    description="Terminal utils.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KrisTHL181/PyScreenUtils",
    packages=find_packages(),
    install_requires=[
        "colorama"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
