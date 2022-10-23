![Bullfinch Logo](.github/images/logo.png)

# Prettybird

A domain-specific language for programmatically designing fonts

## Installation

1. Clone the repo:
    ```bash
    git clone --recurse-submodules https://github.com/CharlesAverill/prettybird.git
    ```
2. Install [fontforge](https://fontforge.org/en-US/downloads/)
    - On Ubuntu:
        ```bash
        add-apt-repository ppa:fontforge/fontforge
        apt update
        apt install fontforge
        ```
3. Install `prettybird`
    - For usage:
        ```bash
        pip install .
        ```
    - For development (uses [poetry](https://python-poetry.org/)):
        ```
        make install
        ```
    - With Docker:
        ```bash
        docker build . -t prettybird
        docker run -it prettybird /bin/bash
        ```
        If you're using Visual Studio Code, you can use the option `Dev Containers: Open Folder in Container...` to work on this project within the built Docker container.

## Usage

Prettybird provides a CLI to read in `.pbd` (such as [examples/abcs.pbd](examples/abcs.pbd)) files and compile them to various formats.

### General Usage

```
prettybird [-h] [--format FORMAT] [--font-name FONT_NAME] [--stdout] input_file

positional arguments:
  input_file            .pbd file to compile

optional arguments:
  -h, --help            show this help message and exit
  --format FORMAT, -f FORMAT
                        Format to convert to. Supported: [BDF, SVG, TTF]
  --font-name FONT_NAME, -n FONT_NAME
                        Name to give to the output font
  --stdout              Print compiled glyph IR to stdout
```

### Within Poetry Environment

Compiles `input_file` to a TTF font

```bash
make run input=[input_file]
```
