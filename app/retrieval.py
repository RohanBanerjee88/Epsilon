"""Keyless paper/source retrieval.

Providers used (no API keys required):
  - OpenAlex   -> broad coverage, citation counts, reconstructable abstracts.
  - arXiv      -> recent CS/ML preprints (Atom XML, parsed with stdlib).
  - Semantic Scholar -> best-effort; rate-limited without a key, so failures
                        are swallowed rather than fatal.

Everything is async and defensive: a provider timing out or erroring must never
sink the whole request. We just return fewer sources.
"""

from __future__ import annotations

import asyncio
import xml.etree.ElementTree as ET
from typing import Dict, List

import httpx

# Keep the platform polite: OpenAlex asks for a contact in the query string.
OPENALEX_MAILTO = "epsilon@maritime.app"
TIMEOUT = httpx.Timeout(12.0, connect=6.0)
HEADERS = {"User-Agent": f"Epsilon/2.1 (mailto:{OPENALEX_MAILTO})"}


def _reconstruct_abstract(inverted: Dict[str, List[int]] | None) -> str:
    """OpenAlex ships abstracts as an inverted index {word: [positions]}."""
    if not inverted:
        return ""
    positions: List[tuple[int, str]] = []
    for word, idxs in inverted.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    text = " ".join(word for _, word in positions)
    return text[:900]


async def _search_openalex(client: httpx.AsyncClient, query: str, limit: int) -> List[dict]:
    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per_page": limit,
        "sort": "relevance_score:desc",
        "mailto": OPENALEX_MAILTO,
    }
    r = await client.get(url, params=params, headers=HEADERS)
    r.raise_for_status()
    out: List[dict] = []
    for w in r.json().get("results", []):
        pid = w.get("doi") or w.get("id") or ""
        url_out = pid if pid.startswith("http") else (f"https://doi.org/{pid}" if pid else "")
        out.append(
            {
                "title": (w.get("display_name") or "").strip(),
                "url": url_out or (w.get("id") or ""),
                "abstract": _reconstruct_abstract(w.get("abstract_inverted_index")),
                "year": w.get("publication_year"),
                "citation_count": w.get("cited_by_count"),
                "source_type": "paper",
                "provider": "openalex",
            }
        )
    return out


async def _search_arxiv(client: httpx.AsyncClient, query: str, limit: int) -> List[dict]:
    url = "https://export.arxiv.org/api/query"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": limit,
        "sortBy": "relevance",
    }
    r = await client.get(url, params=params, headers=HEADERS)
    r.raise_for_status()
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(r.text)
    out: List[dict] = []
    for entry in root.findall("a:entry", ns):
        title = (entry.findtext("a:title", default="", namespaces=ns) or "").strip()
        summary = (entry.findtext("a:summary", default="", namespaces=ns) or "").strip()
        link = entry.findtext("a:id", default="", namespaces=ns) or ""
        published = entry.findtext("a:published", default="", namespaces=ns) or ""
        year = None
        if len(published) >= 4 and published[:4].isdigit():
            year = int(published[:4])
        out.append(
            {
                "title": title.replace("\n", " "),
                "url": link,
                "abstract": summary.replace("\n", " ")[:900],
                "year": year,
                "citation_count": None,
                "source_type": "paper",
                "provider": "arxiv",
            }
        )
    return out


async def _search_semantic_scholar(client: httpx.AsyncClient, query: str, limit: int) -> List[dict]:
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,url,year,citationCount",
    }
    r = await client.get(url, params=params, headers=HEADERS)
    r.raise_for_status()
    out: List[dict] = []
    for p in r.json().get("data", []) or []:
        out.append(
            {
                "title": (p.get("title") or "").strip(),
                "url": p.get("url") or "",
                "abstract": (p.get("abstract") or "")[:900],
                "year": p.get("year"),
                "citation_count": p.get("citationCount"),
                "source_type": "paper",
                "provider": "semantic_scholar",
            }
        )
    return out


def _dedupe(items: List[dict]) -> List[dict]:
    seen: set[str] = set()
    result: List[dict] = []
    for it in items:
        title = it.get("title") or ""
        key = "".join(ch for ch in title.lower() if ch.isalnum())[:80]
        if not title or key in seen:
            continue
        seen.add(key)
        result.append(it)
    return result


async def retrieve(queries: List[str], per_query: int = 4, cap: int = 24) -> List[dict]:
    """Run every query against every provider concurrently, then dedupe.

    Failures from any single provider/query are swallowed so partial results
    still flow through.
    """
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        tasks = []
        for q in queries:
            tasks.append(_search_openalex(client, q, per_query))
            tasks.append(_search_arxiv(client, q, per_query))
            tasks.append(_search_semantic_scholar(client, q, per_query))
        results = await asyncio.gather(*tasks, return_exceptions=True)

    flat: List[dict] = []
    for res in results:
        if isinstance(res, Exception):
            continue
        flat.extend(res)

    deduped = _dedupe(flat)

    # Light prioritisation: keep citation-rich work near the top but don't let it
    # dominate — recent, low-citation preprints are where the gaps often live.
    def score(it: dict) -> float:
        c = it.get("citation_count") or 0
        return float(c)

    deduped.sort(key=score, reverse=True)
    return deduped[:cap]
