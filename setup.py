from setuptools import find_packages, setup

setup(
    name="atlas",
    version="0.1",
    package_dir={"": "src"},
    packages=find_packages("src"),
    install_requires=[
        "typer",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "atlas=atlas.cli:app",
        ]
    },
)
