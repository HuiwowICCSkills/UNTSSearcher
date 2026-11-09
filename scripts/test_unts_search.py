"""Offline tests for UNTSSearcher."""
from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import unts_adapter as adapter  # noqa: E402


def meta(url):
    return {"source_url": url, "http_status": 200, "content_type": "text/html",
            "bytes": 100, "retrieved_at": "2026-11-09T00:00:00Z", "sha256": "0" * 64}


class FakeHttp:
    def __init__(self):
        self.evidence = []

    def soup(self, url, params=None, headers=None):
        if "ParticipationStatus" in url:
            html = '<html><body><a href="Treaties.aspx?id=1">Chapter I</a></body></html>'
        else:
            html = ('<html><body><a href="ViewDetails.aspx?src=TREATY&mtdsg_no=I-1">'
                    'Charter of the United Nations</a></body></html>')
        return BeautifulSoup(html, "html.parser"), meta(url)


def args(**kwargs):
    base = dict(limit=1, offset=0, max_pages=2, cache=".cache", offline=False, cache_ttl=0, timeout=30)
    base.update(kwargs)
    return argparse.Namespace(**base)


class UntsTests(unittest.TestCase):
    def test_search_reads_title_catalogue(self):
        out = adapter.search("Charter", args(), FakeHttp())
        self.assertEqual(out["status"], "ok")
        self.assertEqual(out["total"], 1)
        self.assertEqual(out["results"][0]["result_type"], "retrieved_metadata")
        self.assertIn("Charter", out["results"][0]["title"])


if __name__ == "__main__":
    unittest.main()
