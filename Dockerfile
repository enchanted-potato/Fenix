FROM python:3.10

WORKDIR /Fenix

ARG POETRY_VERSION=1.3.1

RUN curl -sSL https://install.python-poetry.org | python - --version $POETRY_VERSION
ENV PATH /root/.local/bin:$PATH

RUN poetry --version

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-interaction --no-ansi

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py"]
