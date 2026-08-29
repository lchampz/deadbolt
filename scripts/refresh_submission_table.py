"""Reescreve a tabela de resultados dentro de SUBMISSION.md a partir de eval/report.py.

Existe para que a tabela do documento do juiz não possa divergir dos números
medidos. Nunca edite aquele bloco à mão.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "SUBMISSION.md"
BEGIN, END = "<!-- BEGIN REPORT TABLE -->", "<!-- END REPORT TABLE -->"

table = subprocess.run(
    [sys.executable, str(ROOT / "eval" / "report.py")],
    capture_output=True, text=True, check=True, cwd=ROOT,
).stdout.strip()

text = DOC.read_text()
if BEGIN not in text or END not in text:
    sys.exit(f"marcadores ausentes em {DOC.name}")

new = f"{BEGIN}\n```\n{table}\n```\n{END}"
DOC.write_text(re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: new, text, flags=re.S))
print(f"tabela de {DOC.name} atualizada ({len(table.splitlines())} linhas)")
