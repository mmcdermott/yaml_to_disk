# `yaml_to_disk`

[![PyPI - Version](https://img.shields.io/pypi/v/yaml_to_disk)](https://pypi.org/project/yaml_to_disk/)
![python](https://img.shields.io/badge/-Python_3.12-blue?logo=python&logoColor=white)
[![codecov](https://codecov.io/gh/mmcdermott/yaml_to_disk/graph/badge.svg?token=5RORKQOZF9)](https://codecov.io/gh/mmcdermott/yaml_to_disk)
[![tests](https://github.com/mmcdermott/yaml_to_disk/actions/workflows/tests.yaml/badge.svg)](https://github.com/mmcdermott/yaml_to_disk/actions/workflows/tests.yaml)
[![code-quality](https://github.com/mmcdermott/yaml_to_disk/actions/workflows/code-quality-main.yaml/badge.svg)](https://github.com/mmcdermott/yaml_to_disk/actions/workflows/code-quality-main.yaml)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/mmcdermott/yaml_to_disk#license)
[![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/mmcdermott/yaml_to_disk/pulls)
[![contributors](https://img.shields.io/github/contributors/mmcdermott/yaml_to_disk.svg)](https://github.com/mmcdermott/yaml_to_disk/graphs/contributors)

A simple tool to let you define a directory structure in yaml form, then populate it on disk in a single
command. Highly useful for simplifying test case setup, espically in doctest settings where readability is
critical.

## 1. Installation

```bash
pip install yaml_to_disk
```

If you plan on using the Parquet functionality, install the optional
`pyarrow` dependency with:

```bash
pip install "yaml_to_disk[parquet]"
```

If you want to work with TOML files, install the optional `tomli-w`
dependency:

```bash
pip install "yaml_to_disk[toml]"
```

## 2. Usage

To use, you simply define a yaml representation of the files you want to populate, then call the function.
E.g.,

```python
>>> from yaml_to_disk import yaml_disk
>>> target_contents = '''
... dir1:
...   "sub1.txt/":
...     file1.txt: "Hello, World!"
...   sub2:
...     cfg.yaml: {"foo": "bar"}
...     data.csv: |-2
...       a,b,c
...       1,2,3
... a.json:
...   - key1: value1
...     key2: value2
...   - str_element
... '''
>>> with yaml_disk(target_contents) as root_path:
...     print_directory(root_path)
...     print("---------------------")
...     print(f"file1.txt contents: {(root_path / 'dir1' / 'sub1.txt' / 'file1.txt').read_text()}")
...     print(f"a.json contents: {(root_path / 'a.json').read_text()}")
...     print("cfg.yaml contents:")
...     print((root_path / 'dir1' / 'sub2' / 'cfg.yaml').read_text().strip())
...     print("data.csv contents:")
...     print((root_path / 'dir1' / 'sub2' / 'data.csv').read_text().strip())
├── a.json
└── dir1
    ├── sub1.txt
    │   └── file1.txt
    └── sub2
        ├── cfg.yaml
        └── data.csv
---------------------
file1.txt contents: Hello, World!
a.json contents: [{"key1": "value1", "key2": "value2"}, "str_element"]
cfg.yaml contents:
foo: bar
data.csv contents:
a,b,c
1,2,3

```

You can also pass a filepath that contains the target yaml on disk, or a parsed view of the yaml contents
(e.g., as a dictionary or a list):

```python
>>> with tempfile.TemporaryDirectory() as temp_dir:
...     yaml_path = Path(temp_dir) / "target.yaml"
...     _ = yaml_path.write_text(target_contents)
...     with yaml_disk(yaml_path) as root_path:
...         print_directory(root_path)
├── a.json
└── dir1
    ├── sub1.txt
    │   └── file1.txt
    └── sub2
        ├── cfg.yaml
        └── data.csv
>>> as_list = ["foo.png"] # Note that this will only make an empty file with this name
>>> with yaml_disk(as_list) as root_path:
...     print_directory(root_path)
└── foo.png
>>> as_dict = {"foo.pkl": {"bar": "baz"}}
>>> import pickle
>>> with yaml_disk(as_dict) as root_path:
...     print_directory(root_path)
...     print("----------------------")
...     with open(root_path / "foo.pkl", "rb") as f:
...         print(f"foo.pkl contents: {pickle.load(f)}")
└── foo.pkl
----------------------
foo.pkl contents: {'bar': 'baz'}

```

### YAML Syntax

The
YAML syntax specifies a list or ordered dictionaries of nested files and directories. In list form, a plain
string list entry is either a file name (if it does not end in `/`) or a directory name (if it does end in
`/`), and the file (or directory) will be created at the requisite location. If the entry is a dictionary, it
must have a single key, which is the file (or directory) name, and the value is either the file contents (in
various representations) or the nested directory contents. In this syntax, directories are not required to end
in `/`, as file contents can only be added to files with extensions so that the package knows how to format
them.

```yaml
DIR_NAME:
  SUB_DIR_NAME:
    - FILE_NAME.EXT: FILE_CONTENT
    - FILE_NAME.EXT # No contents, just an empty file
    - SUB_DIR_NAME/ # No contents, just an empty directory
  SUB_DIR_NAME:
    FILE_NAME.EXT: FILE_CONTENT # Can also use a dictionary representation rather than a list if suitable
```

### Supported Extensions:

| Extension    | Description     | Accepts?                                                        | Write Method                                       |
| ------------ | --------------- | --------------------------------------------------------------- | -------------------------------------------------- |
| `txt`        | Plain text file | Plain strings                                                   | Written as is                                      |
| `json`       | JSON file       | Any JSON compatible object                                      | Written via `json.dump`                            |
| `yaml`,`yml` | YAML file       | Any YAML compatible object                                      | Written via `yaml.dump`                            |
| `pkl`        | Pickle file     | Any pickle serializable                                         | Written via `pickle.dump`                          |
| `csv`        | CSV file        | CSV data in either string, column-map, or a list of rows format | See [`CSVFile`](src/file_types/csv.py) for details |
| `tsv`        | TSV file        | TSV data in same formats as CSV                                 | See [`TSVFile`](src/file_types/tsv.py) for details |
| `parquet`    | Parquet file    | `pyarrow.Table`, column-map, or list of row maps                | Written via `pyarrow.parquet.write_table`          |
| `toml`       | TOML file       | Any TOML compatible object                                      | Written via `tomli_w.dumps`                        |

Other extensions can be used, but only in the empty files mode.

#### Adding new extensions:

You can easily add your own file extensions to be supported in your custom python packages by simply
subclassing the [`FileType`](src/file_types/base.py) abstract base class and implementing the necessary
methods and class variables. Then, you can register it as a supported extension by adding an entry point to
your `pyproject.toml` file, like this:

```toml
[project.entry-points."yaml_to_disk.file_types"]
txt = "yaml_to_disk.file_types.txt:TextFile"
json = "yaml_to_disk.file_types.json:JSONFile"
pkl = "yaml_to_disk.file_types.pkl:PickleFile"
yaml = "yaml_to_disk.file_types.yaml:YAMLFile"
csv = "yaml_to_disk.file_types.csv:CSVFile"
tsv = "yaml_to_disk.file_types.tsv:TSVFile"
parquet = "yaml_to_disk.file_types.parquet:ParquetFile"
toml = "yaml_to_disk.file_types.toml:TOMLFile"
```

Then, the system will automatically know how to match and use your new file type. Note that you cannot
overwrite existing file extensions in this way; instead, if an overwrite is attempted, upon the load of all
registered file types, an error will be raised.

Note that you can set all non-recognized extensions with string values to be treadted as `.txt` files via the
class variable `YamlDisk._USE_TXT_ON_UNK_STR_FILES`, which is `True` by default or by passing the keyword
argument `use_txt_on_unk_str_files` to the `yaml_disk` function. For example:

```python
>>> unk_file_contents_str = '''
... file1.txt: "Hello, World!"
... file2.md: "# Hello, World!"
... '''
>>> with yaml_disk(unk_file_contents_str) as root_path:
...     print_directory(root_path)
...     print("---------------------")
...     print(f"file1.txt contents: {(root_path / 'file1.txt').read_text()}")
...     print(f"file2.md contents: {(root_path / 'file2.md').read_text()}")
├── file1.txt
└── file2.md
---------------------
file1.txt contents: Hello, World!
file2.md contents: # Hello, World!
>>> with yaml_disk(unk_file_contents_str, use_txt_on_unk_str_files=False) as root_path:
...     pass # An error will be thrown
Traceback (most recent call last):
  ...
ValueError: No file type found for .md
>>> unk_file_contents_not_str = '''
... file1.txt: "Hello, World!"
... file2.pdf: [["a", "b", "c"], ["1", "2", "3"]]
... '''
>>> with yaml_disk(unk_file_contents_not_str, use_txt_on_unk_str_files=True) as root_path:
...     pass # An error will be thrown as the contents aren't string
Traceback (most recent call last):
  ...
ValueError: No file type found for .pdf

```
