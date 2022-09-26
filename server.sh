#!/bin/sh
export FLASK_APP=src/app.py
export FLASK_DEBUG=1
export CONFIG_FILE=$(pwd)/config.toml

exec flask run --with-threads
