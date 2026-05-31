import io
from pathlib import PurePosixPath

import pandas as pd


def _display_filename(filename: str | None, default: str = "list.csv") -> str:
    name = (filename or default).strip()
    return PurePosixPath(name).name or default


def read_recipient_file(contents: bytes, filename: str | None) -> pd.DataFrame:
    """Parse uploaded CSV/Excel; keeps every column from the first sheet."""
    name = _display_filename(filename)
    lower = name.lower()

    if lower.endswith(".csv"):
        try:
            text = contents.decode("utf-8")
        except UnicodeDecodeError:
            text = contents.decode("latin-1")
        return pd.read_csv(io.StringIO(text), dtype=object, keep_default_na=False)

    if lower.endswith(".xlsx"):
        return pd.read_excel(
            io.BytesIO(contents),
            sheet_name=0,
            dtype=object,
            keep_default_na=False,
            engine="openpyxl",
        )

    if lower.endswith(".xls"):
        return pd.read_excel(
            io.BytesIO(contents),
            sheet_name=0,
            dtype=object,
            keep_default_na=False,
        )

    raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")


def build_full_data_archive(data: pd.DataFrame, filename: str | None) -> tuple[bytes, str]:
    """
    Serialize the entire parsed sheet (all columns, all rows) for Cloudinary storage.
    """
    name = _display_filename(filename)
    lower = name.lower()
    stem = PurePosixPath(name).stem or "recipients"

    if lower.endswith((".xls", ".xlsx")):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            data.to_excel(writer, index=False, sheet_name="Recipients")
        return buffer.getvalue(), f"{stem}.xlsx"

    csv_text = data.to_csv(index=False)
    return csv_text.encode("utf-8-sig"), f"{stem}.csv"


def build_storage_files(
    data: pd.DataFrame, original_contents: bytes, filename: str | None
) -> list[tuple[bytes, str]]:
    """
    Files to archive on Cloudinary:
    - Excel: original workbook (all sheets) + normalized copy of sheet 1 with every column
    - CSV: original file + normalized copy (same data, explicit full export)
    """
    name = _display_filename(filename)
    lower = name.lower()
    full_bytes, full_name = build_full_data_archive(data, filename)
    files: list[tuple[bytes, str]] = [(full_bytes, full_name)]

    if lower.endswith((".xls", ".xlsx")):
        files.insert(0, (original_contents, name))

    elif lower.endswith(".csv"):
        files.insert(0, (original_contents, name))

    return files
