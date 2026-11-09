
from langchain.tools import tool


def is_table_row(line):
    return "|" in line and len(line.split("|")) >= 2


def is_separator_row(line):
    """Identify Markdown table separator rows, such as |---|---|."""

    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]

    return bool(cells) and all(
        cell and all(char in "-:" for char in cell)
        for cell in cells
    )


def extract_table_rows(text):
    lines = text.split("\n")

    tables = []
    current_table = []

    for line in lines:

        if is_separator_row(line):
            continue

        if is_table_row(line):
            current_table.append(line)

        else:
            if len(current_table) >= 2:
                tables.append(current_table)

            current_table = []

    if len(current_table) >= 2:
        tables.append(current_table)

    return tables


def convert_table(table_lines, metadata=None):

    rows = []

    for line in table_lines:
        cells = [
            cell.strip()
            for cell in line.strip().strip("|").split("|")
        ]

        rows.append(cells)

    headers = rows[0]
    data = []

    for row in rows[1:]:

        if len(row) != len(headers):
            continue

        data.append(dict(zip(headers, row)))

    return {
        "columns": headers,
        "rows": data,
        "source": metadata.get("source") if metadata else None,
        "page": metadata.get("page") if metadata else None,
        "section": metadata.get("section") if metadata else None,
        "chunk_id": metadata.get("chunk_id") if metadata else None
    }


def extract_tables(text, metadata=None):

    table_lines = extract_table_rows(text)

    return [
        convert_table(table, metadata)
        for table in table_lines
    ]


def extract_tables_from_evidence(evidence):

    all_tables = []

    for item in evidence:

        tables = extract_tables(
            text=item.get("text", ""),
            metadata=item
        )

        all_tables.extend(tables)

    return all_tables


@tool
def table_extractor_tool(
    text: str,
    source: str = "",
    page: int = 0,
    section: str = "",
    chunk_id: str = ""
) -> list[dict]:
    """
    Extract structured tables from retrieved document text.

    Identifies pipe-separated tables, extracts their columns
    and rows, and preserves document source information.
    """

    metadata = {
        "source": source,
        "page": page if page != 0 else None,
        "section": section,
        "chunk_id": chunk_id
    }

    return extract_tables(text, metadata)
