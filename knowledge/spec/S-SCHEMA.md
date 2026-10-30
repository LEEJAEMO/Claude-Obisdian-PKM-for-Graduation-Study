# S-SCHEMA — 지식 카드와 검증 상태 규격

적용: schema catalog id source provenance verification hash spec

비대상: 과거 문서의 metadata를 현재 재현 성공으로 승격하지 않는다

출처 ID: note-properties, AI-proposal. 일반화·재작성: 2026-10-30.
검증 수준: 원문 대조한 설계; 새 과제에서의 효능은 미검증.

catalog.json의 필드: id, title, kind, path, when, avoid, source_ids, verification, sha256. kind는 module/troubleshooting/spec 중 하나다. 경로는 배포본 knowledge/ 안의 Markdown으로 제한한다.

source_ids는 원래 PKM 또는 설계 출처를 식별한다. 개인 원문은 배포하지 않으며 이 카드는 새로 일반화한 별도 문서다. verification=adapted-source-reviewed는 원문 대조·일반화를 뜻하며 이 업무의 성공을 실증했다는 뜻이 아니다.

검증 기록은 별도 실행 명령·환경·실제 결과로 남긴다. knowledge 파일 변경 후 sha256 불일치 시 읽기를 중단한다. 해시는 우발적 변경 탐지이며 악의적으로 재작성한 catalog의 진위를 보장하지 않는다. 고정 Git commit과 함께 확인한다.
