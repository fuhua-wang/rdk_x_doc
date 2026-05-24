#!/usr/bin/env python3
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
PARTS = [ROOT / f"scripts/ptq_part{i}_en.md" for i in range(1, 5)]
DST = (
    ROOT
    / "i18n/en/docusaurus-plugin-content-docs/current/07_Advanced_development/04_toolchain_development/intermediate/ptq_process.md"
)

content = "".join(p.read_text(encoding="utf-8") for p in PARTS)
content = content.replace(":::note Note", ":::info Note")

DST.write_text(content, encoding="utf-8")

cn = len(re.findall(r"[\u4e00-\u9fff]", content))
lines = content.count("\n") + (1 if content and not content.endswith("\n") else 0)
print(f"Written: {DST}")
print(f"Lines: {lines}")
print(f"Remaining Chinese chars: {cn}")
for i, p in enumerate(PARTS, 1):
    text = p.read_text(encoding="utf-8")
    print(f"Part {i}: {p.stat().st_size} bytes, {text.count(chr(10)) + 1} lines")
