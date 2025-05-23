FROM alpine AS builder

RUN apk add --no-cache make npm yarn
WORKDIR /opt/app
RUN mkdir -p ./src
COPY package.json ./
COPY yarn.lock ./
RUN cd /opt/app && yarn


FROM python:3.12-alpine

RUN apk add --no-cache git gcc g++ musl-dev
RUN pip install --no-cache-dir pipenv
WORKDIR /opt/app
COPY Pipfile ./
COPY Pipfile.lock ./
RUN pipenv install --system --deploy
COPY . ./
COPY --from=builder /opt/app/node_modules ./node_modules
COPY config.default.toml /etc/freitagsfoo-web.toml

ENV CONFIG_FILE /etc/freitagsfoo-web.toml
ENTRYPOINT ["/usr/local/bin/gunicorn","-w","10","-b","0.0.0.0:5000","--chdir", "/opt/app/src", "--timeout", "120", "app:app"]
EXPOSE 5000/tcp
