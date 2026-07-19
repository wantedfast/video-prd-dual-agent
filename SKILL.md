---
name: video-prd-dual-agent
description: Controller skill for mandatory real multi-agent Chinese video PRD production for HyperFrame / HyperFrames. Use when the user invokes video-prd-dual-agent or provides SRT, narration, screenshots, charts, product notes, statistics, or visual assets and asks for a video PRD, video generation PRD, storyboard, shot plan, animation plan, or HyperFrame-ready production brief. This skill requires visible role-bounded sub-agent dispatch for Agent A, Agent B, Scene Planner, Scene Director, Visual Asset Agent, Motion Agent, Text Agent, and PRD Reviewer; it must not silently simulate those roles inside one agent.
---

# Video PRD Dual Agent

## Core Positioning

`video-prd-dual-agent` is a controller skill for mandatory real multi-agent PRD production.

It does **not** simulate an internal team. The main agent is the Controller / Integrator: it reads the materials, dispatches visible role-bounded sub-agents, collects their artifacts, integrates the final PRD, and reports execution evidence.

Forbidden:

- silently simulating Agent A / Agent B / Scene Planner / Scene Director / Visual Asset Agent / Motion Agent / Text Agent / PRD Reviewer inside one hidden draft
- claiming multi-agent execution without listing dispatched agents and returned artifacts
- asking the user for step-by-step decisions when the provided materials and defaults are enough
- producing a PRD that lacks Scene, Shot, visual asset plan, Motion, subtitle, prompt, or risk-review sections

Invoking this skill counts as an explicit user request for role-bounded sub-agent work.

## Mandatory Real Multi-Agent Execution

Before generating any PRD content, the main agent must:

1. Load this `SKILL.md` and the required reference checklist.
2. Read `references/video-prd-checklist.md`, `references/video-visual-constraints.md`, `references/video-prd-structured-workflow.md`, and `references/video-prd-output-spec.md`.
3. Read all user-provided text materials completely, including SRT files.
4. Inspect all user-provided local images, screenshots, charts, and media that are relevant to the PRD.
5. Dispatch visible sub-agents for all mandatory roles:
   - Agent A
   - Agent B
   - Scene Planner
   - Scene Director
   - Visual Asset Agent
   - Motion Agent
   - Text Agent
   - PRD Reviewer
6. Run Agent A and Agent B as an explicit proposal-review-reconciliation loop before downstream planning.
7. Create `video-prd.project.json` from `assets/video-prd-project.template.json`, then make it the only editable source of truth for Scene, Shot, subtitle, asset, Motion, sound-effect, fact, and render data.
8. Collect one concrete artifact from each role and merge it into the canonical JSON after each dependency wave. Agents return structured fields or patches; they do not maintain separate Markdown truth.
9. Run the deterministic pre-review gate with `scripts/video_prd_pipeline.py validate`. Fix every error before review. Treat warnings as explicit decisions, or use `--strict` to block them.
10. Generate PRD v1 with `scripts/video_prd_pipeline.py build`. Do not hand-edit the generated Markdown.
11. Send the canonical JSON, validation report, and generated PRD v1 to PRD Reviewer.
12. If PRD Reviewer returns `NOT OK`, route mandatory fixes back to the owning role or fix them locally when ownership is purely integrative, update the JSON, rerun validation and build, then repeat reviewer validation until `OK` or until the blocker is explicit.

If visible sub-agent capability is unavailable, do not silently degrade into single-agent simulation. Return exactly:

`Blocked: visible sub-agent capability unavailable; this skill forbids silent single-agent simulation.`

If any mandatory role cannot be dispatched or fails to return a concrete artifact, do not continue as if the role succeeded. Return exactly:

`Blocked: mandatory role artifact unavailable: <role-name>. This skill forbids completing the PRD without all required role artifacts.`

## Canonical Data And Parallel Scheduling

Read `references/video-prd-structured-workflow.md` before dispatch. Its data ownership and dependency graph are mandatory.

The Controller owns these four artifacts:

- `video-prd.project.json`: canonical editable data
- original SRT and source assets: immutable evidence
- `video-prd.validation.json`: automated gate evidence
- `video-prd.md`: generated Markdown delivery

Run work in dependency waves:

1. Material intake and `sync-srt`.
2. Agent A proposal -> Agent B review -> Agent A reconciliation.
3. Scene Planner -> Scene Director Shot skeleton.
4. In parallel: Visual Asset Agent, Text Agent, and Controller fact registration.
5. Motion Agent after visual object and asset IDs are stable; Motion Agent also owns crisp sound-effect cues and their exact Shot-relative timing.
6. Structured merge -> automated validation -> Markdown build -> PRD Reviewer.

Do not serialize independent work merely for convenience. Do not start dependent work from unstable IDs. The Controller must merge by stable IDs (`scene_id`, `shot_id`, `asset_id`, `fact_id`, `srt_id`) and reject orphan references.

The automated validator runs before PRD Reviewer and must cover:

- exact SRT cue ID, timing, and text consistency
- continuous Shot timing with no gap or overlap
- exactly-once SRT coverage by Shots
- required fields, unique IDs, and valid cross-references
- existence of every source-asset path
- banned terms and required disclaimers
- canonical numeric facts, required context, and unregistered-number warnings

Automation is a deterministic gate, not a substitute for the Reviewer. PRD Reviewer still judges narrative logic, visual feasibility, pacing, hierarchy, compliance nuance, and overall production quality.

## Execution Evidence

The final response must include a short execution evidence block before or after the PRD location:

- Selected agents
- One-line artifact returned by each agent
- PRD Reviewer verdict
- Final PRD file path, when a file is created

Hide chain-of-thought and do not paste long agent transcripts unless the user explicitly asks for them. Do not hide the fact that agents were dispatched.

## Initial Intake

First identify and analyze everything the user provided:

- SRT, narration script, voiceover draft, subtitles, outline, or story text
- screenshots, charts, data images, product images, brand visuals, style frames, or reference images
- product, brand, audience, platform, duration, aspect ratio, distribution context, and risk constraints
- existing local files mentioned in the thread, such as generated charts, reports, images, data files, or prior scripts

If there are images or local media, inspect them before writing the PRD. If there is text, read it completely before extracting the topic, structure, emotional arc, key claims, risk-sensitive statements, and phrases suitable for on-screen emphasis.

For detailed checkpoints, read `references/video-prd-checklist.md` before dispatching PRD roles.

For the default visual packaging system, read `references/video-visual-constraints.md` before dispatching PRD roles. Treat it as the global visual baseline for subtitle, packaging, HUD, animation, safe-zone, and HyperFrames implementation constraints unless the user provides a higher-priority brand guide, visual reference, or explicit alternate style.

## Default Assumptions

Use these defaults only when the user does not explicitly specify a choice and the materials do not imply another answer.

- Default platform: Douyin / WeChat Video Account / Xiaohongshu short-video distribution.
- Default aspect ratio: 9:16 vertical, 1080x1920.
- If charts, dashboards, desktop UI, or 16:9 assets are central, use a 16:9 master version and note a 9:16 derivative when useful.
- If the user provides SRT, use the SRT total duration and timestamps as the timing baseline.
- If the user provides only narration, estimate duration from Chinese narration speed and split by semantic paragraphs.
- Default style: high information density, fast rhythm, strong opening hook, data-driven presentation, clear subtitles, highlighted keywords and numbers.
- The first 3 seconds must contain at least one strong conclusion, question, key statistic, conflict point, or suspense point.
- Default final target: HyperFrame / HyperFrames video generation workflow.

## Role Contracts

The main agent is the Controller / Integrator. It is not allowed to impersonate the role outputs below.

### Agent A: Requirements Designer

Input:

- user request
- complete text/SRT summary
- visual asset inventory
- chart/data facts
- known risk constraints

Output artifact:

- decision memo covering objective, audience, platform, ratio, duration, style, opening hook, narrative structure, chart/data strategy, and risk boundary
- concrete questions for Agent B to agree with, modify, or reject
- structured `meta` and `decisions` patch keyed to the canonical JSON

### Agent B: Co-Designer

Input:

- Agent A decision memo
- same material summary and risk constraints

Output artifact:

- review memo
- for each decision: `agreed`, `modified`, or `disagreed`
- executable alternative when modifying or disagreeing
- list of decisions that must be reflected in the final PRD
- structured decision amendments keyed by decision item; do not rewrite unrelated fields

Collaboration rule:

- Agent A proposes; Agent B responds.
- If Agent B modifies or disagrees on core decisions, send the response back to Agent A once for reconciliation.
- Limit the A/B loop to two rounds unless the conflict would make the PRD unusable.

### Scene Planner

Input:

- reconciled Agent A/B decision memo
- SRT or narration timeline
- source material map

Output artifact:

- Scene overview table
- per-Scene time range, narration segment, narrative purpose, core message, recommended visual type, source material, emotional rhythm
- canonical `scenes[]` records with stable Scene IDs and source asset IDs

Scene rules:

- Split by content logic, not mechanical equal duration.
- Opening hook must be its own Scene.
- Align timing with SRT timestamps when SRT exists.

### Scene Director

Input:

- Scene Planner artifact
- visual asset inventory
- HyperFrame target constraints

Output artifact:

- Shot-by-Shot storyboard table
- per-Shot time range, narration, visual content, subject elements, background elements, camera movement, transition, required assets, HyperFrame-oriented prompt, notes
- canonical `shots[]` skeleton with stable Shot IDs and exact `srt_ids`; leave owned arrays present even when another role fills them later

Shot rules:

- Each Scene must include at least one Shot.
- Complex Scenes should be split into multiple Shots.
- Do not write only "show chart" or "show image"; describe entry motion, highlighted region, viewer focus, and transition.

### Visual Asset Agent

Input:

- reconciled Agent A/B decision memo
- Scene Planner artifact
- Scene Director storyboard
- source material map
- user-provided visual references and risk constraints
- global visual constraints from `references/video-visual-constraints.md`

Output artifact:

- visual asset boundary: what can be generated as packaging, what must come from source footage, and what is forbidden
- asset list: per-asset id, type, source type, purpose, suggested filename, and approved-for-generation flag
- usage map: per-asset Scene/Shot placement, trigger moment, duration, layer position, and narrative purpose
- prompt set: image-generation or design prompts plus negative prompts
- motion/risk notes: how Motion Agent should animate each asset and what factual risks to avoid
- generation mode: `planned_only` by default; use `generate_assets` only when the user explicitly requests actual image files
- canonical `assets[]` records and Shot `asset_ids` patches; every source asset path must be exact and verifiable

Visual asset rules:

- This role is a PRD planning role; it must not generate images or claim generated file paths.
- Packaging assets may include title cards, labels, stickers, symbolic scene illustrations, texture transitions, info cards, and teaser cards.
- Generated/planned assets must enhance the packaging layer only. They must not fake dishes, shop exteriors/interiors, people, maps, streets, landmarks, receipts, menus, ratings, or any other factual footage.
- If actual image generation is requested, route approved assets to a separate Asset Generation Agent outside PRD planning; video rendering remains outside this skill.

### Motion Agent

Input:

- Scene Planner artifact
- Scene Director storyboard
- Visual Asset Agent usage map, when packaging assets are planned
- global visual constraints from `references/video-visual-constraints.md`

Output artifact:

- Motion timeline table
- per-Shot animation timing, objects, actions, animation style, duration, intensity, and purpose
- per-Shot `motion[]` and `sfx[]` patches with Shot-relative `at_ms`; every sound cue includes name, sonic character, and narrative purpose

Motion rules:

- The first 3 seconds need clear rhythm design.
- Important numbers may enlarge, outline, glow, or sweep-light, but avoid empty spectacle.
- Chart content should reveal progressively rather than appearing all at once.
- Motion must serve information clarity.
- Default interface/data cues should be crisp, short, clean, and restrained: glass tick, soft click, light chime, or precise whoosh. Avoid muddy impacts and generic trailer booms unless the brief explicitly calls for them.

### Text Agent

Input:

- SRT or narration
- Scene and Shot artifacts
- risk constraints

Output artifact:

- subtitle and keyword table
- main on-screen title and supporting text rules
- highlighted words and number rules
- banned-word check
- final risk wording
- canonical Shot `screen_text` patches plus `rules.banned_terms`, `rules.required_disclaimers`, subtitle rules, and keyword highlights

Text rules:

- No more than 2 subtitle lines per screen.
- Prefer no more than 14 Chinese characters per line for vertical video; for 16:9 chart videos, use readable line breaks and avoid chart overlap.
- Important numbers should be isolated or enlarged when useful.
- Subtitles must match the narration meaning.
- Screen titles may compress wording but must not distort the SRT/narration.

### PRD Reviewer

Input:

- PRD v1 assembled by the Controller / Integrator
- canonical `video-prd.project.json`
- `video-prd.validation.json` with zero unresolved errors
- all role artifacts
- source material summary

Output artifact:

- review verdict ending with exactly `OK` or `NOT OK`
- if `NOT OK`, list only mandatory fixes with section references

Reviewer must check:

- completeness
- executable Scene design
- concrete Shot design
- concrete Motion rules
- clear subtitle rules
- consistency with user materials
- HyperFrame / HyperFrames suitability
- finance, medical, marketing, copyright, or other domain risk controls when relevant
- absence of fabricated data
- absence of forbidden expressions

## Finance And Investment Risk Rules

Activate finance risk review when the material involves stocks, funds, ETFs, futures, macroeconomics, financial reports, industry investing, trading strategies, individual stock analysis, price movement predictions, position sizing, or return statistics.

Finance content should frame results as historical observation, product demonstration, methodology explanation, and learning exchange. It must not be framed as investment advice.

Do not output concrete trading execution advice, including:

- buy-in price ranges
- take-profit or stop-loss levels
- position-size percentages or allocation ratios
- leverage multiples
- intraday follow-trade instructions
- packaging backtest or historical win rate as future return expectation

Forbidden or must-be-softened expressions include:

- 必涨
- 稳赚
- 保证收益
- 无风险
- 无脑买入
- 满仓
- 梭哈
- 确定性机会
- 明确买入
- 明确卖出
- 目标价一定达到
- 100% 胜率
- 包赚
- 翻倍确定
- 暴富机会

Prefer safer wording such as:

- 历史复盘
- 方法演示
- 数据观察
- 学习交流
- 不构成投资建议
- 需要继续验证
- 历史数据不代表未来
- 理论最优是事后观察指标，不代表实盘可达到

If user material contains high-risk language, preserve the factual context but rewrite screen text into non-actionable analysis, risk observation, method explanation, or educational framing. SRT subtitles may follow the narration, but large screen text must be risk-controlled.

## SRT And Material Handling Rules

If the user provides SRT:

- read SRT bytes with encoding detection when needed
- preserve timestamps
- run `python scripts/video_prd_pipeline.py sync-srt <project.json>`; do not manually retype the canonical `subtitles` array
- never edit synced subtitle ID, timing, or text to make the storyboard fit; change Shot boundaries and mappings instead
- align Scene and Shot timing with SRT as much as possible
- use SRT text as narration ground truth unless the user provides a newer script
- do not omit important narration information
- merge subtitle items into larger Scenes while preserving logical order

If terminal output shows garbled text, verify file bytes and encoding before concluding that the SRT is corrupt.

If multiple materials conflict, resolve with these priorities:

1. Timing: SRT timestamps > narration timing estimate
2. Subtitle meaning: newest user-provided script > SRT text > older conversation draft
3. Data: chart or screenshot original text and numbers > narration summary
4. Visual style: provided brand/material visuals > generic defaults

Record any assumption in the internal decision summary.

## PRD Output Structure

Use Chinese. Prefer concise but complete Markdown. The following structure is rendered from `video-prd.project.json` by `scripts/video_prd_pipeline.py build`; never maintain it separately by hand.

```markdown
# AI 视频生成 PRD

## 0. 多 Agent 执行摘要

## 1. 项目目标

## 2. 输入素材分析

## 3. 需求决策总表

## 4. 视频定位

## 5. Scene 总览

## 6. Scene-by-Scene 结构

## 7. Shot-by-Shot 分镜 PRD

## 7A. 视觉包装素材 PRD

## 8. Motion 动画时间轴

## 9. 字幕与关键词高亮规则

## 10. 视觉语言

## 11. 统一视觉规范

## 12. AI 视频生成总提示词

## 13. Negative Prompt / 禁止事项

## 14. 风险与合规检查

## 15. 生成后检查清单
```

For detailed per-section content requirements, read `references/video-prd-output-spec.md`. The JSON schema and generator define table shape; the output specification defines semantic completeness.

## Completion Checklist For Skill Edits

When editing this skill, verify:

1. `SKILL.md` contains no garbled Chinese.
2. It explicitly forbids silent single-agent simulation.
3. It requires visible sub-agent dispatch.
4. Every mandatory role has an output artifact contract.
5. PRD Reviewer has an `OK` / `NOT OK` gate.
6. Final output requires execution evidence.
7. Visual Asset Agent is represented when packaging assets are relevant.
8. `references/video-visual-constraints.md` is read and applied as the default visual baseline.
9. HyperFrame / HyperFrames remains the primary output target.
10. Finance risk-control rules are included.
11. SRT handling requires reading actual text, not only timestamps.
12. PRD includes executable Scene, Shot, visual asset, Motion, subtitle, prompt, and risk sections.
13. `video-prd.project.json` is the only editable source of truth and generated Markdown is not hand-edited.
14. Automated validation runs before PRD Reviewer and blocks SRT, timing, reference, path, banned-term, disclaimer, and numeric-fact errors.
15. Independent roles run in parallel dependency waves, while Motion waits for stable visual object and asset IDs.
16. Motion Agent specifies Shot-relative crisp sound effects with character, timing, and narrative purpose.
