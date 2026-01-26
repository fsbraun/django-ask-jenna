from typing import Any
import requests

from bs4 import BeautifulSoup, Comment, NavigableString, PageElement


class SemanticIndex:
    _headings: list[str] = ["h1", "h2", "h3", "h4", "h5", "h6"]
    _paragraphs: list[str] = ["p", "blockquote"]
    _lists: list[str] = ["ul", "ol", "li"]
    _links: list[str] = ["a"]
    _images: list[str] = ["img", "figure"]
    _code: list[str] = ["code", "pre"]
    _tables: list[str] = ["table"]
    _sections: list[str] = ["section", "article", "aside"]

    _tags: list[str] = (
        _headings + _paragraphs + _lists + _images + _code + _tables + _sections
    )
    _ignore: list[str] = [
        "script",
        "style",
        "nav",
        "header",
        "footer",
        "head",
        "button",
        "form",
        "template",
    ]

    def __init__(self, html: str):
        self._html: str = html
        self._soup: BeautifulSoup = BeautifulSoup(html, "lxml")
        self._index: list[dict[str, Any]] | None = None
        self._node_count: int = 0

    def _build_index(self):
        self._index = []
        self._node_count = 0

        def _process_node(node: PageElement):
            self._node_count += 1
            if node.name in self._tags:
                self._add_to_index(node)
            if node.name not in self._ignore:
                for child in node.children:
                    if child.name:
                        _process_node(child)

        _process_node(self._soup)

    def _to_text(self, node: PageElement) -> str:
        if node.name == "a" and node.get("href", "#") != "#":
            return f'[{node.get_text(separator=" ", strip=True)}]({node.get("href")})'
        return "".join(
            [
                child.string.strip()
                if isinstance(child, NavigableString)
                else self._to_text(child)
                for child in node.children
            ]
        )

    def _to_markdown(self, node: PageElement) -> str:
        if isinstance(node, Comment):
            return ""

        text = (
            self._to_text(node)
            if node.name != "a"
            else node.get_text(separator=" ", strip=True)
        )
        text = text.replace(chr(173), "")  # Remove soft hyphens
        if node.name in self._headings:
            level = (
                int(node.name[1])
                if len(node.name) == 2 and node.name[1].isdigit()
                else 1
            )
            prefix = "#" * max(1, min(level, 6))
            return f"{prefix} {text}\n"

        if node.name == "blockquote":
            return "> " + text + "\n"

        if node.name == "p":
            return text + "\n\n"

        if node.name in ("ul", "ol"):
            items = []
            for idx, li in enumerate(node.find_all("li", recursive=False), start=1):
                bullet = f"{idx}. " if node.name == "ol" else "- "
                items.append(bullet + li.get_text(separator=" ", strip=True))
            return "\n".join(items)

        if node.name == "li":
            return "- " + text

        if node.name == "a":
            if text:
                href = node.get("href", "")
                return f"[{text}]({href})" if href and href != "#" else text
            return ""

        if node.name in ("img", "figure"):
            src = node.get("src") or ""
            alt = node.get("alt") or text
            if not src and not alt:
                return ""
            return f"![{alt}]({src})" if src else f"![{alt}]()"

        if node.name == "code":
            return f"`{text}`"

        if node.name == "pre":
            return f"```\n{text}\n```"

        if node.name == "table":
            rows = []
            for tr in node.find_all("tr", recursive=False):
                cells = [
                    c.get_text(separator=" ", strip=True)
                    for c in tr.find_all(["th", "td"], recursive=False)
                ]
                if cells:
                    rows.append(" | ".join(cells))
            return "\n".join(rows)

        if node.name in self._sections:
            return text

        return text

    def _add_to_index(self, node: PageElement) -> dict[str, Any]:
        self._index.append(
            {
                "tag": node.name,
                "text": node.get_text(separator=" ", strip=True).replace(chr(173), ""),
                "md": self._to_markdown(node),
                "node": node,
            }
        )

    def get_index(self) -> list[dict[str, Any]]:
        if self._index is None:
            self._build_index()
        return self._index

    def to_markdown(self) -> str:
        return "\n".join([node["md"] for node in self.get_index()])

    def to_html(self) -> str:
        return "".join(str(child) for child in self._soup.body.children)

    @property
    def content_score(self) -> float:
        """
        Simple measure for the content density of the HTML document.

        :return: The content density of the HTML document.
        :rtype: float
        """
        return len(self.get_index()) / self._node_count


if __name__ == "__main__":
    import sys

    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.uibk.ac.at/de/"
    html = requests.get(url).text
    index = SemanticIndex(html)

    print(index.to_markdown())

    sys.stderr.write(f"Content score: {index.content_score}\n")
