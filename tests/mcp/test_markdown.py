import importlib
import sys
import types

import pytest


def _semantic_index():
    if "requests" not in sys.modules:
        sys.modules["requests"] = types.SimpleNamespace(get=lambda url: None)
    return importlib.import_module("cms_mcp.markdown").SemanticIndex


def test_to_markdown_captures_supported_tags():
    html = """
    <html><body>
      <h1>Title</h1>
      <p>Paragraph with <a href="https://example.com">link</a></p>
      <ul><li>First</li><li>Second</li></ul>
      <img src="/img.png" alt="Pic">
    </body></html>
    """

    SemanticIndex = _semantic_index()
    index = SemanticIndex(html)
    tags = {item["tag"] for item in index.get_index()}

    assert {"h1", "p", "a", "ul", "li", "img"}.issubset(tags)

    md = index.to_markdown()
    assert "# Title" in md
    assert "Paragraph with [link](https://example.com)" in md
    assert "- First" in md
    assert "![Pic](/img.png)" in md


def test_content_score_and_soft_hyphen_stripping():
    html = "<html><body><p>Soft\u00adhyphen</p></body></html>"

    SemanticIndex = _semantic_index()
    index = SemanticIndex(html)
    md = index.to_markdown()

    assert "Soft" in md and "hyphen" in md and "\u00ad" not in md
    assert index.content_score == pytest.approx(1 / 4)


def test_html_comments_are_ignored_in_markdown():
    html = """
    <html><body>
      <!-- hidden comment -->
      <p>Visible text</p>
    </body></html>
    """

    SemanticIndex = _semantic_index()
    index = SemanticIndex(html)
    md = index.to_markdown()

    assert "Visible text" in md
    assert "hidden comment" not in md


def test_table_is_serialized_as_rows():
    html = """
        <html><body>
            <table>
                <tr><th>H1</th><th>H2</th></tr>
                <tr><td>A1</td><td>B1</td></tr>
            </table>
        </body></html>
        """

    SemanticIndex = _semantic_index()
    index = SemanticIndex(html)
    md = index.to_markdown()

    assert "H1 | H2" in md
    assert "A1 | B1" in md


def test_code_and_pre_are_rendered():
    html = """
        <html><body>
            <p>Inline <code>snippet</code> text.</p>
            <pre>line1\nline2</pre>
        </body></html>
        """

    SemanticIndex = _semantic_index()
    index = SemanticIndex(html)
    md = index.to_markdown()
    tags = {item["tag"] for item in index.get_index()}

    assert "code" in tags
    assert "pre" in tags
    assert "`snippet`" in md
    assert "```\nline1\nline2\n```" in md
