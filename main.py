import argparse
import json
import time
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

def check_url(url: str, timeout: int = 10):
    start = time.time()
    req = Request(url, headers={"User-Agent": "healthwatch/1.0"})
    try:
        with urlopen(req, timeout=timeout) as r:
            latency_ms = round((time.time() - start) * 1000, 2)
            return {"url": url, "ok": True, "status": r.status, "latency_ms": latency_ms, "error": None}
    except HTTPError as e:
        latency_ms = round((time.time() - start) * 1000, 2)
        return {"url": url, "ok": False, "status": e.code, "latency_ms": latency_ms, "error": str(e)}
    except URLError as e:
        latency_ms = round((time.time() - start) * 1000, 2)
        return {"url": url, "ok": False, "status": None, "latency_ms": latency_ms, "error": str(e.reason)}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--url', action='append', required=True, help='URL to check (repeatable)')
    p.add_argument('--out', default='report.json', help='Output JSON file')
    args = p.parse_args()

    results = [check_url(u) for u in args.url]
    payload = {
        "checked_at": datetime.utcnow().isoformat() + "Z",
        "total": len(results),
        "ok": sum(1 for r in results if r["ok"]),
        "failed": sum(1 for r in results if not r["ok"]),
        "results": results,
    }

    for r in results:
        mark = "✅" if r["ok"] else "❌"
        print(f"{mark} {r['url']} | status={r['status']} | {r['latency_ms']}ms")

    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\nSaved report to {args.out}")

if __name__ == '__main__':
    main()
