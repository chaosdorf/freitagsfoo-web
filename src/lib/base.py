from os import path, environ

def read_secret(name):
    lower = name.lower().replace("_", "-").replace("fftalks-", "", 1)
    if path.exists(lower):
        file_name = lower
    elif environ.get(name):
        print(f"WARN: Reading {name} from the environment; consider using secrets instead.")
        return environ[name]
    else:
        file_name = "/run/secrets/" + name
    with open(file_name, "r") as f:
        return f.readline().strip()


def result(status, *, data=None, reason=None, last_step=None):
    res = dict()
    assert status in ("ok", "error")
    res["status"] = status
    if data:
        res["data"] = data
    if reason:
        assert status == "error"
        res["reason"] = reason
    if last_step:
        assert status == "error"
        res["last_step"] = last_step
    return res


from .info_beamer import _infobeamer_send_command


def talks_begin(config):
    return _infobeamer_send_command(
        int(config["INFO-BEAMER_pi-id"]),
        "freitagsfoo/screen",
        "title",
    )


def talks_end(config):
    return _infobeamer_send_command(
        int(config["INFO-BEAMER_pi-id"]),
        "freitagsfoo/screen",
        "initial"
    )


def post_error(config, raven, data):
    print("error posted:", data)
    # figure out if this is a Python exception or a message from the Lua part
    if "source" not in data.keys():
        return result("error", reason="source is missing")
    if data["source"] == "python":
        # TODO: use strings, just pass the name
        # and possibly the traceback in string representation?
        if not ("exc_info" in data.keys() and "hostname" in data.keys()):
            return result("error", reason="exc_info or hostname missing")
        if raven is not None:
            raven.captureException(
                exc_info=data["exc_info"],
                server_name=data["hostname"],
            )
        return result("ok")
    elif data["source"] == "lua":
        pass  # TODO
    else:
        return result("error", reason="invalid source")
