import json
 
import pytest
 
import memory
 
 
@pytest.fixture(autouse=True)
def isolated_memory_file(tmp_path, monkeypatch):
    test_file = tmp_path / "test_memory.json"
    monkeypatch.setattr(memory, "MEMORY_FILE", test_file)
    yield test_file
 
 
def test_load_memory_returns_empty_notes_when_file_missing():
    assert memory.load_memory() == {"notes": []}
 
 
def test_load_memory_reads_existing_file(isolated_memory_file):
    isolated_memory_file.write_text(json.dumps({"notes": [{"text": "hi"}]}))
    assert memory.load_memory() == {"notes": [{"text": "hi"}]}
 
 
def test_load_memory_backfills_missing_notes_key(isolated_memory_file):
    isolated_memory_file.write_text(json.dumps({}))
    assert memory.load_memory() == {"notes": []}
 
 
def test_load_memory_recovers_from_corrupt_json(isolated_memory_file):
    isolated_memory_file.write_text("{not valid json")
    assert memory.load_memory() == {"notes": []}
 
 
def test_save_memory_writes_json_to_disk(isolated_memory_file):
    memory.save_memory({"notes": [{"text": "saved"}]})
    on_disk = json.loads(isolated_memory_file.read_text())
    assert on_disk == {"notes": [{"text": "saved"}]}
 
 
def test_add_note_appends_a_note_with_date_and_time():
    memory.add_note("remember this")
    notes = memory.load_memory()["notes"]
    assert len(notes) == 1
    assert notes[0]["text"] == "remember this"
    assert "date" in notes[0]
    assert "time" in notes[0]
 
 
def test_add_note_preserves_existing_notes():
    memory.add_note("first")
    memory.add_note("second")
    notes = memory.load_memory()["notes"]
    assert [n["text"] for n in notes] == ["first", "second"]
 
 
def test_get_recent_notes_respects_limit():
    for i in range(5):
        memory.add_note(f"note {i}")
    recent = memory.get_recent_notes(limit=2)
    assert [n["text"] for n in recent] == ["note 3", "note 4"]
 
 
def test_get_recent_notes_defaults_to_20():
    for i in range(3):
        memory.add_note(f"note {i}")
    assert len(memory.get_recent_notes()) == 3
 
 
def test_clear_memory_empties_notes():
    memory.add_note("to be cleared")
    memory.clear_memory()
    assert memory.load_memory() == {"notes": []}