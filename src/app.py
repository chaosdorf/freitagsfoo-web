from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config["BOOTSTRAP_SERVE_LOCAL"] = True
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
