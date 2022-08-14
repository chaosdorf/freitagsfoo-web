#!/bin/sh
export FLASK_APP=src/app.py
export FLASK_ENV=development
export CONFIG_FILE=$(pwd)/config.toml

exec flask run --with-threads
