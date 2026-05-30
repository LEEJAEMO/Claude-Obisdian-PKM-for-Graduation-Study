# Zotero 자동화 설정

## 1. Citekey 자동 생성 (BBT Postscript)

### 설치 순서

1. Zotero 데스크톱 열기
2. `Edit` → `Preferences` → `Better BibTeX` 클릭
3. 상단 탭에서 **`Citation keys`** 선택
4. **Formula** 필드 확인:
   - 기본값이 `auth.lower + year` 또는 유사한 형태여야 함
   - `authEtal + year` 로 설정 권장 (AuthorEtAlYear 형식 생성)
5. 하단 **`Postscript`** 영역에 `bbt-postscript.js` 파일 내용 **전체 붙여넣기**
6. `OK` 클릭

### 적용 확인

설치 후 Zotero에 새 논문을 추가하면 citekey가 자동으로 아래 형식이 됨:

```
HayashiEtAl2023_Observation of long-range orbital transport and (CommunPhys)
```

기존 논문도 citekey를 재생성하려면:
- 전체 선택 → 우클릭 → `Better BibTeX` → `Refresh BibTeX key`

### 저널 약칭 추가

새로운 저널을 등록하려면 `bbt-postscript.js`의 `journalMap` 객체에 한 줄 추가:

```javascript
"New Journal Name": "NewJAbbr",
```

수정 후 Zotero Preferences에서 다시 붙여넣기.

---

## 2. 파일 구조

```
.claude/zotero/
├── README.md              ← 이 파일
└── bbt-postscript.js      ← BBT Postscript 코드
```

---

## 3. 관련 Claude 명령어

- `/zotero-add [DOI/arXiv/제목]` — 논문 검색·중복 확인 후 Zotero에 추가
- `/paper-review [파일/arXiv]` — Zotero 노트에 읽기 전/후 분석 작성
