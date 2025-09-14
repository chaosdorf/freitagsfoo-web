#!/bin/sh
export FLASK_APP=src/app.py
export CONFIG_FILE=$(pwd)/config.toml

exec flask --debug run --with-threads $@
