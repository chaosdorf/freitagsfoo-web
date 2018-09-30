FROM alpine as Builder

RUN apk add --no-cache make npm yarn
WORKDIR /opt/app
RUN mkdir -p ./src
COPY package.json ./
COPY yarn.lock ./
RUN cd /opt/app && yarn
COPY src/client_templates ./src/client_templates
RUN mkdir -p ./src/static/templates \
    && cd ./src/client_templates \
    && make


FROM python:3.7-alpine

RUN apk add --no-cache git
RUN pip install --no-cache-dir pipenv
WORKDIR /opt/app
COPY Pipfile ./
COPY Pipfile.lock ./
RUN pipenv install --system --deploy
COPY . ./
COPY --from=Builder /opt/app/node_modules ./node_modules
COPY --from=Builder /opt/app/src/static/templates ./src/static/templates
COPY config.default.cfg /etc/freitagsfoo-web.cfg

ENV CONFIG_FILE /etc/freitagsfoo-web.cfg
ENTRYPOINT ["/usr/local/bin/gunicorn","-w","2","-b","0.0.0.0:5000","--chdir", "/opt/app/src", "app:app"]
EXPOSE 5000/tcp
