# S-ENV — 환경 명세와 즉시 대안

적용: environment MCP stdio python 설치 setup spec offline fallback

비대상: 차단된 설정·접속 경로·업로드 제한을 우회하지 않는다

출처 ID: Specs-index, AI-proposal. 일반화·재작성: 2026-10-30.
검증 수준: 원문 대조한 설계; 새 과제에서의 효능은 미검증.

필수 환경은 Python 3.10 이상뿐이다. API 키, 외부 AI, 데이터베이스, 벡터 서비스, pip 설치는 필요하지 않다. 다운로드 뒤 조회 도구는 네트워크에 접속하지 않는다.

MCP는 tools-only stdio, protocol 2025-11-25, pkm_search와 pkm_read 두 도구를 제공한다. HTTP 원격 서버·파일 쓰기·셸 실행·화면 자동 조작 기능은 제공하지 않는다.

시험 환경에서 MCP 등록이 지원되지 않거나 바로 성공하지 않으면 kit.py CLI를 사용한다. Python도 없다면 START_HERE.md와 knowledge/를 파일로 읽는다. 읽기 도구 자체는 추가 파일을 만들지 않지만 Python은 기본적으로 캐시를 만들 수 있으므로 -B 또는 PYTHONDONTWRITEBYTECODE=1을 사용한다.
