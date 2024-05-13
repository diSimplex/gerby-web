# See: https://gerby-project.github.io/
# See: https://github.com/gerby-project/gerby-website

FROM python:latest

RUN set -eux && \
  mkdir /gerby-website && \
  mkdir /gerby-website/gerbyRunner

COPY pyproject.toml /gerby-website
COPY gerbyRunner /gerby-website/gerbyRunner

RUN set -eux && \
  pip install ./gerby-website && \
  python -c "import gerbyRunner.postInstall; gerbyRunner.postInstall.patches()" && \
  mkdir /gerby-data

WORKDIR /gerby-website

ENTRYPOINT [ "gerbyRunner", "-v", "/gerby-data/config.yaml"]
