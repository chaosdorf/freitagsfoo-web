from os import environ
from requests import Session

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
    r = session.get(INFO_BEAMER_API + "device/list")
    if not r.ok:
        return result("error", last_step="info-beamer.com")
    # Find the right device.
    for dev in r.json()["devices"]:
        if dev["uuid"] == config["info-beamer_pi_uuid"]:
            device = dev
            break
    else:
        return result("error", last_step="find-device")
    # Check if the device is online and synced.
    if not device["is_online"]:
        return result("error", last_step="check-device-online")
    if not device["is_synced"]:
        return result("error", last_step="check-device-synced")
    # Check if the right setup is running.
    if device["setup"]["id"] != int(config["info-beamer_background_setup_id"]):
        return result("error", data=device["setup"], last_step="setup")
    return result("ok", data=device)
