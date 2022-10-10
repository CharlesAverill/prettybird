# prettybird

A domain-specific language for programmatically designing fonts

## Installation

Clone the repo:

```bash
git clone --recurse-submodules https://github.com/CharlesAverill/prettybird.git
```

For installing in the [poetry](https://python-poetry.org/) environment:

```bash
make install
```

For installing outside of the pip environment:

```bash
pip install .
```

For installing with Docker:

```bash
docker build . -t prettybird
docker run -it prettybird /bin/bash
```

If you're using Visual Studio Code, you can use the option `Dev Containers: Open Folder in Container...` to work on this project.

## Execution

With poetry:

```bash
make run input=[input_file]
```

With pip:

```bash
prettybird [input_file]
```
