"""
Zotero 라이브러리 무결성 점검 + SI 오염 탐지.

용법:
  python zotero_audit.py           # 점검만
  python zotero_audit.py --fix     # 자동 수정 (CrossRef 조회)
"""
import sys
import os
import re
import json

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import requests
from pyzotero import zotero

ZOT_ID = "20128584"
ZOT_KEY = "3vBPrrUl9w2gtM94iNC5IaAe"
FIX = "--fix" in sys.argv

zot = zotero.Zotero(ZOT_ID, "user", ZOT_KEY)


def fetch_crossref(doi: str) -> dict | None:
    try:
        r = requests.get(
            f"https://api.crossref.org/works/{doi}",
            headers={"User-Agent": "zotero-audit/1.0"},
            timeout=10,
        )
        if r.status_code != 200:
            return None
        return r.json().get("message")
    except Exception as e:
        print(f"    CrossRef 오류: {e}")
        return None


def update_from_crossref(item, cr: dict):
    d = item["data"]
    # title
    if cr.get("title"):
        d["title"] = cr["title"][0]
    # abstract
    if cr.get("abstract"):
        abs_clean = re.sub(r"<[^>]+>", "", cr["abstract"])
        d["abstractNote"] = abs_clean.strip()
    # authors
    if cr.get("author"):
        d["creators"] = [
            {
                "creatorType": "author",
                "firstName": a.get("given", ""),
                "lastName": a.get("family", ""),
            }
            for a in cr["author"]
        ]
    # journal
    if cr.get("container-title"):
        d["publicationTitle"] = cr["container-title"][0]
    # volume/issue/pages
    if cr.get("volume"):
        d["volume"] = cr["volume"]
    if cr.get("issue"):
        d["issue"] = cr["issue"]
    if cr.get("page"):
        d["pages"] = cr["page"]
    # date
    if cr.get("published-print") or cr.get("published-online"):
        pub = cr.get("published-print") or cr.get("published-online")
        parts = pub.get("date-parts", [[]])[0]
        d["date"] = "-".join(str(x) for x in parts)
    zot.update_item(item)


# ============================================================
# 1. 전체 논문 가져오기
# ============================================================
print("=== Zotero 라이브러리 점검 ===\n")
all_items = zot.everything(zot.items())
papers = [
    i for i in all_items if i["data"].get("itemType") == "journalArticle"
]
print(f"논문 수: {len(papers)}\n")

# ============================================================
# 2. SI / Supplementary 오염 탐지
# ============================================================
print("--- 제목 오염 검사 (SI / Supplementary) ---")
si_suspects = []
for item in papers:
    title = item["data"].get("title", "")
    if re.search(r"\b(SI|SM|Supplementary|Supporting Info)\b", title):
        si_suspects.append(item)
        key = item["key"]
        print(f"  ⚠ [{key}] {title}")

if not si_suspects:
    print("  (정상)")
print()

# ============================================================
# 3. 메타데이터 누락 검사
# ============================================================
print("--- 메타데이터 누락 검사 ---")
missing = []
for item in papers:
    d = item["data"]
    problems = []
    if not d.get("title"):
        problems.append("title")
    if not d.get("creators"):
        problems.append("authors")
    if not d.get("date"):
        problems.append("date")
    if not d.get("publicationTitle") and d.get("itemType") == "journalArticle":
        problems.append("journal")
    if not d.get("DOI"):
        problems.append("DOI")
    if problems:
        missing.append((item, problems))
        print(f"  ⚠ [{item['key']}] {d.get('title','(제목없음)')[:50]}")
        print(f"      누락: {', '.join(problems)}")
if not missing:
    print("  (정상)")
print()

# ============================================================
# 4. 중복 탐지
# ============================================================
print("--- 중복 탐지 (title + year) ---")
seen = {}
dups = []
for item in papers:
    d = item["data"]
    title = (d.get("title", "") or "").lower().strip()
    year = (d.get("date", "") or "")[:4]
    sig = f"{title[:40]}_{year}"
    if sig in seen:
        dups.append((seen[sig], item))
        print(f"  ⚠ 중복: {d.get('title','')[:50]}")
        print(f"      [{seen[sig]['key']}] <-> [{item['key']}]")
    else:
        seen[sig] = item
if not dups:
    print("  (정상)")
print()

# ============================================================
# 5. --fix 모드: SI 오염 자동 수정
# ============================================================
if FIX and si_suspects:
    print("=== --fix 모드: SI 오염 자동 수정 ===")
    for item in si_suspects:
        d = item["data"]
        doi = d.get("DOI", "")
        key = item["key"]
        title = d.get("title", "")
        print(f"\n  [{key}] {title[:60]}")
        if not doi:
            print(f"    DOI 없음 - 수동 수정 필요")
            continue
        print(f"    DOI: {doi}")
        cr = fetch_crossref(doi)
        if not cr:
            print(f"    CrossRef 조회 실패 - 수동 수정 필요")
            continue
        new_title = cr.get("title", [""])[0]
        if new_title == title:
            print(f"    CrossRef가 같은 제목을 반환 - 스킵")
            continue
        print(f"    -> {new_title[:70]}")
        update_from_crossref(item, cr)
        print(f"    ✓ 업데이트 완료")

    print(
        "\n[참고] BBT citekey는 Zotero 데스크톱에서 "
        "Refresh BibTeX Key를 눌러야 재생성됩니다."
    )
