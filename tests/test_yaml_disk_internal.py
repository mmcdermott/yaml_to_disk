from pathlib import Path

import pytest

from yaml_to_disk.yaml_to_disk import Directory, File, YamlDisk


def test_is_yaml_file():
    assert YamlDisk._is_yaml_file("foo.yaml")
    assert YamlDisk._is_yaml_file("foo.yml")
    assert not YamlDisk._is_yaml_file("foo.txt")
    with pytest.raises(TypeError):
        YamlDisk._is_yaml_file(1)  # type: ignore[arg-type]


def test_read_yaml_file(tmp_path: Path):
    fp = tmp_path / "cfg.yaml"
    fp.write_text("a: 1")
    assert YamlDisk._read_yaml_file(fp) == {"a": 1}
    with pytest.raises(FileNotFoundError):
        YamlDisk._read_yaml_file(tmp_path / "missing.yaml")


def test_parse_yaml_contents_and_write(tmp_path: Path):
    yaml_data = {
        "dir/": {"a.txt": "hi"},
        "b.txt": "bye",
    }
    parsed = YamlDisk._parse_yaml_contents(yaml_data)
    assert len(parsed) == 2
    dir_entry = next(p for p in parsed if isinstance(p, Directory))
    file_entry = next(p for p in parsed if isinstance(p, File) and p.rel_path.name == "b.txt")

    dir_entry.write(tmp_path)
    file_entry.write(tmp_path)

    assert (tmp_path / "dir" / "a.txt").read_text() == "hi"
    assert (tmp_path / "b.txt").read_text() == "bye"


def test_file_write_errors(tmp_path: Path):
    file = File(Path("foo.txt"), "bar")
    file.write(tmp_path)
    with pytest.raises(FileExistsError):
        file.write(tmp_path)
    file.write(tmp_path, do_overwrite=True)
    (tmp_path / "dir").mkdir()
    with pytest.raises(FileExistsError):
        File(Path("dir"), "x").write(tmp_path)
    with pytest.raises(IsADirectoryError):
        File(Path("dir"), "x").write(tmp_path, do_overwrite=True)


def test_directory_write_errors(tmp_path: Path):
    (tmp_path / "a_file").write_text("x")
    dir_entry = Directory(Path("a_file"), [])
    with pytest.raises(NotADirectoryError):
        dir_entry.write(tmp_path)
