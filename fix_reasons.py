import json

with open("data/2026-03-06.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("bad_reasons.txt", "w", encoding="utf-8") as out:
    for item in data.get("signals", []):
        short_reason = item.get("short_reason", "")
        summary = item.get("summary", "")
        
        needs_fix = False
        if "," in short_reason: needs_fix = True
        if "시장 흐름 및 관련 테마 분석" in short_reason or "시장 흐름 및 관련 테마 분석" in summary: needs_fix = True
        if "상승 마감했습니다" in summary or "하락 마감했습니다" in summary: needs_fix = True
        
        if needs_fix:
            out.write(f"ID: {item['id']}\n")
            out.write(f"OLD: {short_reason}\n")
            out.write(f"SUMMARY: {summary}\n\n")
