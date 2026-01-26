import pytest


from cms_mcp import errors
from cms_mcp.markdown import SemanticIndex


def test_to_markdown_captures_supported_tags():
    html = """
    <html><body>
      <h1>Title</h1>
      <p>Paragraph with <a href="https://example.com">link</a></p>
      <ul><li>First</li><li>Second</li></ul>
      <img src="/img.png" alt="Pic">
    </body></html>
    """

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

    index = SemanticIndex(html)
    md = index.to_markdown()
    tags = {item["tag"] for item in index.get_index()}

    assert "code" in tags
    assert "pre" in tags
    assert "`snippet`" in md
    assert "```\nline1\nline2\n```" in md


def test_sections_articles_aside_are_indexed():
    html = """
        <html><body>
            <section>Section text</section>
            <article>Article text</article>
            <aside>Aside text</aside>
        </body></html>
        """

    index = SemanticIndex(html)
    tags = {item["tag"] for item in index.get_index()}
    md = index.to_markdown()

    assert {"section", "article", "aside"}.issubset(tags)
    assert "Section text" in md
    assert "Article text" in md
    assert "Aside text" in md


def test_div_and_ignored_tags_are_not_indexed():
    html = """
        <html><body>
            <p>Keep me</p>
            <div>Skip me</div>
            <script>ignored()</script>
        </body></html>
        """

    index = SemanticIndex(html)
    tags = {item["tag"] for item in index.get_index()}
    md = index.to_markdown()

    assert "div" not in tags
    assert "script" not in tags
    assert "Keep me" in md
    assert "Skip me" not in md
    assert "ignored()" not in md


test_content = """
    <html><body>
        <h1 data-secret="preserve-attributes">Keep me</h1>
        <div>Skip me</div>
        <p>We offer fast delivery worldwide</p>
        <script>ignored()</script>
        <h2>Keep me</h2>
    </body></html>
    """

test_operations = [
    {
        "op": "replace_block",
        "target": {"kind": "paragraph", "match": "We offer fast delivery worldwide"},
        "new_markdown": "We offer [fast, carbon-neutral delivery](/delivery) worldwide.",
    },
    {
        "op": "insert_before",
        "target": {"kind": "paragraph", "match": "We offer fast delivery worldwide"},
        "new_markdown": "We offer [fast, carbon-neutral delivery](/delivery) worldwide.",
    },
]


def test_replace_block_replaces_target_node():
    """Test that replace_block replaces the matched target node with new markdown content."""
    index = SemanticIndex(test_content)

    # Get original markdown and HTML
    original_md = index.to_markdown()
    original_html = index.to_html()
    assert "We offer fast delivery worldwide" in original_md
    assert "We offer fast delivery worldwide" in original_html

    # Execute replace operation
    operation = test_operations[0]
    index.execute_operation(operation)

    # Get updated markdown
    updated_md = index.to_markdown()
    updated_html = index.to_html()
    # Original text should be replaced in both markdown and HTML
    assert "We offer fast delivery worldwide" not in updated_md
    assert "We offer fast delivery worldwide" not in updated_html
    # New content should be present in both
    assert "[fast, carbon-neutral delivery](/delivery)" in updated_md
    assert "fast, carbon-neutral delivery" in updated_html
    assert "/delivery" in updated_html
    # Surrounding content should remain
    assert "# Keep me" in updated_md
    assert "## Keep me" in updated_md
    assert "Keep me" in updated_html


def test_insert_before_adds_content_before_target():
    """Test that insert_before adds new markdown content before the matched target."""

    index = SemanticIndex(test_content)

    # Get original markdown and HTML
    original_html = index.to_html()
    assert "<p>We offer fast delivery worldwide</p>" in original_html

    # Execute insert operation
    operation = test_operations[1]
    index.execute_operation(operation)

    # Get updated markdown and HTML
    updated_md = index.to_markdown()
    updated_html = index.to_html()

    # Original text should still be present in both
    assert "We offer fast delivery worldwide" in updated_md
    assert "We offer fast delivery worldwide" in updated_html
    # New content should be present in both
    assert "[fast, carbon-neutral delivery](/delivery)" in updated_md
    assert "fast, carbon-neutral delivery" in updated_html
    assert "/delivery" in updated_html
    # New content should appear before original (verify order in markdown)
    new_pos = updated_md.find("[fast, carbon-neutral delivery](/delivery)")
    orig_pos = updated_md.find("We offer fast delivery worldwide")
    assert new_pos < orig_pos, "New content should appear before original text"
    # New content should also appear before original in HTML
    new_html_pos = updated_html.find("fast, carbon-neutral delivery")
    orig_html_pos = updated_html.find("We offer fast delivery worldwide")
    assert (
        new_html_pos < orig_html_pos
    ), "New content should appear before original text in HTML"


def test_find_target_with_matching_kind_and_text():
    """Test that find_target correctly identifies matching nodes."""
    index = SemanticIndex(test_content)

    target = {"kind": "paragraph", "match": "We offer fast delivery worldwide"}

    found = index.find_target(target)

    assert found is not None
    assert found["kind"] == "paragraph"
    assert "We offer fast delivery worldwide" in found["text"]


def test_find_target_raises_on_no_match():
    """Test that find_target raises ToolError when no match is found."""
    from mcp import MCPError

    index = SemanticIndex(test_content)

    target = {"kind": "paragraph", "match": "This text does not exist"}

    with pytest.raises(MCPError) as exc_info:
        index.find_target(target)

    assert exc_info.value.code == errors.NO_MATCH
    assert "No content block matches" in exc_info.value.message


def test_find_target_raises_on_ambiguous_match():
    """Test that find_target raises ToolError when multiple matches are found."""
    from mcp import MCPError

    html = """
    <html><body>
        <h1>Keep me</h1>
        <p>Keep me</p>
        <p>Keep me</p>
    </body></html>
    """

    index = SemanticIndex(html)

    target = {"kind": "heading", "match": "Keep me"}

    # This should find multiple matches, but they're different kinds, so no error
    # Let's test with actual duplicate
    target = {"kind": "paragraph", "match": "Keep me"}

    with pytest.raises(MCPError) as exc_info:
        index.find_target(target)

    assert exc_info.value.code == errors.AMBIGUOUS_TARGET
    assert "Multiple content blocks match" in exc_info.value.message


def test_validate_target_rejects_invalid_kind():
    """Test that validate_target raises error for invalid kind."""
    from mcp import MCPError

    index = SemanticIndex(test_content)

    target = {"kind": "invalid_kind", "match": "some text"}

    with pytest.raises(MCPError) as exc_info:
        index.validate_target(target)

    assert exc_info.value.code == errors.INVALID_TARGET
    assert "Invalid target kind" in exc_info.value.message


def test_markdown_to_nodes_converts_markdown_to_soup_elements():
    """Test that markdown_to_nodes correctly converts markdown strings to soup elements."""
    index = SemanticIndex(test_content)

    markdown = "## New Heading\n\nNew paragraph with [link](https://example.com)."
    nodes = index.markdown_to_nodes(markdown)

    assert len(nodes) > 0
    # Check that heading was created
    heading = next((n for n in nodes if hasattr(n, "name") and n.name == "h2"), None)
    assert heading is not None

    # Check that paragraph was created
    para = next((n for n in nodes if hasattr(n, "name") and n.name == "p"), None)
    assert para is not None


def test_insert_at_end_appends_content_to_body():
    """Test that insert_at_end appends new markdown content at the end of the document."""
    index = SemanticIndex(test_content)

    # Get original markdown and HTML
    original_len = len(index.get_index())

    # Execute insert_at_end operation
    operation = {
        "op": "insert_at_end",
        "new_markdown": "## Footer Section\n\nThis is the footer content with a [link](/footer).",
    }
    index.execute_operation(operation)

    # Get updated markdown and HTML
    updated_md = index.to_markdown()
    updated_html = index.to_html()
    updated_len = len(index.get_index())

    # New content should be present in both markdown and HTML
    assert "## Footer Section" in updated_md
    assert "Footer Section" in updated_html
    assert "This is the footer content" in updated_md
    assert "This is the footer content" in updated_html
    assert "[link](/footer)" in updated_md
    assert "/footer" in updated_html

    # Original content should still be present
    assert "# Keep me" in updated_md
    assert "Keep me" in updated_html

    # New content should appear at the end
    footer_pos = updated_md.rfind("## Footer Section")
    h2_pos = updated_md.rfind("## Keep me")
    assert footer_pos > h2_pos, "Footer should appear after all original content"

    # Index should have more entries
    assert updated_len > original_len, "Index should contain new entries"
