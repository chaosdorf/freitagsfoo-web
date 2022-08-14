from .base import result

def compute_state(redis_client):
    from . import info_beamer, talks, extron
    ib = info_beamer.get_state(redis_client)
    t = talks.list(redis_client)
    e = extron.get_state(redis_client)
    if ib["status"] == "ok" and t["status"] == "ok" and e["status"] == "ok":
        return result("ok", data={
            "info-beamer": ib.get("data"),
            "talks": t.get("data"),
            "extron": e.get("data"),
        })
    return result("error", reason="fetch")


def push_state(redis_client, sse):
    sse.publish(compute_state(redis_client))
