FROM alpine as Builder

RUN apk add --no-cache make npm yarn
WORKDIR /opt/app
COPY . /opt/app/
RUN cd /opt/app && yarn
RUN mkdir -p /opt/app/src/static/templates \
    && cd /opt/app/src/client_templates \
    && make


FROM python:3.7-alpine

RUN apk add --no-cache git
RUN pip install --no-cache-dir pipenv
WORKDIR /opt/app
COPY --from=Builder /opt/app .
RUN pipenv install --system --deploy
COPY config.default.cfg /etc/freitagsfoo-web.cfg

ENV CONFIG_FILE /etc/freitagsfoo-web.cfg
ENTRYPOINT ["/usr/local/bin/gunicorn","-w","2","-b","0.0.0.0:5000","--chdir", "/opt/app/src", "app:app"]
EXPOSE 5000/tcp
