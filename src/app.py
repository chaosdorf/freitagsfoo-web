from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/host")
def host_initial():
    return render_template("host_initial.html")
