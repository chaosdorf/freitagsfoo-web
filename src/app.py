from os import environ
from datetime import date
from flask import Flask, render_template, jsonify, request
from dealer.contrib.flask import Dealer
from raven.contrib.flask import Sentry
from flask_redis import FlaskRedis
from dotenv import load_dotenv
import toml
import lib.base
import lib.talks
import lib.info_beamer

app = Flask(__name__)
load_dotenv()
config = dict()
config_file = toml.load(environ["CONFIG_FILE"])
for section in config_file.keys():
    for option in config_file[section]:
        config["_".join((section, option))] = config_file[section][option]
app.config.update(config)
Dealer(app)
redis_client = FlaskRedis(app)

if app.env == "development":
    print("Not enabling Sentry in development.")
    sentry = None
else:
    sentry_cfg = app.config.get("SENTRY_CONFIG", dict())
    sentry_cfg["release"] = app.revision
    app.config["SENTRY_CONFIG"] = sentry_cfg
    del sentry_cfg
    sentry = Sentry(app, dsn=lib.base.read_secret("FFTALKS_SENTRY_DSN"))


@app.context_processor
def inject_js_sentry_dsn():
    return {
        "sentry_dsn": sentry.client.get_public_dsn() if sentry else None
    }


@app.errorhandler(404)
def error_404(error):
    return render_template("error_404.html.j2"), 404


@app.errorhandler(500)
def error_500(error):
    return render_template("error_500.html.j2"), 500


@app.route("/")
def hello():
    return render_template("index.html.j2")


@app.route("/talks/list")
def list_talks():
    return jsonify(lib.talks.table(date.today()))


@app.route("/host")
@app.route("/host/")
def host_initial():
    return render_template("host_initial.html.j2")


@app.route("/host/check")
def host_check():
    return render_template("host_check.html.j2")


@app.route("/host/check/info-beamer", methods=("GET", "POST", "PATCH"))
def host_check_infobeamer():
    if request.method == "GET":
        return jsonify(lib.info_beamer.infobeamer_check(
            app.config, redis_client,
        ))
    elif request.method == "POST":
        return jsonify(lib.info_beamer.infobeamer_assign_correct_setup(
            app.config, redis_client,
        ))
    elif request.method == "PATCH":
        return jsonify(lib.info_beamer.end_talks(app.config, redis_client))
    else:
        raise RuntimeError("should not be reached!")


@app.route("/host/action")
def host_action():
    return render_template(
        "host_action.html.j2",
        wiki_link=lib.talks.WIKI_URL_FORMAT.format(date.today()),
    )


@app.route("/host/action/info_beamer/state", methods=("GET",))
def host_action_info_beamer_state():
    return jsonify(lib.info_beamer.get_state(redis_client))


@app.route("/host/action/begin_talks/info_beamer", methods=("POST",))
def host_action_begin_talks():
    return jsonify(lib.info_beamer.begin_talks(app.config, redis_client))


@app.route("/host/action/announce_talk/info_beamer", methods=("POST",))
def host_announce_talk():
    return jsonify(lib.base.announce_talk(
        app.config, redis_client, int(request.form["index"])
    ))


@app.route("/host/action/list_talks/info_beamer", methods=("POST",))
def host_list_talks():
    return jsonify(lib.base.list_talks(app.config, redis_client))


@app.route("/host/action/end_talks/info_beamer", methods=("POST",))
def host_action_end_talks():
    return jsonify(lib.info_beamer.end_talks(app.config, redis_client))


@app.route("/host/final")
def host_final():
    return render_template("host_final.html.j2")
