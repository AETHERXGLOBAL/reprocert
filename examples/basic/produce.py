import json
from pathlib import Path

values = [8, 13, 21, 34, 55]
result = {"records_processed": len(values), "sum": sum(values), "max": max(values)}
Path("result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result))
