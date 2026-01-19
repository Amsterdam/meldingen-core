FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /opt/meldingen-core

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT="/usr/local"

COPY pyproject.toml uv.lock* ./

ARG INSTALL_DEV=false
RUN if [ "$INSTALL_DEV" = "true" ]; then \
      uv sync --frozen --no-install-project; \
    else \
      uv sync --frozen --no-install-project --no-dev; \
    fi

COPY . .

ENV PYTHONPATH=/opt/meldingen-core