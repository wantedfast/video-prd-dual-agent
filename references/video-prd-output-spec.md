# Video PRD Output Specification

The Markdown generator must produce every section listed in `SKILL.md`. Use this reference to judge whether the structured data is detailed enough before build and whether the generated PRD is complete during review.

## 0. 多 Agent 执行摘要

Include selected agents, one-line artifact returned by each agent, PRD Reviewer verdict, and major assumptions. Do not include long transcripts or hidden reasoning.

## 1. 项目目标

Explain what problem the video solves, what the audience should understand and remember, and the distribution goal.

## 2. 输入素材分析

Organize SRT/narration, screenshots, charts, product materials, brand materials, statistics, and other assets. Explain how each is used. If a type is absent, write `未提供`; do not invent it.

## 3. 需求决策总表

Include platform, aspect ratio, duration, style, opening hook, narrative structure, subtitle rules, chart usage, animation intensity, risk reminder, and AI generation method. Each decision needs its final value and rationale.

## 5. Scene 总览

Each Scene needs a time range, narrative function, core message, recommended visual, and source assets. List the opening hook separately.

## 7. Shot-by-Shot 分镜 PRD

Each Shot needs a time range, exact narration mapping, visual content, subject and background elements, camera movement, transition, assets, screen text, facts, notes, and a HyperFrame-oriented prompt.

## 7A. 视觉包装素材 PRD

Each asset needs a stable ID, type, source/generated status, path or proposed filename, purpose, Shot usage, processing/generation instruction, negative constraints, approval status, and risk notes.

- This section is mandatory when packaging assets are relevant.
- `approved_for_generation` only marks safe future generation; it does not trigger image generation.
- Use `planned_only` by default.
- Nonfactual symbolic packaging is allowed; fabricated factual footage is forbidden.

## 8. Motion 动画时间轴

Every Motion and sound-effect row must link to a Shot. Include relative timing, object or sound, action/character, duration when relevant, intensity/easing, and narrative purpose.

## 9. 字幕与关键词高亮规则

Include subtitle position, font size, maximum characters, line count, keyword selection and style, screen-title rules, risk-reminder rules, and forbidden words. When SRT exists, preserve exact synced subtitle text and map it by stable cue IDs.

## 12. AI 视频生成总提示词

Output one global HyperFrame / HyperFrames prompt containing style, applicable global visual constraints, aspect ratio, camera language, Motion, subtitle style, chart/screenshot treatment, pacing, risk wording, a no-fabrication instruction, and an instruction to follow the Scene/Shot/Motion timeline exactly.

## 14. 风险与合规检查

For finance content, state whether the material involves investment advice, individual stocks/funds/ETFs, return promises, exaggerated language, unclear sources, replaced high-risk expressions, and the final risk reminder. For other domains, keep the section and report the relevant risk checks.
