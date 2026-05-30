---
description: Vault 안전 이동/rename — wikilink 갱신 + 정리로그 자동 생성
argument-hint: "[작업명] [src] [dst]"
---

# /safe-move — 파일 이동/rename 안전 도구

Vault 내부 `.md` 파일 이동·rename·삭제 시 사용. `scripts/safe_move.py`의 래퍼.

## 사용 패턴

```
/safe-move <작업명>
```

그러면 AI가:
1. 사용자에게 moves.csv에 기록할 행들을 받거나 제안 생성
2. 임시 CSV 저장 후 `safe_move.py --name <작업명> --moves <csv>` 로 **드라이런**
3. 결과(시뮬레이션)를 사용자에게 보이고 승인 요청
4. 승인 시 `--apply` 추가해 재실행
5. 생성된 `moves.csv`, `summary.md`의 **절대 경로**를 보고

## 구현 지시 (AI에게)

```bash
PYTHONUTF8=1 python "$PROJECT_ROOT\scripts\safe_move.py" \
  --name "<$1>" \
  --moves "<임시 CSV 경로>"
# 승인 시 --apply 추가
```

### CSV 형식
```csv
src,dst,kind,reason
<절대경로>,<절대경로>,<dir|file>,<사유>
```
- 삭제 시 `dst`를 `TRASH`로 기재 → 스크립트가 `~/.Trash/<이름>`으로 이동
- 상세: `14. Specs/environment/safe-move-rules.md`

## 반드시 지킬 것

- **드라이런 없이 --apply 바로 실행 금지**
- 사용자 승인 전 절대 파일 건드리지 않음
- 보고에 **moves.csv / summary.md 절대 경로 필수**
