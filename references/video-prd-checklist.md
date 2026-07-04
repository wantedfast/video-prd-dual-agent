# Video PRD Multi-Agent Checklist

Use this reference as a quality checklist for `video-prd-dual-agent`. It supports the controller workflow in `SKILL.md`; it must not reintroduce step-by-step user questioning, Agent C, virtual role simulation, or single-agent fallback.

## Material Intake Checks

For SRT, narration, subtitles, or copy:

- Read the actual text, not only timestamps.
- Preserve the SRT timing baseline.
- Extract topic, viewpoint, chapter structure, emotional arc, key claims, data claims, and risk-sensitive phrases.
- Identify phrases suitable for large on-screen text.
- Identify phrases that should remain in subtitles but should not be enlarged as screen titles.

For charts, screenshots, and reference images:

- Inspect the actual image.
- Extract palette, typography, layout, chart type, important numbers, labels, and visual hierarchy.
- Record exact data values that must not be changed.
- Record which regions should be highlighted, zoomed, masked, or avoided.
- Record any privacy, copyright, stock-code, account, or brand-logo risks.

For product or brand materials:

- Extract product category, target user, product promise, UI affordances, brand tone, and visual constraints.
- Do not invent features absent from the material.

## Required Sub-Agent Artifacts

The Controller / Integrator must collect these artifacts before writing PRD v1.

| Role | Required artifact | Must include |
| --- | --- | --- |
| Agent A | Decision memo | objective, audience, platform, ratio, duration, style, opening hook, narrative structure, risk boundary |
| Agent B | Co-design review memo | agreed / modified / disagreed decisions, executable alternatives, final decisions to reflect |
| Scene Planner | Scene overview | time ranges, narration mapping, narrative function, core message, recommended visuals, source material |
| Scene Director | Shot storyboard | per-Shot visuals, assets, camera movement, transition, HyperFrame prompt, notes |
| Motion Agent | Motion timeline | per-Shot timing, object, action, animation style, duration, intensity, purpose |
| Text Agent | Subtitle and keyword plan | subtitle rules, screen text, keyword highlights, banned words, risk wording |
| PRD Reviewer | Review verdict | `OK` or `NOT OK`; if `NOT OK`, mandatory fixes with section references |

If any artifact is missing, the Controller must stop with the mandatory-role blocked message from `SKILL.md`.

## Decision Coverage Checklist

The A/B decision loop must settle:

- video objective and content type
- target audience
- platform, aspect ratio, resolution, and duration
- source-material priority when materials conflict
- opening hook
- scene structure and pacing
- chart / screenshot / product material display strategy
- animation intensity
- subtitle density and keyword highlight rules
- ending and risk reminder
- domain risk boundary
- final AI video tool output format, defaulting to HyperFrame / HyperFrames

## Scene Checklist

- Opening hook is its own Scene.
- Each Scene has one narrative purpose.
- Scene timing follows SRT when SRT exists.
- Each Scene maps to source material or a generated visual strategy.
- Data explanation, chart display, product demonstration, conclusion, and risk warning are separated when useful.
- No Scene depends on fabricated facts.

## Shot Checklist

- Every Scene has at least one Shot.
- Complex Scenes are split into multiple Shots.
- Each Shot includes narration, visual content, main elements, background elements, camera movement, transition, required assets, and a HyperFrame-oriented prompt.
- Chart Shots say exactly what region is highlighted and how the viewer should read it.
- Screenshot/UI Shots say what is visible, what is masked, and what interaction or camera movement happens.
- Finance-related Shots do not show unmasked stock codes, account details, buy/sell markers, or actionable trading instructions unless the user explicitly provided a compliant non-investment context.

## Motion Checklist

- Motion timeline links every row to a Scene and Shot.
- The first 3 seconds have deliberate rhythm.
- Important numbers have controlled emphasis.
- Charts reveal progressively or receive focused highlights.
- Transitions are specified with timing and style.
- Motion serves comprehension, not empty spectacle.
- Repeated animation patterns are avoided unless consistency is intentional.

## Text And Subtitle Checklist

- Subtitles match the SRT/narration meaning.
- No more than two subtitle lines per screen unless the target format explicitly supports more.
- Screen titles compress but do not distort meaning.
- Important numbers, keywords, product names, and concepts are highlighted.
- Risk-sensitive phrases are softened in large screen text.
- Banned or high-risk words are listed when relevant.
- Final risk reminder wording is explicit when domain risk exists.

## Risk Boundaries

### Finance / Investment / Business

Avoid income promises, stock recommendations, explicit buy/sell instructions, target price promises, position sizing, leverage, follow-trade language, and future-return implications.

Allow methodology, historical cases, risk reminders, abstract data display, and market logic explanation.

Required framing for finance content:

- historical review
- method demonstration
- data observation
- learning exchange
- not investment advice
- history does not represent the future

### Medical / Health / Pharmaceutical

Avoid diagnosis conclusions, treatment promises, replacing doctor advice, exaggerated efficacy, and fear-based claims.

Allow science education, medical consultation reminders, lifestyle suggestions, and risk identification.

### Technology / AI / Software Product

Avoid fake features, exaggerated performance, presenting unimplemented capabilities as real, and over-complex UI.

Allow product workflow demos, abstract architecture animation, feature highlights, and usage scenarios.

### Brand Promotion / Advertising

Avoid value-proposition pileups, empty slogans, visual-brand mismatch, and exaggerated claims.

Allow brand story, user pain points, product value, and emotionalized visual angle.

## Final PRD Completeness Checklist

The final PRD must include:

- `0. 多 Agent 执行摘要`
- `1. 项目目标`
- `2. 输入素材分析`
- `3. 需求决策总表`
- `4. 视频定位`
- `5. Scene 总览`
- `6. Scene-by-Scene 结构`
- `7. Shot-by-Shot 分镜 PRD`
- `8. Motion 动画时间轴`
- `9. 字幕与关键词高亮规则`
- `10. 视觉语言`
- `11. 统一视觉规范`
- `12. AI 视频生成总提示词`
- `13. Negative Prompt / 禁止事项`
- `14. 风险与合规检查`
- `15. 生成后检查清单`

The final response must include execution evidence:

- Selected agents
- One-line artifact returned by each agent
- PRD Reviewer verdict
- Final PRD file path when created
