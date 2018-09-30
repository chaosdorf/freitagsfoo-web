# freitagsfoo-web

webapp for managing Freitagsfoo talks

# Development

To run the flask development server:

1. Copy `config.default.cfg` to `config.cfg` and fill in values.
2. Add `info-beamer-api-key` file and fill in value.
3. Add `sentry-dsn` file and fill in value.
4. run `docker-compose up --build` to start the flask development server.

# Deployment

Add service to `docker-compose.yml`, provide `freitagsfoo.cfg` config and secrets, e.g.:

```yml
version: '3.7'

services:
  app:
    image: chaosdorf/freitagsfoo-web:latest
    configs:
      - source: freitagsfoo.cfg
        target: /etc/freitagsfoo.cfg
    secrets:
      - INFO_BEAMER_API_KEY
      - FFTALKS_SENTRY_DSN

configs:
  freitagsfoo.cfg:
    [..]

secrets:
  INFO_BEAMER_API_KEY:
    [..]
  FFTALKS_SENTRY_DSN:
    [..]
```
