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
