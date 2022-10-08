# prettybird

A domain-specific language for programmatically designing fonts

## Installation

```bash
conda create -n prettybird python==3.9
conda activate prettybird

conda install poetry
poetry install
```

For installing outside of the conda environment:

```bash
pip install .
```

For installing with Docker:

```bash
docker build . -t prettybird
docker run -it prettybird /bin/bash
```

If you use Visual Studio Code, you can use the option `Dev Containers: Open Folder in Container...`.

## Execution

```bash
prettybird [input_file]
```
