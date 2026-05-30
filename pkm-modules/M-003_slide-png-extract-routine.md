---
type: pkm-module
id: M-003
title: 강의 영상 슬라이드 PNG 추출 루틴
domain: [lecture-note, video-frame, obsidian]
task_type: workflow
input: "강의 MP4 + lecture_transcribe.py 가 만든 녹취록 TXT + 추출할 슬라이드 번호 목록 (선택)"
output: "Obsidian Vault/0. Inbox/Files/<prefix>_pXX.png (1280×720 등 원본 해상도)"
related_command: ""
related_spec: ""
related_agent: ""
created: 2026-05-07
updated: 2026-05-07
---

# M-003 — 강의 영상 슬라이드 PNG 추출 루틴

> **재사용 목적**: 강의노트 본문에서 `![[ID_WN_pXX.png|560]]` 로 임베드할 슬라이드 이미지를 mp4에서 추출. 강사 라이브 마크업·필기·구두 보충 등 **PDF 강의자료에는 없고 영상에만 있는 정보**가 필요할 때 사용.

## 사용 판단 기준

- **PDF 강의자료만으로 충분한 경우 → 이 모듈 미사용**
- 다음 중 하나라도 해당하면 사용:
  - 강사가 강의 중 슬라이드 위에 펜으로 강조·보충 표시를 함
  - 슬라이드에는 없고 영상에서만 보이는 텍스트(쪽 슬라이드, 별도 화면 공유 등)가 있음
  - 노트의 시각적 anchor 로 슬라이드 이미지가 필요한데 PDF 의 해당 페이지가 슬라이드와 1:1 매칭이 안 됨
  - 4/30 ID 4주차 노트의 ID_W4 시리즈처럼 강의별 슬라이드 갤러리를 갖추고 싶음

## 트리거

- 자연어: "5/7 강의 슬라이드 PNG 추출해줘", "노트의 placeholder 슬라이드를 영상에서 캡처해줘"

## 사전 조건

1. M-002 (강의 녹취록 생성 루틴) 완료 — 녹취록 TXT 가 있어야 슬라이드 시작 시각을 파싱할 수 있음
2. 강의노트가 이미 작성되어 있고 본문에 `![[<prefix>_p<번호>.png]]` placeholder 가 있음 (또는 모든 슬라이드 일괄 추출)

## 단계 요약

| Step | 작업 |
|------|------|
| 1 | 노트에서 참조 슬라이드 번호 grep (`grep -oE "<prefix>_p\d+"` ) 또는 "all" 결정 |
| 2 | `extract_slide_pngs.py` 실행 (전경 OK — 18장 기준 수십 초 소요) |
| 3 | `find` 또는 `ls` 로 출력 PNG 개수 검증 |
| 4 | 노트 본문에서 자동 렌더링 확인 (Obsidian 기본 검색 경로가 `0. Inbox/Files/` 포함) |

## 스크립트 실행 명령

```bash
python "$PROJECT_ROOT/.claude/scripts/extract_slide_pngs.py" \
  "<mp4_경로>" \
  --transcript "<녹취록_경로>" \
  --out "$VAULT/0. Inbox/Files" \
  --prefix ID_W5 \
  --slides 4,7,10,14,15,16,20,23,26,27,33,35,38,50,58,60,65,66 \
  --offset 2.0
```

`--slides all` 로 모든 슬라이드 일괄 추출도 가능.

## 파라미터 가이드

| 파라미터 | 권장값 | 근거 |
|---------|-------|------|
| `--prefix` | `ID_WN` | 4/30 노트 `ID_W4`, 5/7 노트 `ID_W5` 등 회차별 식별자. 강의 간 충돌 회피 |
| `--offset` | `2.0` | 슬라이드 전환 직후의 잔상·애니메이션 회피. 1초 미만이면 전환 중 프레임 캡처 가능성 |
| `--slides` | (노트가 참조하는 번호만) | 71개 모두 추출하면 Vault 용량·동기화 시간 증가. 강의노트가 임베드한 번호만 추출 권장 |
| `--out` | `Obsidian Vault/0. Inbox/Files` | 4/30 노트의 ID_W4 시리즈와 동일 위치. Obsidian 기본 검색 경로 |

## 노트 참조 슬라이드 번호 추출 예

본문에 임베드 placeholder 가 이미 있을 때 (5/7 노트 사례):

```bash
# 노트에서 ID_W5_pXX 번호 추출 (정렬, 중복 제거)
grep -oE "ID_W5_p\d+" "<강의노트.md>" | sort -u
# 또는 위 grep 결과를 콤마 구분 문자열로 변환
grep -oE "ID_W5_p\d+" "<강의노트.md>" | sort -u | sed 's/ID_W5_p0*//' | paste -sd,
```

## 기술 노트 — Windows + 한글 경로 imwrite 우회

`cv2.imwrite("...한글_경로.../foo.png", frame)` 는 Windows 환경에서 **에러 없이 조용히 실패**한다 (파일이 생성되지 않음). 본 스크립트는 다음 우회를 사용:

```python
ok, buf = cv2.imencode(".png", frame)
out_path.write_bytes(buf.tobytes())   # Python 표준 IO 는 한글 경로 OK
```

향후 Linux/macOS 로 환경이 바뀌어도 동일하게 동작하므로 그대로 유지 권장.

## 슬라이드 시작 시각 파싱 형식

녹취록 TXT 의 라인:
```
━━━ 【スライド 60】 01:10:39 ━━━
━━━ 【スライド 4】 02:33 ━━━
```
정규식: `スライド\s*(\d+)】\s*(?:(\d+):)?(\d+):(\d+)`
HH:MM:SS 와 MM:SS 모두 지원.

## 검증 체크리스트

추출 후 다음 확인:
- [x] 출력 디렉토리에 PNG 파일 개수 = 요청 슬라이드 개수 ✅ 2026-05-08
- [x] PNG 1~2장을 직접 열어 (Read 도구 또는 Obsidian 미리보기) 깨진 프레임·전환 중 잔상 없는지 확인 ✅ 2026-05-08
- [x] Obsidian 노트에서 `![[<prefix>_pXX.png]]` 가 자동 렌더링되는지 확인 (Vault 동기화 후) ✅ 2026-05-08

## 토큰 예산

| 단계 | tool calls | 비용 |
|------|-----------|------|
| 노트에서 슬라이드 번호 추출 | 1 (grep) | 최소 |
| 스크립트 실행 | 1 (Bash) | 최소 |
| 결과 검증 | 1~2 (find + Read) | 작음 |
| **합계** | **3~4** | **~2K tokens** |

## 다음 단계

추출 완료 후 노트 본문이 자동 렌더링되므로 별도 후속 작업은 보통 불필요.
필요 시 사용자가 노트를 검토하면서 추가 슬라이드 번호 요청 → 같은 명령에서 `--slides` 만 변경하여 재실행.

## 트러블슈팅

| 증상 | 원인 후보 | 대응 |
|------|---------|------|
| `[skip] slide N: no timestamp in transcript` | 녹취록 슬라이드 감지가 N 번을 잡지 못함 (cooldown 초과 등) | 녹취록 직접 확인 후 인접 슬라이드 번호로 대체, 또는 lecture_transcribe.py 를 `--cooldown 15` 로 재생성 |
| 모든 PNG 생성 후에도 Obsidian 에서 안 보임 | OneDrive 동기화 지연 또는 Obsidian Vault 캐시 | 30 초 대기 후 Obsidian 재시작 |
| 추출된 프레임이 이전 슬라이드 잔상 | offset 이 너무 짧음 | `--offset 3.0` 또는 `4.0` 으로 재시도 |
