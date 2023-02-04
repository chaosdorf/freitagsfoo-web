import json
import mimetypes
from os import environ
from datetime import date
from flask import Flask, render_template, jsonify, request
from flask.wrappers import Response
from dealer.contrib.flask import Dealer
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask_apscheduler import APScheduler
from flask_redis import FlaskRedis
from flask_sse import sse
from dotenv import load_dotenv
import toml
import lib.base
import lib.talks
import lib.info_beamer
import lib.extron
import lib.state

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
app.register_blueprint(sse, url_prefix="/stream")

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
    with app.app_context():
        lib.talks.fetch(redis_client, sse)


@scheduler.task("interval", id="extron_fetch", seconds=15)
def extron_fetch():
    with app.app_context():
        lib.extron.fetch_state(config, redis_client, sse)


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
    with app.app_context():
        if request.method == "GET":
            return jsonify(lib.info_beamer.infobeamer_check(
                app.config, redis_client,
            ))
        elif request.method == "POST":
            return jsonify(lib.info_beamer.infobeamer_assign_correct_setup(
                app.config, redis_client,
            ))
        elif request.method == "PATCH":
            return jsonify(lib.info_beamer.end_talks(app.config, redis_client, sse))
        elif request.method == "PUT":
            return jsonify(lib.extron.switch_to_pi(app.config, redis_client, sse))
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
    return jsonify(lib.state.compute_state(redis_client))

# @app.route("/state/stream", methods=("GET",))
# def stream_state():
#     def stream_func():

#         yield "data: " + json.dumps(state)
#     return Response(stream_func(), mimetype="text/event-stream")

@app.route("/host/action/begin_talks/info_beamer", methods=("POST",))
def host_action_begin_talks():
    with app.app_context():
        return jsonify(lib.info_beamer.begin_talks(app.config, redis_client, sse))


@app.route("/host/action/announce_talk/info_beamer", methods=("POST",))
def host_announce_talk():
    with app.app_context():
        return jsonify(lib.info_beamer.announce_talk(
            app.config, redis_client, sse, int(request.form["index"])
        ))


@app.route("/host/action/list_talks/info_beamer", methods=("POST",))
def host_list_talks():
    return jsonify(lib.talks.list(redis_client))


@app.route("/host/action/begin_talk", methods=("POST",))
def host_begin_talk():
    with app.app_context():
        switch_to = json.loads(request.form["input"])
        if switch_to:
            extron_result = lib.extron.switch_to_input(
                app.config, redis_client, sse, switch_to,
            )
            if extron_result["status"] == "err":
                return jsonify(extron_result)
        # ymmv: do we want to explicitly switch to the info-beamer in the other case?
        talks_result = lib.talks.begin_talk(redis_client, sse, int(request.form["talk"]))
        return jsonify(talks_result)


@app.route("/host/action/end_talk", methods=("POST",))
def host_end_talk():
    with app.app_context():
        extron_result = lib.extron.switch_to_pi(
            app.config, redis_client, sse,
        )
        if extron_result["status"] == "err":
            return jsonify(extron_result)
        talks_result = lib.talks.end_talk(redis_client, sse)
        return jsonify(talks_result)


@app.route("/host/action/end_talks/info_beamer", methods=("POST",))
def host_action_end_talks():
    with app.app_context():
        return jsonify(lib.info_beamer.end_talks(app.config, redis_client, sse))


@app.route("/host/final")
def host_final():
    return render_template("host_final.html.j2")


scheduler.start()
