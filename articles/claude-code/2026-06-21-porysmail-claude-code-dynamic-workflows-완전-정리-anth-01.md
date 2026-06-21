---
id: "2026-06-21-porysmail-claude-code-dynamic-workflows-완전-정리-anth-01"
title: "@porysmail: ✅ Claude Code Dynamic Workflows 완전 정리 (Anthropic 내부 엔지니어들이 실"
url: "https://x.com/porysmail/status/2068499644666331441"
source: "x"
category: "claude-code"
tags: ["claude-code", "API", "AI-agent", "JavaScript", "x"]
date_published: "2026-06-21"
date_collected: "2026-06-21"
summary_by: "auto-x"
query: ""Claude Code" workflow OR CLAUDE.md setup OR "Claude context""
---

✅ Claude Code Dynamic Workflows 완전 정리
(Anthropic 내부 엔지니어들이 실제로 쓰는 방식)

Claude Code 사용자 대부분은 아직도 프롬프트를 하나씩 연결하고 복사-붙여넣기 하면서 작업한다.

Dynamic Workflows를 제대로 쓰면 Claude가 그 작업에 맞는 JavaScript 하네스를 실시간으로 작성해 여러 sub-agent를 조율하고 검증하고 루프를 돌려준다.

아래는 Anthropic 내부에서 실제로 쓰는 방식 + 6가지 핵심 패턴을 정리한 내용이다.

🔥 1. 기본 생각의 틀 (Mental Model)

• 워크플로우 = Claude가 직접 작성하는 하네스
• 기본 Claude Code: 하나의 컨텍스트 창에서 계획 + 실행을 함께 함
• Dynamic Workflow: Claude가 그 작업에 최적화된 JavaScript 파일을 실시간으로 만들어 여러 sub-agent를 관리

✅ Dynamic Workflow가 주는 진짜 장점
• 각 에이전트가 독립적인 컨텍스트를 가짐 (정보 오염 방지)
• 에이전트마다 다른 모델을 지정 가능 (Opus / Sonnet / Haiku)
• 격리 수준 선택 가능 (worktree 또는 remote)

✅ 시작 방법
• 그냥 말하기: “make a workflow that…”
• 또는 트리거 단어: ultracode

🔥 2. Dynamic Workflow가 해결하는 3가지 실패 모드

• Agentic Laziness → 복잡한 작업 중간에 포기함
  해결: 여러 에이전트가 나눠서 끝까지 실행

• Self-preferential Bias → 자신이 만든 결과를 스스로 검증
  해결: 작성 에이전트와 검증 에이전트를 완전히 분리

• Goal Drift → 여러 턴 지나면서 목표가 희미해짐
  해결: 각 에이전트가 명확한 목표를 가진 독립 컨텍스트 사용

🔥 3. 핵심 API

• parallel() → 여러 작업 동시에 실행 → 모두 끝날 때까지 대기
• pipeline() → 작업을 순차적으로 흐르게 함 (더 빠르고 저렴)
• agent() → 개별 sub-agent 생성

🔥 4. 6가지 핵심 패턴

• 1. Classify-and-act
  → 작업 종류가 다양할 때
  → 먼저 분류 에이전트가 판단 → 적합한 모델로 라우팅

• 2. Fan-out-and-synthesize
  → 많은 항목을 처리해야 할 때
  → 여러 에이전트가 병렬 작업 → 하나로 종합

• 3. Adversarial verification
  → 신뢰성이 중요한 작업
  → 작성 에이전트와 별도의 검증 에이전트 사용

• 4. Generate-and-filter
  → 아이디어나 솔루션을 많이 뽑아야 할 때
  → 많이 생성 → 기준으로 필터링

• 5. Tournament
  → 품질 비교·랭킹이 필요할 때
  → 여러 방식으로 경쟁 → pairwise 비교로 승자 결정

• 6. Loop until done
  → 언제 끝날지 모를 때
  → 조건이 만족될 때까지 계속 반복

🔥 5. 실제 사용 사례별 패턴 조합

• 대규모 마이그레이션 / 리팩토링 → Fan-out + Adversarial verification + Loop until done
• 딥 리서치 → Fan-out + Adversarial verification + Synthesize
• 코드 리뷰 → 작성 에이전트 + 별도 검증 에이전트 완전 분리
• 버그 원인 분석 → 여러 이론 생성 → 검증 패널 → Loop until done
• 디자인 / 네이밍 / UI 선택 → Generate-and-filter + Tournament

🔥 6. 실전에서 함께 쓰는 명령어

• /goal → 하드 종료 조건 설정
  예시: “이론 하나가 증명될 때까지 절대 멈추지 마”

• /loop → 워크플로우를 주기적으로 자동 실행

• 토큰 예산 명시
  예시: “이 워크플로우는 최대 15,000 토큰까지만 사용해”

🔥 7. 보안: Quarantine 패턴

• 신뢰할 수 없는 입력(유
