#!/usr/bin/env python3
"""UN Treaty Collection / MTDSG title-catalogue adapter for UNTSSearcher."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from skillkit import HTTP, RetrievalError, clean, pdf_pages, result

PROG = "unts_search.py"
DESCRIPTION = "Search the UN Treaty Collection MTDSG title catalogue."
CACHE_DEFAULT = ".unts-cache"
FETCH_TIMEOUT_DEFAULT = 300

ROOT_URL = "https://treaties.un.org/Pages/ParticipationStatus.aspx?clang=_en"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/155.0.0.0 Safari/537.36"
)


def _headers() -> dict[str, str]:
    return {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }


def make_http(args: argparse.Namespace) -> HTTP:
    return HTTP(
        args.cache,
        offline=args.offline,
        ttl=args.cache_ttl,
        timeout=args.timeout,
        user_agent=UA,
    )


def add_search_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--limit", type=int, default=10, help="1..50 (default 10)")
    parser.add_argument("--offset", type=int, default=0, help=">= 0 (default 0)")
    parser.add_argument("--max-pages", type=int, default=20, help="Catalogue pages to scan (1..2000)")


def add_fetch_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--text-out", help="Write extracted page text here")
    parser.add_argument("--pdf-out", help="Write a PDF response here")
    parser.add_argument("--max-mb", type=int, default=250, help="Maximum response size in MiB")


def search(query: str, args: argparse.Namespace, http: HTTP) -> dict[str, Any]:
    if not query.strip():
        raise ValueError("A non-empty query is required")
    if not 1 <= args.limit <= 50:
        raise ValueError("limit must be 1..50")
    if args.offset < 0:
        raise ValueError("offset must be >= 0")
    if not 1 <= args.max_pages <= 2000:
        raise ValueError("max-pages must be 1..2000")

    root, root_meta = http.soup(ROOT_URL, headers=_headers())
    pages = list(
        dict.fromkeys(
            urljoin(root_meta["source_url"], anchor["href"])
            for anchor in root.select("a[href]")
            if re.search(r"Treaties\.aspx\?", anchor["href"], re.I)
        )
    )
    if not pages:
        raise RetrievalError("UNTC ParticipationStatus page has no Treaties.aspx links")
    discovered = len(pages)
    pages = pages[: args.max_pages]
    matches: list[dict[str, Any]] = []
    errors: list[str] = []
    for page_url in pages:
        try:
            soup, meta = http.soup(page_url, headers=_headers())
        except RetrievalError as exc:
            errors.append(str(exc))
            continue
        valid = 0
        for anchor in soup.select("a[href]"):
            target = urljoin(meta["source_url"], anchor["href"])
            path = urlparse(target).path
            if "viewdetails" not in path.lower():
                continue
            valid += 1
            title = clean(anchor.get_text(" ", strip=True))
            if not title or not all(term in title.casefold() for term in query.casefold().split()):
                continue
            matches.append(
                result(
                    title,
                    target,
                    "unts-title-catalogue",
                    provider="UNTC MTDSG title catalogue",
                    content_scope="catalogue title match; treaty detail page not yet fetched",
                    discovered_on=meta["source_url"],
                )
            )
        if not valid:
            errors.append("No viewdetails links found: " + page_url)

    matches = list({row["url"]: row for row in matches}.values())
    selected = matches[args.offset : args.offset + args.limit]
    return {
        "status": "partial" if errors else "ok",
        "query": query,
        "total": len(matches),
        "results": selected,
        "pagination": {
            "offset": args.offset,
            "limit": args.limit,
            "next_offset": args.offset + len(selected) if args.offset + len(selected) < len(matches) else None,
            "catalogues_discovered": discovered,
            "catalogues_requested": len(pages),
        },
        "warnings": errors,
        "scope": (
            "UNTC Secretary-General depositary (MTDSG) title catalogue; "
            "a subset and alternative to the full UNTS registration search"
        ),
        "evidence": http.evidence,
    }


def fetch(locator: str, args: argparse.Namespace, http: HTTP) -> dict[str, Any]:
    parsed = urlparse(locator)
    if parsed.scheme != "https" or (parsed.hostname or "").lower() not in {
        "treaties.un.org",
        "www.treaties.un.org",
    }:
        raise ValueError("fetch expects an https://treaties.un.org/ URL")
    max_bytes = args.max_mb * 1024 * 1024
    body, meta = http.get(locator, headers=_headers())
    if len(body) > max_bytes:
        raise RetrievalError(f"Response exceeds --max-mb ({args.max_mb} MiB)")
    if body.startswith(b"%PDF"):
        pages = pdf_pages(body)
        text = "\n\n".join(f"@@PAGE {p['page']}@@\n{p['text']}" for p in pages)
        if args.pdf_out:
            Path(args.pdf_out).write_bytes(body)
        if args.text_out:
            Path(args.text_out).write_text(text, encoding="utf-8")
        return {
            "status": "ok",
            "url": meta["source_url"],
            "pages": len(pages),
            "needs_ocr": not any(p["text"].strip() for p in pages),
            "page_text": pages,
            "pdf_out": str(Path(args.pdf_out).resolve()) if args.pdf_out else None,
            "text_out": str(Path(args.text_out).resolve()) if args.text_out else None,
            "sha256": meta["sha256"],
            "retrieved_at": meta["retrieved_at"],
        }
    soup = BeautifulSoup(body, "html.parser")
    container = soup.select_one("main") or soup.select_one("#content") or soup.body or soup
    for node in container.select("script, style, nav, header, footer, input, select, button, textarea, noscript"):
        node.decompose()
    text = container.get_text("\n", strip=True)
    if len(text) < 100:
        raise RetrievalError("Insufficient UNTC page text")
    links = []
    seen = set()
    for anchor in container.select("a[href]"):
        href = urljoin(meta["source_url"], anchor["href"])
        if href in seen:
            continue
        seen.add(href)
        links.append({"text": clean(anchor.get_text(" ", strip=True)), "url": href})
    if args.text_out:
        Path(args.text_out).write_text(text, encoding="utf-8")
    return {
        "status": "ok",
        "url": meta["source_url"],
        "title": clean(soup.title.get_text(" ", strip=True)) if soup.title else "",
        "text": text,
        "text_characters": len(text),
        "document_links": links,
        "content_scope": "UNTC treaty detail/status page text; linked PDFs must be fetched separately",
        "text_out": str(Path(args.text_out).resolve()) if args.text_out else None,
        "sha256": meta["sha256"],
        "retrieved_at": meta["retrieved_at"],
    }


def doctor(args: argparse.Namespace) -> dict[str, Any]:
    checks = [
        {"check": "python", "ok": True, "detail": "Python runtime available"},
        {"check": "requests", "ok": True, "detail": "requests importable"},
        {"check": "beautifulsoup4", "ok": True, "detail": "bs4 importable"},
    ]
    if args.no_probe:
        return {"ok": True, "status": "ok (probes skipped)", "checks": checks}
    http = make_http(args)
    try:
        soup, meta = http.soup(ROOT_URL, headers=_headers())
        links = [a for a in soup.select("a[href]") if re.search(r"Treaties\.aspx\?", a["href"], re.I)]
        checks.append(
            {
                "check": "UNTC ParticipationStatus",
                "ok": bool(links),
                "catalogue_links": len(links),
                "http_status": meta["http_status"],
                "bytes": meta["bytes"],
            }
        )
        ok = bool(links)
    except Exception as exc:
        checks.append({"check": "UNTC ParticipationStatus", "ok": False, "error": f"{type(exc).__name__}: {exc}"})
        ok = False
    return {"ok": ok, "status": "ok" if ok else "error", "checks": checks, "catalog": {"root": ROOT_URL}}
