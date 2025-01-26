# pull official base image
FROM python:3.11-slim-buster

# set working directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc postgresql curl \
  && apt-get clean

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
# Add poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# copy the poetry configuration files
COPY ./pyproject.toml ./poetry.lock* /usr/src/app/

# install python dependencies (including dev dependencies)
RUN poetry install --no-root  # This installs both regular and dev dependencies

# add app
COPY . .
