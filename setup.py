from setuptools import find_packages, setup

setup(
    name="rag",
    version="0.1",
    packages=find_packages(),
    py_modules=[
        "cli",
        "chunker",
        "config",
        "embeddings",
        "ingest",
        "main",
        "rag",
        "vectorstore",
    ],
    install_requires=[
        "typer",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "rag=cli:app",
        ]
    },
)
