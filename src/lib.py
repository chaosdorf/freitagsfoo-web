from os import environ
from requests import Session
from requests.exceptions import ConnectionError, HTTPError

INFO_BEAMER_API = "https://info-beamer.com/api/v1/"
session = Session()
session.auth = ("", environ["INFO_BEAMER_API_KEY"])


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


def infobeamer_check(config):
    # Get all available devices.
    try:
        r = session.get(INFO_BEAMER_API + "device/list")
        r.raise_for_status()
        data = r.json()
    except (ConnectionError, HTTPError, ValueError):
        return result("error", last_step="info-beamer.com")
    # Find the right device.
    for dev in data["devices"]:
        if dev["uuid"] == config["info-beamer_pi_uuid"]:
            device = dev
            break
    else:
        return result(
            "error",
            data={
                "id": int(config["info-beamer_pi_id"]),
                "uuid": config["info-beamer_pi_uuid"],
            },
            last_step="find-device"
        )
    # Check if the right setup is running.
    if device["setup"]["id"] != int(config["info-beamer_background_setup_id"]):
        return result(
            "error",
            data={
                "device": device,
                "actual": device["setup"],
                "expected": {
                    "id": int(config["info-beamer_background_setup_id"]),
                    "name": config["info-beamer_background_setup_name"],
                },
            },
            last_step="setup"
        )
    # Check if the device is online and synced.
    if not device["is_online"]:
        return result("error", data=device, last_step="check-device-online")
    if not device["is_synced"]:
        return result("error", data=device, last_step="check-device-synced")
    return result("ok", data=device)


def infobeamer_assign_background_setup(config):
    return _infobeamer_assign_setup(
        int(config["info-beamer_pi_id"]),
        int(config["info-beamer_background_setup_id"])
    )


def _infobeamer_assign_setup(pi_id, setup_id):
    try:
        r = session.post(
            INFO_BEAMER_API + "device/" + str(pi_id),
            data={"setup_id": setup_id},
        )
    except ConnectionError:
        return result("error", last_step="info-beamer.com")
    if not r.ok:
        return result("error", last_step="assign-setup")
    try:
        data = r.json()
    except ValueError:
        return result("error", last_step="info-beamer.com")
    if not data.get("ok"):
        return result("error", last_step="assign-setup")
    return result("ok")


def talks_begin(config):
    return _infobeamer_assign_setup(
        int(config["info-beamer_pi_id"]),
        int(config["info-beamer_talks_setup_id"])
    )


def talks_end(config):
    return _infobeamer_assign_setup(
        int(config["info-beamer_pi_id"]),
        int(config["info-beamer_background_setup_id"])
    )
