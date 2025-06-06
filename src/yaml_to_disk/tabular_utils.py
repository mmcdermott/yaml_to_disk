from __future__ import annotations

from typing import Any


def validate_column_map(column_map: dict[str, list[Any]]) -> None:
    """Validate a mapping of column names to column values."""
    if not column_map:
        return

    bad_keys = [f"{k} ({type(k).__name__})" for k in column_map if not isinstance(k, str)]
    if bad_keys:
        raise ValueError(f"Column-maps must have all string keys; got {', '.join(bad_keys)}")

    bad_keys = [f"{k} ({type(v).__name__})" for k, v in column_map.items() if not isinstance(v, list)]
    if bad_keys:
        raise ValueError(f"Column-maps must have all list values; got cols {', '.join(bad_keys)}")

    N = len(next(iter(column_map.values())))
    bad_keys = [f"{k} ({len(v)})" for k, v in column_map.items() if len(v) != N]
    if bad_keys:
        bad_keys_str = ", ".join(bad_keys)
        raise ValueError(f"Column-maps must have all lists of the same length {N}; got {bad_keys_str}")


def validate_row_map_list(rows: list[dict[str, Any]]) -> list[str]:
    """Validate a list of row dictionaries and return the field names."""
    if not rows:
        return []

    bad_keys = [k for k in rows[0] if not isinstance(k, str)]
    if bad_keys:
        raise ValueError(f"Column-maps must have all string keys; got {bad_keys}")

    fieldnames = list(rows[0].keys())

    bad_rows = []
    for i, row in enumerate(rows):
        missing_keys = set(fieldnames) - set(row.keys())
        extra_keys = set(row.keys()) - set(fieldnames)

        err_parts = []
        if extra_keys:
            err_parts.append(f"extra keys {sorted(extra_keys)}")
        if missing_keys:
            err_parts.append(f"missing keys {sorted(missing_keys)}")

        if err_parts:
            bad_rows.append(f"Row {i} has {', '.join(err_parts)}")

    if bad_rows:
        bad_rows_str = "\n".join(bad_rows)
        raise ValueError(f"Row-maps must be consistent; got\n{bad_rows_str}")

    return fieldnames
