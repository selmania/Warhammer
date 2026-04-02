"""Product search module — scrapes and queries online hobby retailers and forums."""

from __future__ import annotations

import re
import time
import urllib.parse
from dataclasses import dataclass, field
from typing import Optional

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class ProductResult:
    title: str
    price: str
    url: str
    source: str
    description: str = ""
    rating: Optional[str] = None
    in_stock: Optional[bool] = None


@dataclass
class ForumPost:
    title: str
    url: str
    source: str
    snippet: str = ""


# ---------------------------------------------------------------------------
# Retailer / source definitions
# ---------------------------------------------------------------------------

HOBBY_SOURCES = [
    {
        "name": "Amazon",
        "search_url": "https://www.amazon.com/s?k={query}",
        "type": "retailer",
    },
    {
        "name": "eBay",
        "search_url": "https://www.ebay.com/sch/i.html?_nkw={query}",
        "type": "retailer",
    },
    {
        "name": "Miniature Market",
        "search_url": "https://www.miniaturemarket.com/searchresults?q={query}",
        "type": "retailer",
    },
    {
        "name": "Games Workshop",
        "search_url": "https://www.games-workshop.com/en-US/searchResults?N=0&Ntt={query}",
        "type": "retailer",
    },
    {
        "name": "The Army Painter",
        "search_url": "https://thearmypainter.com/?s={query}",
        "type": "retailer",
    },
    {
        "name": "Woodland Scenics",
        "search_url": "https://woodlandscenics.woodlandscenics.com/show/category/702AllProducts?find={query}",
        "type": "retailer",
    },
]

FORUM_SOURCES = [
    {
        "name": "Reddit r/TerrainBuilding",
        "search_url": "https://www.reddit.com/r/TerrainBuilding/search/?q={query}&restrict_sr=1",
        "type": "forum",
    },
    {
        "name": "Reddit r/Warhammer",
        "search_url": "https://www.reddit.com/r/Warhammer/search/?q={query}&restrict_sr=1",
        "type": "forum",
    },
    {
        "name": "DakkaDakka",
        "search_url": "https://www.dakkadakka.com/dakkaforum/search.page?search={query}",
        "type": "forum",
    },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

REQUEST_TIMEOUT = 12  # seconds


# ---------------------------------------------------------------------------
# Low-level fetch helpers
# ---------------------------------------------------------------------------

def _fetch_page(url: str) -> Optional[BeautifulSoup]:
    """Fetch a URL and return parsed soup, or None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except (requests.RequestException, Exception):
        return None


def _clean(text: str) -> str:
    """Collapse whitespace."""
    return re.sub(r"\s+", " ", text).strip()


# ---------------------------------------------------------------------------
# Retailer scrapers (best-effort — sites change layouts frequently)
# ---------------------------------------------------------------------------

def _parse_amazon(soup: BeautifulSoup, limit: int = 5) -> list[ProductResult]:
    results: list[ProductResult] = []
    for item in soup.select('[data-component-type="s-search-result"]')[:limit]:
        title_el = item.select_one("h2 a span")
        price_el = item.select_one(".a-price .a-offscreen")
        link_el = item.select_one("h2 a")
        if title_el and link_el:
            href = link_el.get("href", "")
            url = f"https://www.amazon.com{href}" if href.startswith("/") else href
            results.append(ProductResult(
                title=_clean(title_el.get_text()),
                price=_clean(price_el.get_text()) if price_el else "See listing",
                url=url,
                source="Amazon",
            ))
    return results


def _parse_ebay(soup: BeautifulSoup, limit: int = 5) -> list[ProductResult]:
    results: list[ProductResult] = []
    for item in soup.select(".s-item")[:limit + 1]:
        title_el = item.select_one(".s-item__title")
        price_el = item.select_one(".s-item__price")
        link_el = item.select_one(".s-item__link")
        if title_el and link_el:
            title = _clean(title_el.get_text())
            if title.lower() == "shop on ebay":
                continue
            results.append(ProductResult(
                title=title,
                price=_clean(price_el.get_text()) if price_el else "See listing",
                url=link_el.get("href", ""),
                source="eBay",
            ))
    return results[:limit]


def _parse_generic(soup: BeautifulSoup, source_name: str, limit: int = 5) -> list[ProductResult]:
    """Fallback parser — grabs links with price-like text nearby."""
    results: list[ProductResult] = []
    price_pattern = re.compile(r"\$\d+\.?\d*")
    for link in soup.find_all("a", href=True):
        text = _clean(link.get_text())
        if len(text) < 10 or len(text) > 200:
            continue
        parent_text = _clean(link.parent.get_text()) if link.parent else ""
        price_match = price_pattern.search(parent_text)
        if price_match:
            results.append(ProductResult(
                title=text[:120],
                price=price_match.group(),
                url=link["href"],
                source=source_name,
            ))
            if len(results) >= limit:
                break
    return results


# Source name → parser map
_PARSERS = {
    "Amazon": _parse_amazon,
    "eBay": _parse_ebay,
}


# ---------------------------------------------------------------------------
# Forum scrapers
# ---------------------------------------------------------------------------

def _parse_reddit(soup: BeautifulSoup, source_name: str, limit: int = 5) -> list[ForumPost]:
    posts: list[ForumPost] = []
    for link in soup.select("a[href*='/comments/']"):
        title = _clean(link.get_text())
        href = link.get("href", "")
        if len(title) < 10:
            continue
        url = f"https://www.reddit.com{href}" if href.startswith("/") else href
        if url not in {p.url for p in posts}:
            posts.append(ForumPost(title=title, url=url, source=source_name))
            if len(posts) >= limit:
                break
    return posts


def _parse_generic_forum(soup: BeautifulSoup, source_name: str, limit: int = 5) -> list[ForumPost]:
    posts: list[ForumPost] = []
    for link in soup.find_all("a", href=True):
        text = _clean(link.get_text())
        if 20 < len(text) < 200:
            posts.append(ForumPost(title=text, url=link["href"], source=source_name))
            if len(posts) >= limit:
                break
    return posts


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class ProductSearchEngine:
    """Searches hobby retailers and forums for terrain-building products and discussions."""

    def __init__(self, rate_limit_seconds: float = 1.5):
        self.rate_limit = rate_limit_seconds
        self._last_request_time = 0.0

    def _throttle(self) -> None:
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self._last_request_time = time.time()

    # -- product search --------------------------------------------------

    def search_products(
        self,
        query: str,
        sources: Optional[list[str]] = None,
        limit_per_source: int = 5,
    ) -> list[ProductResult]:
        """Search hobby retailers for products matching *query*.

        Returns a combined list of ProductResult across sources.
        """
        results: list[ProductResult] = []
        for src in HOBBY_SOURCES:
            if sources and src["name"] not in sources:
                continue
            url = src["search_url"].format(query=urllib.parse.quote_plus(query))
            self._throttle()
            soup = _fetch_page(url)
            if not soup:
                continue
            parser = _PARSERS.get(src["name"])
            if parser:
                results.extend(parser(soup, limit=limit_per_source))
            else:
                results.extend(_parse_generic(soup, src["name"], limit=limit_per_source))
        return results

    # -- forum search ----------------------------------------------------

    def search_forums(
        self,
        query: str,
        limit_per_source: int = 5,
    ) -> list[ForumPost]:
        """Search wargaming forums for discussions matching *query*."""
        posts: list[ForumPost] = []
        for src in FORUM_SOURCES:
            url = src["search_url"].format(query=urllib.parse.quote_plus(query))
            self._throttle()
            soup = _fetch_page(url)
            if not soup:
                continue
            if "reddit" in src["name"].lower():
                posts.extend(_parse_reddit(soup, src["name"], limit=limit_per_source))
            else:
                posts.extend(_parse_generic_forum(soup, src["name"], limit=limit_per_source))
        return posts

    # -- convenience: search for a specific material ---------------------

    def search_material(self, material_keywords: list[str], limit_per_source: int = 3) -> list[ProductResult]:
        """Search for a specific material across retailers using its keywords."""
        all_results: list[ProductResult] = []
        for kw in material_keywords:
            all_results.extend(self.search_products(kw, limit_per_source=limit_per_source))
        # Deduplicate by URL
        seen: set[str] = set()
        unique: list[ProductResult] = []
        for r in all_results:
            if r.url not in seen:
                seen.add(r.url)
                unique.append(r)
        return unique

    # -- build a full shopping list for a board design -------------------

    def build_shopping_list(
        self,
        materials: list[dict],
        limit_per_material: int = 3,
    ) -> dict[str, list[ProductResult]]:
        """Given a list of material dicts (with 'name' and 'search_keywords'),
        return a mapping of material name → product search results."""
        shopping: dict[str, list[ProductResult]] = {}
        for mat in materials:
            name = mat.get("name", "Unknown")
            keywords = mat.get("search_keywords", [name])
            shopping[name] = self.search_material(keywords, limit_per_source=limit_per_material)
        return shopping


# Convenience singleton
search_engine = ProductSearchEngine()
