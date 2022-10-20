FROM mcr.microsoft.com/devcontainers/python:3.9

ENV POETRY_VERSION=1.2.1

# Install poetry
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
WORKDIR /app
COPY poetry.lock pyproject.toml /app/

# Install dependencies
RUN poetry config virtualenvs.create false && \
  poetry install --no-interaction --no-ansi

# copy files to the container
COPY . /app

# install fontforge
RUN apt-get update -y \
  && apt-get install -y --no-install-recommends software-properties-common \
  && add-apt-repository --remove ppa:fontforge/fontforge \
  && add-apt-repository -y -r ppa:fontforge/fontforge \
  && apt-get update -y \
  && apt-get install -y --no-install-recommends fontforge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*