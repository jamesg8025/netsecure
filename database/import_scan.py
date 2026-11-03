import argparse
import ipaddress
import re
import sqlite3
from pathlib import Path

def parse_report(text):
    """Read compact scanner text. A trailing numeric token is a version."""
    hosts = []
    host = None
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        match = re.fullmatch(r"(\d+)/(tcp|udp)\s+(\S+)(?:\s+—\s+(.+))?", line)
        if match:
            if host is None:
                raise ValueError(f"Line {number}: service precedes device")
            port = int(match[1])
            if not 0 <= port <= 65535:
                raise ValueError(f"Line {number}: invalid port")
            product = match[4]
            version = None
            if product:
                product = product.strip()
                parts = product.rsplit(None, 1)
                if len(parts) == 2 and re.fullmatch(r"[0-9][A-Za-z0-9._+~:-]*", parts[1]):
                    product, version = parts
            host["services"].append({
                "port": port, "protocol": match[2], "name": match[3],
                "product": product, "version": version})
            continue
        match = re.fullmatch(r"(\S+)(?:\s+\(([^()]*)\))?", line)
        if not match:
            raise ValueError(f"Line {number}: unrecognized text")
        try:
            ip = str(ipaddress.ip_address(match[1]))
        except ValueError:
            raise ValueError(f"Line {number}: invalid IP address") from None
        host = {"ip": ip, "hostname": (match[2] or "").strip() or None, "services": []}
        hosts.append(host)
    if not hosts:
        raise ValueError("Empty report: backend must handle verified zero-device scans separately")
    return hosts

def import_report(db, scan_id, text, finished_at):
    from datetime import datetime
    stamp = datetime.strptime(finished_at, "%Y-%m-%d %H:%M:%S")
    if stamp.strftime("%Y-%m-%d %H:%M:%S") != finished_at:
        raise ValueError("Use UTC YYYY-MM-DD HH:MM:SS")
    hosts = parse_report(text)
    if db.in_transaction:
        raise ValueError("Use a connection with no active transaction")
    db.execute("PRAGMA foreign_keys = ON")
    with db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT status FROM scans WHERE scan_id=?", (scan_id,)).fetchone()
        if row is None or row[0] != "running":
            raise ValueError("Import requires an existing running scan")
        if db.execute("SELECT 1 FROM hosts WHERE scan_id=?", (scan_id,)).fetchone():
            raise ValueError("Scan already has results")
        for host in hosts:
            host_id = db.execute(
                "INSERT INTO hosts(scan_id,ip_address,hostname) VALUES(?,?,?)",
                (scan_id, host["ip"], host["hostname"])).lastrowid
            for service in host["services"]:
                db.execute(
                    """INSERT INTO services(host_id,port,protocol,service_name,product,version)
                       VALUES(?,?,?,?,?,?)""",
                    (host_id, service["port"], service["protocol"], service["name"],
                     service["product"], service["version"]))
        db.execute("UPDATE scans SET status='completed', finished_at=? WHERE scan_id=?",
                   (finished_at, scan_id))
    return len(hosts), sum(len(h["services"]) for h in hosts)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report")
    parser.add_argument("--db", default=str(Path(__file__).with_name("netsecure.db")))
    parser.add_argument("--scan-id", required=True, type=int)
    parser.add_argument("--finished-at", required=True, help="Actual scan end, UTC YYYY-MM-DD HH:MM:SS")
    args = parser.parse_args()
    from datetime import datetime
    datetime.strptime(args.finished_at, "%Y-%m-%d %H:%M:%S")
    path = Path(args.db).resolve()
    db = sqlite3.connect(path.as_uri() + "?mode=rw", uri=True)
    try:
        print("Imported hosts and services:", import_report(
            db, args.scan_id, Path(args.report).read_text(encoding="utf-8-sig"), args.finished_at))
    finally:
        db.close()
