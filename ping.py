#!/usr/bin/env python3
"""
CPC Ping Manager
-----------------
Pings each Supabase project's REST API so the project stays active and
doesn't get auto-paused by Supabase's free-tier inactivity timer.

Writes the result of each ping to status.json, which the status page
(index.html) reads and displays.

To add a project: add an entry to PROJECTS below, then add a matching
repository secret in GitHub (Settings > Secrets and variables > Actions)
holding that project's "anon" / "public" API key.
"""

import json
import os
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

PROJECTS = [
    {
        "name": "CPC Connect (+ Defect Tracker, Safety Violation Tracker, CPC Site Reports)",
        "ref": "ihwgejsioutzcmkaaumi",
        "secret_env": "CPC_CONNECT_ANON_KEY",
    },
    {
        "name": "Vehicle Movement Dashboard (pick-up schedule)",
        "ref": "lahrwbqnurklcsbkghic",
        "secret_env": "VEHICLE_DASHBOARD_ANON_KEY",
    },
]

STATUS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "status.json")
TIMEOUT_SECONDS = 15


def ping_project(project):
    ref = project["ref"]
    key = os.environ.get(project["secret_env"], "")
    url = f"https://{ref}.supabase.co/rest/v1/"

    result = {
        "name": project["name"],
        "ref": ref,
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ok": False,
        "http_status": None,
        "response_ms": None,
        "error": None,
    }

    if not key:
        result["error"] = f"Missing secret {project['secret_env']}"
        return result

    req = urllib.request.Request(
        url,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
        },
    )

    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            result["http_status"] = resp.status
            result["ok"] = 200 <= resp.status < 300
    except urllib.error.HTTPError as e:
        # Supabase returns 200s for a valid key; a 401/404 etc still means
        # we successfully reached the project (which is all "keep-alive"
        # needs), so treat any HTTP response as reachable, but only a 2xx
        # as fully "ok".
        result["http_status"] = e.code
        result["ok"] = 200 <= e.code < 300
        result["error"] = f"HTTP {e.code}"
    except Exception as e:  # noqa: BLE001 - want to record any failure
        result["error"] = str(e)
    finally:
        result["response_ms"] = round((time.monotonic() - start) * 1000)

    return result


def main():
    results = [ping_project(p) for p in PROJECTS]

    status = {
        "last_run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "projects": results,
    }

    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)
        f.write("\n")

    for r in results:
        print(f"{r['name']}: {'OK' if r['ok'] else 'FAILED'} "
              f"(http={r['http_status']}, {r['response_ms']}ms) {r['error'] or ''}")


if __name__ == "__main__":
    main()
