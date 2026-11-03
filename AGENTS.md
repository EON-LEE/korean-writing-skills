# 저장소 작업 규칙

- Copilot 앱과 기본 `gh` 계정은 `eonlee_MSDEMO`를 사용한다.
- Git fetch와 push에는 기존 EON-LEE Git 인증을 사용한다.
- 별도 인증 include를 중복 적용하지 않는다.
- EON-LEE 저장소의 `gh` 쓰기 작업에는 EON-LEE 토큰을 해당 프로세스에만 설정한다.
- 작업이 끝나면 프로세스에서 토큰을 제거한다.
- Branch protection을 약화하거나 force push하지 않는다.

## 스킬 유지 관리

- `skills/korean-clear-writing/`의 파일은 CRLF 줄바꿈을 유지한다. `.gitattributes`가 이 바이트를 보존한다.
- 스킬을 수정하면 `metadata.version`을 올리고 `python scripts/validate_skill.py`를 실행한다.
- 동작에 영향을 주는 변경은 `evals/README.md`의 절차로 이전 버전과 비교하고 결과를 `evals/results/`에 기록한다.
- 평가 기준과 통과 규칙은 결과를 보기 전에 정한다.
