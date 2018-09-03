from os import environ, path
from datetime import date
from flask import Flask, render_template, jsonify, request
from flask_bootstrap import Bootstrap
from raven.contrib.flask import Sentry
from dotenv import load_dotenv
from configparser import ConfigParser
import lib

WIKI_URL_FORMAT = "https://wiki.chaosdorf.de/Freitagsfoo/{}"

app = Flask(__name__)
app.config["BOOTSTRAP_SERVE_LOCAL"] = True
load_dotenv()
config = dict()
config_parser = ConfigParser()
config_parser.read(environ["CONFIG_FILE"])
for section in config_parser.sections():
    for option in config_parser[section]:
        config["_".join((section, option))] = config_parser[section][option]
app.config.update(config)
Bootstrap(app)

if app.env == "development":
    print("Not enabling Sentry in development.")
else:
    if path.exists("sentry-python-dsn"):
        file_name = "sentry-python-dsn"
    else:
        file_name = "/run/secrets/FFTALKS_SENTRY_PYTHON_DSN"
    with open(file_name) as f:
        sentry = Sentry(app, dsn=f.readline().strip())


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/host")
def host_initial():
    return render_template("host_initial.html")


@app.route("/host/check")
def host_check():
    return render_template("host_check.html")


@app.route("/host/check/info-beamer", methods=("GET", "POST"))
def host_check_infobeamer():
    if request.method == "GET":
        return jsonify(lib.infobeamer_check(app.config))
    elif request.method == "POST":
        return jsonify(lib.infobeamer_assign_background_setup(app.config))
    else:
        raise RuntimeError("should not be reached!")


@app.route("/host/review_talks")
def host_review_talks():
    return render_template(
        "host_review_talks.html",
        wiki_link=WIKI_URL_FORMAT.format(date.today())
    )


@app.route("/host/action")
def host_action():
    return render_template("host_action.html")


@app.route("/host/action/begin_talks", methods=("POST",))
def host_action_begin_talks():
    return jsonify(lib.talks_begin(app.config))


@app.route("/host/action/end_talks", methods=("POST",))
def host_action_end_talks():
    return jsonify(lib.talks_end(app.config))


@app.route("/host/final")
def host_final():
    return render_template("host_final.html")
