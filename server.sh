#!/bin/sh

export FLASK_APP=src/app.py
export FLASK_ENV=development
exec flask run
