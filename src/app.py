from os import environ
from flask import Flask, render_template, jsonify
from flask_bootstrap import Bootstrap
from dotenv import load_dotenv
from configparser import ConfigParser
from lib import infobeamer_check

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


@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/host")
def host_initial():
    return render_template("host_initial.html")


@app.route("/host/check")
def host_check():
    return render_template("host_check.html")


@app.route("/host/check/info-beamer")
def host_check_infobeamer():
    return jsonify(infobeamer_check(app.config))
