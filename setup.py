from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="espeonage",
    version="0.1.0",
    author="",
    description="A hybrid Python + Node.js tool that parses Pokémon Showdown replays",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/frxyoz/espeonage",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
    ],
    entry_points={
        "console_scripts": [
            "espeonage=espeonage.cli:main",
        ],
    },
)
