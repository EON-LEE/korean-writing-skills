# korean-writing-skills

명확한 한국어 업무 문서를 작성·수정·검토하는 Copilot 스킬 `korean-clear-writing`을 관리하는 저장소다.

## 구성

| 경로 | 내용 |
|---|---|
| `skills/korean-clear-writing/SKILL.md` | 스킬 진입점. 작업 절차와 결과 형식을 정의한다. |
| `skills/korean-clear-writing/references/` | 작성 규칙(R01–R15), 문서 유형별 구조, 검토 기준, 출처 대응 |
| `skills/korean-clear-writing/assets/` | 수정 전후 예시, 회귀 검토 사례(T01–T30) |
| `scripts/validate_skill.py` | 스킬 구조 검사 스크립트 |
| `evals/` | 스킬 변경 전후의 응답 비교 평가 |

## 설치

Copilot CLI는 `~/.copilot/skills` 폴더에 있는 개인 스킬을 읽는다. 다음 두 방법 중 하나로 설치한다.

**주의:** 복사 명령은 같은 이름의 기존 파일을 확인 없이 덮어쓴다. 설치된 스킬을 직접 수정했다면 먼저 백업한다.

### 방법 1: 저장소 복제 후 복사

1. 저장소를 복제한다.

   ```shell
   git clone https://github.com/EON-LEE/korean-writing-skills.git
   cd korean-writing-skills
   ```

2. 스킬 폴더를 복사한다.

   Windows PowerShell:

   ```powershell
   $destination = "$HOME\.copilot\skills\korean-clear-writing"
   New-Item -ItemType Directory -Force $destination | Out-Null
   Copy-Item -Recurse -Force .\skills\korean-clear-writing\* $destination
   ```

   macOS 또는 Linux:

   ```bash
   mkdir -p ~/.copilot/skills/korean-clear-writing
   cp -R ./skills/korean-clear-writing/. ~/.copilot/skills/korean-clear-writing/
   ```

### 방법 2: GitHub CLI

`gh skill` 명령을 지원하는 GitHub CLI가 필요하다. 이 기능은 미리 보기 단계이므로 동작이 바뀔 수 있다.

```shell
gh skill preview EON-LEE/korean-writing-skills korean-clear-writing
gh skill install EON-LEE/korean-writing-skills korean-clear-writing --agent github-copilot --scope user
```

- 첫 번째 명령은 설치 전에 스킬 내용을 보여 준다.
- 두 번째 명령은 스킬을 `~/.copilot/skills/korean-clear-writing`에 설치하고 `SKILL.md`의 frontmatter에 출처 정보를 추가한다.
- 같은 이름의 스킬이 이미 있으면 설치를 중단한다. `--force`를 붙이면 기존 파일을 덮어쓴다.

### 설치 확인

Copilot CLI를 새로 시작하거나, 실행 중인 세션에서 다음 명령을 입력한다.

```text
/skills reload
/skills info korean-clear-writing
```

## 사용

```text
/korean-clear-writing 이 초안을 경영진 보고서로 다듬어줘
/korean-clear-writing 이 README를 수정하지 말고 검토만 해줘
/korean-clear-writing 엄격 강도로 이 절차서를 수정해줘
```

- 스킬은 작성, 수정, 검토 중 요청한 작업만 수행한다.
- 적용 강도를 지정하지 않으면 문서 유형에 따라 선택한다. 절차서와 안전·운영 문서는 엄격, 보고서·기획서·설명문은 균형을 사용한다.
- 검토 요청에는 지적마다 위치, 필수·선택 구분, 수정안을 제시한다.

## 업데이트

- **방법 1로 설치한 경우:** 저장소 폴더에서 `git pull`을 실행한 뒤 방법 1의 2단계를 다시 실행한다. 복사 명령은 저장소에서 삭제된 파일을 설치 폴더에서 지우지 않는다.
- **방법 2로 설치한 경우:** `gh skill update korean-clear-writing`을 실행한다.

## 검증

Python 3로 스킬 구조를 검사한다.

```shell
python scripts/validate_skill.py
```

이 스크립트는 frontmatter, 참조 경로, UTF-8 인코딩, 줄바꿈 일관성, 규칙·출처·사례 번호를 확인한다.

스킬 응답의 변경 효과는 `evals/README.md`의 절차로 비교한다. 결과는 `evals/results/`에 기록한다.

## 출처와 범위

스킬은 ASD-STE100의 명확성 원칙과 Andrej Karpathy가 제안한 설명 형식을 참고한다. 세부 출처와 지침 대응은 `skills/korean-clear-writing/references/source-mapping.md`에 기록되어 있다.

이 저장소는 공식 ASD-STE100 번역, 인증 자료, 전체 표준 준수 검사 도구가 아니다. 표준 전문이나 통제 어휘 사전을 포함하지 않으며, 실제 문서의 공식 준수 여부를 보증하지 않는다.
