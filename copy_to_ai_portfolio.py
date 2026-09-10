"""Phase 4 of the Supabase split: copy reports / portfolio / valuations
from the valerius project to the ai-portfolio project.

Reads, never writes, the source. Refuses to run unless the destination tables
are empty, so re-running it cannot duplicate rows.

    python copy_to_ai_portfolio.py --dry-run   # counts only, no writes
    python copy_to_ai_portfolio.py             # copy

Credentials come from files, never from arguments:
  source      ../sp500-database-webapp/.env   SUPABASE_URL / SUPABASE_SERVICE_KEY
  destination ./.env.aiportfolio              AIP_SUPABASE_URL / AIP_SERVICE_KEY
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

TABLES = ("reports", "portfolio", "valuations")
HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_ENV = os.path.join(HERE, "..", "sp500-database-webapp", ".env")
DEST_ENV = os.path.join(HERE, ".env.aiportfolio")


def read_env(path):
    if not os.path.exists(path):
        sys.exit("missing env file: %s" % os.path.normpath(path))
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def need(env, key, path):
    value = env.get(key)
    if not value:
        sys.exit("%s is not set in %s" % (key, os.path.normpath(path)))
    return value


def ref(url):
    """Project ref from a Supabase URL - safe to print, it is in every URL."""
    return url.split("//", 1)[-1].split(".", 1)[0]


def call(url, key, path, method="GET", body=None, headers=None):
    request = urllib.request.Request(
        url.rstrip("/") + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "apikey": key,
            "Authorization": "Bearer %s" % key,
            "Content-Type": "application/json",
            **(headers or {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = response.read().decode()
            return response.headers, json.loads(payload) if payload else None
    except urllib.error.HTTPError as exc:
        sys.exit("%s %s -> %s %s" % (method, path.split("?")[0], exc.code,
                                     exc.read().decode()[:400]))


def count(url, key, table):
    headers, _ = call(url, key, "/rest/v1/%s?select=id" % table,
                      headers={"Prefer": "count=exact", "Range": "0-0"})
    return int(headers["Content-Range"].split("/")[-1])


def fetch(url, key, table):
    _, rows = call(url, key, "/rest/v1/%s?select=*&order=id.asc" % table)
    return rows or []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    src = read_env(SOURCE_ENV)
    dst = read_env(DEST_ENV)
    src_url = need(src, "SUPABASE_URL", SOURCE_ENV)
    src_key = need(src, "SUPABASE_SERVICE_KEY", SOURCE_ENV)
    dst_url = need(dst, "AIP_SUPABASE_URL", DEST_ENV)
    dst_key = need(dst, "AIP_SERVICE_KEY", DEST_ENV)

    if ref(src_url) == ref(dst_url):
        sys.exit("source and destination are the SAME project (%s) - aborting"
                 % ref(src_url))
    print("source      %s" % ref(src_url))
    print("destination %s\n" % ref(dst_url))

    plan = []
    for table in TABLES:
        before_src = count(src_url, src_key, table)
        before_dst = count(dst_url, dst_key, table)
        print("%-11s source %4d   destination %4d" % (table, before_src, before_dst))
        if before_dst and not args.dry_run:
            sys.exit("\n%s already holds %d rows in the destination. "
                     "Refusing to copy - it would duplicate them." % (table, before_dst))
        plan.append((table, before_src))

    if args.dry_run:
        print("\ndry run - nothing written")
        return

    print()
    for table, expected in plan:
        rows = fetch(src_url, src_key, table)
        for row in rows:
            row.pop("id", None)          # let the destination identity assign
        if rows:
            call(dst_url, dst_key, "/rest/v1/%s" % table, method="POST", body=rows,
                 headers={"Prefer": "return=minimal"})
        after = count(dst_url, dst_key, table)
        still = count(src_url, src_key, table)
        ok = "OK " if after == expected and still == expected else "MISMATCH"
        print("%s %-11s copied %3d   destination now %3d   source still %3d"
              % (ok, table, len(rows), after, still))
        if ok != "OK ":
            sys.exit("row counts do not match - stopping before the next table")

    print("\nall three tables copied and verified. Source untouched.")


if __name__ == "__main__":
    main()
