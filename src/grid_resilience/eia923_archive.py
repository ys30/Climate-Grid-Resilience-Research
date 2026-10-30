"""Inspect the *original* EIA-923 archive before any data transformation.

Fail closed: no inferred worksheet schema, no claims of authenticated source.
This tool reads a local ZIP only. It never downloads or executes archive items.
"""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path

def inspect_archive(archive, output, source_url):
    path = Path(archive)
    if not path.is_file() or not zipfile.is_zipfile(path):
        raise ValueError("Missing or invalid EIA-923 ZIP")
    if not source_url.startswith("https://www.eia.gov/"):
        raise ValueError("Official EIA source URL required")
    files = []
    with zipfile.ZipFile(path) as z:
        for member in z.infolist():
            name = member.filename
            if member.flag_bits & 1:
                raise ValueError("Encrypted archive entry unsupported")
            if name.startswith("/") or ".." in Path(name).parts:
                raise ValueError("Unsafe archive member path")
            if not member.is_dir():
                files.append({
                    "path": name,
                    "bytes_uncompressed": member.file_size,
                    "crc32": format(member.CRC, "08x"),
                })
    workbooks = [x for x in files if x["path"].lower().endswith((".xlsx", ".xls", ".xlsm"))]
    if not workbooks:
        raise ValueError("No Excel workbooks in archive")
    manifest = {
        "source_url_declared_not_authenticated": source_url,
        "archive_name": path.name,
        "archive_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "archive_size_bytes": path.stat().st_size,
        "workbook_count": len(workbooks),
        "workbooks": workbooks,
        "all_entries": files,
        "generation_data_extracted": False,
        "historical_calibration_certified": False,
        "next_step": "Inspect Schedule 3A/5A worksheet headers, units, missing-value and reporting conventions before an explicit column mapping.",
    }
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--source-url", default="https://www.eia.gov/electricity/data/eia923/archive/xls/f923_2024.zip")
    a=p.parse_args()
    print(json.dumps(inspect_archive(a.archive,a.output,a.source_url),indent=2))

if __name__=="__main__":
    main()
