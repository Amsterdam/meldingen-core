FROM python:3.12

WORKDIR /opt/meldingen-core

# Install Poetry
RUN set eux; \
    curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python; \
    cd /usr/local/bin; \
    ln -s /opt/poetry/bin/poetry; \
    poetry config virtualenvs.create false; \
    poetry self add poetry-plugin-sort

COPY ./pyproject.toml ./poetry.lock /opt/meldingen-core/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN set -eux; \
    if [ "$INSTALL_DEV" = "true" ]; then \
      poetry install --no-root; \
    else \
      poetry install --no-root --only main; \
    fi

COPY . /opt/meldingen-core
ENV PYTHONPATH=/opt/meldingen-core
