import pytest
from pydantic import ValidationError
import frontmatter

# Adjust the import based on your actual project structure
# If your file is at app/core/models.py, use:
from app.models import (
    Chapter,
    Raw_Chapter,
    Translated_Chapter
)
from app.utils.markdown_manager import (
    markdown_string_to_chapter_class,
    chapter_class_to_markdown_string
)

# --- Fixtures ---

@pytest.fixture
def raw_chapter_data():
    return {
        "file_name": 101,
        "title": "The Beginning",
        "chapter_number": "1",
        "content": "This is raw content.",
        "url": "https://example.com/chapter/1",
        "type": "raw"
    }

@pytest.fixture
def translated_chapter_data():
    return {
        "file_name": 102,
        "title": "The Translation",
        "chapter_number": "2",
        "content": "This is translated content.",
        "raw_path": ["source_v1.md", "source_v2.md"],
        "type": "translated"
    }

# --- Tests for markdown_string_to_chapter_class ---

def test_markdown_to_raw_chapter(raw_chapter_data):
    """Test parsing a valid markdown string into a Raw_Chapter object."""
    md_content = f"""---
file_name: {raw_chapter_data['file_name']}
title: "{raw_chapter_data['title']}"
chapter_number: "{raw_chapter_data['chapter_number']}"
url: "{raw_chapter_data['url']}"
type: "raw"
---
{raw_chapter_data['content']}"""

    result = markdown_string_to_chapter_class(md_content)

    assert isinstance(result, Raw_Chapter)
    assert result.file_name == raw_chapter_data['file_name']
    assert result.url == raw_chapter_data['url']
    assert result.content.strip() == raw_chapter_data['content']

def test_markdown_to_translated_chapter(translated_chapter_data):
    """Test parsing a valid markdown string into a Translated_Chapter object."""
    # Note: formatting lists in f-strings for YAML can be tricky, doing it manually
    md_content = f"""---
file_name: {translated_chapter_data['file_name']}
title: "{translated_chapter_data['title']}"
chapter_number: "{translated_chapter_data['chapter_number']}"
raw_path:
  - {translated_chapter_data['raw_path'][0]}
  - {translated_chapter_data['raw_path'][1]}
type: "translated"
---
{translated_chapter_data['content']}"""

    result = markdown_string_to_chapter_class(md_content)

    assert isinstance(result, Translated_Chapter)
    assert result.file_name == translated_chapter_data['file_name']
    assert result.raw_path == translated_chapter_data['raw_path']
    assert result.content.strip() == translated_chapter_data['content']

def test_markdown_missing_type_raises_error():
    """Test that missing 'type' in frontmatter raises ValueError."""
    md_content = """---
file_name: 1
title: "No Type"
chapter_number: "1"
---
Content"""
    
    with pytest.raises(ValueError) as excinfo:
        markdown_string_to_chapter_class(md_content)
    assert "Unknown or missing 'type'" in str(excinfo.value)

def test_markdown_unknown_type_raises_error():
    """Test that an unknown 'type' raises ValueError."""
    md_content = """---
file_name: 1
title: "Bad Type"
chapter_number: "1"
type: "unknown_weird_type"
---
Content"""
    
    with pytest.raises(ValueError) as excinfo:
        markdown_string_to_chapter_class(md_content)
    assert "Unknown or missing 'type'" in str(excinfo.value)

def test_markdown_pydantic_validation_error():
    """Test that valid frontmatter missing required Pydantic fields raises ValidationError."""
    # Missing 'url' for Raw_Chapter
    md_content = """---
file_name: 1
title: "Missing URL"
chapter_number: "1"
type: "raw"
---
Content"""
    
    with pytest.raises(ValidationError):
        markdown_string_to_chapter_class(md_content)

# --- Tests for chapter_class_to_markdown_string ---

def test_raw_chapter_to_markdown(raw_chapter_data):
    """Test converting a Raw_Chapter object to a markdown string."""
    chapter = Raw_Chapter(**raw_chapter_data)
    
    md_string = chapter_class_to_markdown_string(chapter)
    
    # Parse it back using frontmatter directly to verify structure
    metadata, content = frontmatter.parse(md_string)
    
    assert metadata['file_name'] == raw_chapter_data['file_name']
    assert metadata['type'] == "raw"
    assert metadata['url'] == raw_chapter_data['url']
    assert content.strip() == raw_chapter_data['content']

def test_translated_chapter_to_markdown(translated_chapter_data):
    """Test converting a Translated_Chapter object to a markdown string."""
    chapter = Translated_Chapter(**translated_chapter_data)
    
    md_string = chapter_class_to_markdown_string(chapter)
    
    metadata, content = frontmatter.parse(md_string)
    
    assert metadata['type'] == "translated"
    assert metadata['raw_path'] == translated_chapter_data['raw_path']
    assert content.strip() == translated_chapter_data['content']

# --- Round Trip Tests (Integration) ---

def test_round_trip_raw_chapter(raw_chapter_data):
    """
    Ensure Object -> String -> Object results in the exact same data.
    """
    original_obj = Raw_Chapter(**raw_chapter_data)
    
    # 1. Convert to string
    md_string = chapter_class_to_markdown_string(original_obj)
    
    # 2. Convert back to object
    new_obj = markdown_string_to_chapter_class(md_string)
    
    # 3. Compare
    assert original_obj == new_obj

def test_round_trip_translated_chapter(translated_chapter_data):
    """
    Ensure Object -> String -> Object results in the exact same data.
    """
    original_obj = Translated_Chapter(**translated_chapter_data)
    
    md_string = chapter_class_to_markdown_string(original_obj)
    new_obj = markdown_string_to_chapter_class(md_string)
    
    assert original_obj == new_obj