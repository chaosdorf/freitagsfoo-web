import json
from os import environ
from datetime import date
from flask import Flask, render_template, jsonify, request
from dealer.contrib.flask import Dealer
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask_apscheduler import APScheduler
from flask_redis import FlaskRedis
from dotenv import load_dotenv
import toml
import lib.base
import lib.talks
import lib.info_beamer
import lib.extron

app = Flask(__name__)
load_dotenv()
config = dict()
config_file = toml.load(environ["CONFIG_FILE"])
for section in config_file.keys():
    for option in config_file[section]:
        config["_".join((section, option))] = config_file[section][option]
app.config.update(config)
scheduler = APScheduler(app=app)
Dealer(app)
redis_client = FlaskRedis(app)

if app.env == "development":
    print("Not enabling Sentry in development.")
    sentry = None
else:
    sentry = sentry_sdk.init(
        dsn=lib.base.read_secret("FFTALKS_SENTRY_DSN"),
        integrations=[FlaskIntegration()],
        release=app.revision,
    )


@app.context_processor
def inject_js_sentry_dsn():
    return {
        "sentry_dsn": sentry_sdk.Hub.current.client.dsn if sentry else None
    }


@app.errorhandler(404)
def error_404(error):
    return render_template("error_404.html.j2"), 404


@app.errorhandler(500)
def error_500(error):
    return render_template("error_500.html.j2"), 500


@scheduler.task("interval", id="talks_fetch", seconds=60)
def talks_fetch():
    lib.talks.fetch(redis_client)


@scheduler.task("interval", id="extron_fetch", seconds=15)
def extron_fetch():
    lib.extron.fetch_state(config, redis_client)


@app.route("/")
def hello():
    return render_template("index.html.j2")


@app.route("/host")
@app.route("/host/")
def host_initial():
    return render_template("host_initial.html.j2")


@app.route("/host/check")
def host_check():
    return render_template("host_check.html.j2")


@app.route("/host/check/info-beamer", methods=("GET", "POST", "PATCH", "PUT"))
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
    elif request.method == "PUT":
        return jsonify(lib.extron.switch_to_pi(app.config, redis_client))
    else:
        raise RuntimeError("should not be reached!")


@app.route("/host/action")
def host_action():
    return render_template(
        "host_action.html.j2",
        wiki_link=lib.talks.WIKI_URL_FORMAT.format(date.today()),
    )


@app.route("/state", methods=("GET",))
def host_action_get_state():
    ib = lib.info_beamer.get_state(redis_client)
    t = lib.talks.list(redis_client)
    e = lib.extron.get_state(redis_client)
    if ib["status"] == "ok" and t["status"] == "ok" and e["status"] == "ok":
        return jsonify(lib.base.result("ok", data={
            "info-beamer": ib.get("data"),
            "talks": t.get("data"),
            "extron": e.get("data"),
        }))
    return jsonify(lib.base.result("error", reason="fetch"))


@app.route("/host/action/begin_talks/info_beamer", methods=("POST",))
def host_action_begin_talks():
    return jsonify(lib.info_beamer.begin_talks(app.config, redis_client))


@app.route("/host/action/announce_talk/info_beamer", methods=("POST",))
def host_announce_talk():
    return jsonify(lib.info_beamer.announce_talk(
        app.config, redis_client, int(request.form["index"])
    ))


@app.route("/host/action/list_talks/info_beamer", methods=("POST",))
def host_list_talks():
    return jsonify(lib.talks.list(redis_client))


@app.route("/host/action/begin_talk", methods=("POST",))
def host_begin_talk():
    return jsonify(lib.extron.switch_to_input(
        app.config, redis_client, int(request.form["input"])
    ))


@app.route("/host/action/end_talk", methods=("POST",))
def host_end_talk():
    return jsonify(lib.extron.switch_to_pi(
        app.config, redis_client
    ))


@app.route("/host/action/end_talks/info_beamer", methods=("POST",))
def host_action_end_talks():
    return jsonify(lib.info_beamer.end_talks(app.config, redis_client))


@app.route("/host/final")
def host_final():
    return render_template("host_final.html.j2")


scheduler.start()
