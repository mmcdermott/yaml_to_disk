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


def test_file_write_null_contents(tmp_path: Path):
    """File with None contents creates an empty file via touch."""
    f = File(Path("empty.txt"), None)
    f.write(tmp_path)
    assert (tmp_path / "empty.txt").exists()
    assert (tmp_path / "empty.txt").read_text() == ""


def test_file_write_unknown_ext_str_uses_txt(tmp_path: Path):
    """String contents with unknown extension falls back to .txt handler."""
    f = File(Path("readme.unknown"), "hello")
    f.write(tmp_path, use_txt_on_unk_str_files=True)
    assert (tmp_path / "readme.unknown").read_text() == "hello"


def test_file_write_unknown_ext_non_str_raises(tmp_path: Path):
    """Non-string contents with unknown extension raises ValueError."""
    f = File(Path("data.unknown"), {"key": "val"})
    with pytest.raises(ValueError, match="No file type found"):
        f.write(tmp_path)


def test_file_write_validation_failure(tmp_path: Path):
    """Contents that fail validation raise ValueError."""
    f = File(Path("bad.csv"), 12345)
    with pytest.raises(ValueError, match="fail validation"):
        f.write(tmp_path)


def test_parse_yaml_contents_invalid_type():
    with pytest.raises(TypeError, match="YAML contents must be a dictionary or list"):
        YamlDisk._parse_yaml_contents("not a dict or list")


def test_parse_yaml_contents_invalid_item_type():
    with pytest.raises(TypeError, match="Invalid item type"):
        YamlDisk._parse_yaml_contents([123])


def test_parse_yaml_contents_dict_item_bad_format():
    """Dict item with non-string key or multiple keys."""
    with pytest.raises(ValueError, match="Invalid format"):
        YamlDisk._parse_yaml_contents([{1: "val"}])


def test_parse_yaml_contents_empty_dir():
    """Bare string ending in / creates empty directory."""
    parsed = YamlDisk._parse_yaml_contents(["emptydir/"])
    assert len(parsed) == 1
    assert isinstance(parsed[0], Directory)
    assert parsed[0].contents == []


def test_parse_yaml_contents_bare_filename():
    """Bare string without trailing / creates a file with None contents."""
    parsed = YamlDisk._parse_yaml_contents(["file.txt"])
    assert len(parsed) == 1
    assert isinstance(parsed[0], File)
    assert parsed[0].contents is None


def test_parse_yaml_contents_extensionless_name_as_dir():
    """A key without a file extension with dict/list contents is treated as a directory."""
    parsed = YamlDisk._parse_yaml_contents({"mydir": ["file.txt"]})
    assert len(parsed) == 1
    assert isinstance(parsed[0], Directory)


def test_parse_yaml_contents_extensionless_name_as_file():
    """A key without a file extension with scalar contents is treated as a file."""
    parsed = YamlDisk._parse_yaml_contents({"Makefile": "echo hello"})
    assert len(parsed) == 1
    assert isinstance(parsed[0], File)
    assert parsed[0].rel_path == Path("Makefile")
    assert parsed[0].contents == "echo hello"


def test_extensionless_file_write_roundtrip(tmp_path: Path):
    """Regression test for issue #11: extensionless filenames with string contents write correctly."""
    from yaml_to_disk.yaml_to_disk import yaml_disk

    data = {"Makefile": "echo hi", "LICENSE": "MIT", "subdir/": {"Dockerfile": "FROM scratch"}}
    yaml_disk(data, root_dir=tmp_path)
    assert (tmp_path / "Makefile").read_text() == "echo hi"
    assert (tmp_path / "LICENSE").read_text() == "MIT"
    assert (tmp_path / "subdir" / "Dockerfile").read_text() == "FROM scratch"


def test_parse_from_yaml_file(tmp_path: Path):
    """_parse can accept a Path to a YAML file."""
    yaml_fp = tmp_path / "spec.yaml"
    yaml_fp.write_text("a.txt: hello\n")
    parsed = YamlDisk._parse(yaml_fp)
    assert len(parsed) == 1
    assert isinstance(parsed[0], File)
    assert parsed[0].contents == "hello"


def test_parse_from_yaml_filename_string(tmp_path: Path):
    """_parse can accept a string that looks like a .yaml filename."""
    yaml_fp = tmp_path / "spec.yaml"
    yaml_fp.write_text("b.txt: world\n")
    parsed = YamlDisk._parse(str(yaml_fp))
    assert len(parsed) == 1
    assert parsed[0].contents == "world"


def test_parse_invalid_type():
    with pytest.raises(TypeError, match="disk_contents must be a string, Path, dict, or list"):
        YamlDisk._parse(12345)
