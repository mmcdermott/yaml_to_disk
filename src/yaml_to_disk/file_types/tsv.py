from typing import ClassVar

from .csv import CSVFile


class TSVFile(CSVFile):
    """A class for validating and writing tab-separated-value (TSV) files.

    Examples:
        >>> column_map_data = {
        ...     "Name": ["Alice", "Bob"],
        ...     "Age": [30, 25],
        ... }
        >>> with tempfile.NamedTemporaryFile() as tmp_file:
        ...     fp = Path(tmp_file.name)
        ...     TSVFile.write(fp, column_map_data)
        ...     print(fp.read_text().strip())
        Name\tAge
        Alice\t30
        Bob\t25

    ``TSVFile.matches`` can detect ``.tsv`` file names:

        >>> from pathlib import Path
        >>> TSVFile.matches(Path('foo.tsv'))
        True
        >>> TSVFile.matches(Path('foo.txt'))
        False
    """

    extension: ClassVar[str] = ".tsv"
    separator: ClassVar[str] = "\t"
