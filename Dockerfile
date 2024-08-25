FROM python:3.11.4-alpine3.18 as base

RUN mkdir /src
COPY src /src
WORKDIR /src

RUN apk add git bash net-tools && \
  apk add gcc g++ && \
  apk add python3-dev musl-dev && \
  apk add linux-headers && \
  apk add --no-cache sqlite && \
  apk add msttcorefonts-installer fontconfig && \
  update-ms-fonts && \
  fc-cache -f

from base as base2

# redis
RUN apk add --update redis


FROM base2 as base3

# node
RUN apk add --update npm && \
  npm install -g eslint && npm install -g standard && \
  npm ci

FROM base3 as node_base

# python
RUN pip install --upgrade pip && pip install -r requirements.txt

FROM node_base as python_base

SHELL ["/bin/bash", "-c"]
EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=app.settings
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
