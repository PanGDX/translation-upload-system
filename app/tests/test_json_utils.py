import os
import json
import pytest
from unittest.mock import patch, call
from app.utils.json_utils import (
    load_json,
    save_json,
    edit_chapter_entry,
    sync_stories_across_files,
    delete_story_globally,
    check_missing_chapters
)

@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory with dummy files."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    files = {
        "scraped": data_dir / "scraped.json",
        "translated": data_dir / "translated.json",
        "uploaded": data_dir / "uploaded.json"
    }

    # Create initial files
    save_json(str(files["scraped"]), {"Story A": [{"chapter": 1, "title": "First"}]})
    save_json(str(files["translated"]), {"Story B": [{"chapter": 1, "translated_title": "Erste"}]})
    
    # Use patch to make the json_utils module use this temp directory
    with patch("app.utils.json_utils.FILES", {k: str(v) for k, v in files.items()}):
        yield files

def test_load_json_exists(temp_data_dir):
    data = load_json(str(temp_data_dir["scraped"]))
    assert data["Story A"][0]["title"] == "First"

def test_load_json_not_exists(tmp_path):
    non_existent_file = tmp_path / "non_existent.json"
    data = load_json(str(non_existent_file))
    assert data == {}

def test_load_json_corrupted(tmp_path):
    corrupted_file = tmp_path / "corrupted.json"
    with open(corrupted_file, 'w') as f:
        f.write("this is not json")
    data = load_json(str(corrupted_file))
    assert data == {}

def test_save_json(tmp_path):
    file_path = tmp_path / "test.json"
    data = {"key": "value"}
    save_json(str(file_path), data)
    with open(file_path, 'r') as f:
        loaded_data = json.load(f)
    assert loaded_data == data

def test_edit_chapter_entry_existing(temp_data_dir):
    edit_chapter_entry("scraped", "Story A", 1, {"title": "New Title"})
    data = load_json(str(temp_data_dir["scraped"]))
    assert data["Story A"][0]["title"] == "New Title"

def test_edit_chapter_entry_new_chapter(temp_data_dir):
    edit_chapter_entry("scraped", "Story A", 2, {"title": "Second Chapter"})
    data = load_json(str(temp_data_dir["scraped"]))
    assert len(data["Story A"]) == 2
    assert data["Story A"][1]["title"] == "Second Chapter"

def test_edit_chapter_entry_new_story(temp_data_dir):
    edit_chapter_entry("scraped", "Story C", 1, {"title": "First Chapter"})
    data = load_json(str(temp_data_dir["scraped"]))
    # This function does not create new stories, it should just return
    assert "Story C" not in data

def test_sync_stories_across_files(temp_data_dir):
    sync_stories_across_files()
    scraped_data = load_json(str(temp_data_dir["scraped"]))
    translated_data = load_json(str(temp_data_dir["translated"]))
    uploaded_data = load_json(str(temp_data_dir["uploaded"]))
    
    assert "Story A" in translated_data
    assert "Story B" in scraped_data
    assert "Story A" in uploaded_data
    assert "Story B" in uploaded_data

@patch('builtins.input', return_value='y')
def test_delete_story_globally_confirm(mock_input, temp_data_dir):
    delete_story_globally("Story A")
    scraped_data = load_json(str(temp_data_dir["scraped"]))
    assert "Story A" not in scraped_data

@patch('builtins.input', return_value='n')
def test_delete_story_globally_cancel(mock_input, temp_data_dir):
    delete_story_globally("Story A")
    scraped_data = load_json(str(temp_data_dir["scraped"]))
    assert "Story A" in scraped_data

@patch('builtins.print')
def test_check_missing_chapters(mock_print, temp_data_dir):
    # Add a story with a missing chapter
    save_json(str(temp_data_dir["scraped"]), {
        "Story A": [{"chapter": 1}, {"chapter": 3}]
    })
    check_missing_chapters()
    
    # Check if the warning was printed
    mock_print.assert_any_call("  [WARNING] Story A: Missing chapters [2]")

@patch('builtins.print')
def test_check_no_missing_chapters(mock_print, temp_data_dir):
    save_json(str(temp_data_dir["scraped"]), {
        "Story A": [{"chapter": 1}, {"chapter": 2}]
    })
    check_missing_chapters()
    mock_print.assert_any_call("  [OK] Story A: 2 chapters (1 to 2)")
