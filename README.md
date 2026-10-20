# korean-writing-skills

명확한 한국어 업무 문서를 작성하고 검토하는 Copilot 스킬을 버전 관리하는 저장소다.

## 포함 파일

```text
skills/korean-clear-writing/
├── SKILL.md
├── assets/
│   ├── acceptance-cases.md
│   └── before-after-examples.md
└── references/
    ├── document-patterns.md
    ├── korean-writing-rules.md
    ├── review-checklist.md
    └── source-mapping.md
```

## 설치

저장소를 복제한 뒤 `skills/korean-clear-writing` 폴더를 사용자별 Copilot 스킬 폴더에 복사한다.

### Windows PowerShell

```powershell
$destination = "$HOME\.copilot\skills\korean-clear-writing"
New-Item -ItemType Directory -Force $destination
Copy-Item -Recurse -Force .\skills\korean-clear-writing\* $destination
```

### macOS 또는 Linux

```bash
mkdir -p ~/.copilot/skills/korean-clear-writing
cp -R ./skills/korean-clear-writing/. ~/.copilot/skills/korean-clear-writing/
```

Copilot CLI에서 다음 명령으로 스킬 목록을 다시 불러온다.

```text
/skills reload
```

기존 설치가 있으면 복사 명령이 같은 이름의 파일을 덮어쓸 수 있다. 로컬에서 수정한 파일이 있으면 먼저 백업하거나 변경 사항을 비교한다.

## 사용

```text
/korean-clear-writing 이 초안을 경영진 보고서로 다듬어줘
```

이 스킬은 보고서, 업무 문서, 기획서, 제안서, 기술 설명서, 절차서의 작성·수정·검토에 사용한다.

## 출처와 범위

스킬은 ASD-STE100의 명확성 원칙과 Andrej Karpathy가 제안한 설명 형식을 참고한다.

세부 출처와 지침 대응은 `skills/korean-clear-writing/references/source-mapping.md`에 기록되어 있다.

이 저장소는 공식 ASD-STE100 번역, 인증 자료, 전체 표준 준수 검사 도구가 아니다. 표준 전문이나 통제 어휘 사전을 포함하지 않으며, 실제 문서의 공식 준수 여부를 보증하지 않는다.