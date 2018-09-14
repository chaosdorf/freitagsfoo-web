FROM alpine as Builder

RUN apk add --no-cache make npm
RUN npm install handlebars -g
WORKDIR /opt/app
COPY src/ /opt/app/
RUN mkdir -p /opt/app/static/templates \
    && cd /opt/app/client_templates \
    && make


FROM python:3.7-alpine

RUN pip install --no-cache-dir pipenv
WORKDIR /opt/app
COPY ./Pipfile .
COPY ./Pipfile.lock .
RUN pipenv install --system --deploy
COPY --from=Builder /opt/app .
COPY config.default.cfg /etc/freitagsfoo-web.cfg

ENV CONFIG_FILE /etc/freitagsfoo-web.cfg
ENTRYPOINT ["/usr/local/bin/gunicorn","-w","2","-b","0.0.0.0:5000","app:app"]
EXPOSE 5000/tcp
