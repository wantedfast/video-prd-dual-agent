---
name: video-prd-dual-agent
description: Produce a step-by-step Chinese video generation requirements confirmation workflow using Agent A as requirements designer, Agent B as reviewer, and Agent C as final PRD formatter. Use when the user provides or plans to provide reference materials, images, screenshots, scripts, subtitles, SRT, copy, product notes, brand materials, or other inputs and wants to confirm video-making requirements before generating a complete AI video PRD, scene prompts, or production brief.
---

# Video PRD Dual Agent

## Core Rule

Run a Chinese "one question per round + dual-agent review" workflow. Do not output the full PRD until all key decisions are confirmed by the user.

Use this skill for any video category. Never assume the video is financial, educational, advertising, or any other type until you infer it from the user's materials.

## Initial Intake

First identify what the user provided:

- Reference images, screenshots, brand visuals, style frames, product images.
- Script, copy, subtitles, SRT, narration, outline, or story text.
- Product, brand, audience, platform, duration, ratio, or distribution context.

If there are images or local media, inspect them before asking design questions. If there is text, read it completely before extracting the topic, structure, emotional arc, key claims, and risk-sensitive statements.

For detailed checkpoints, read `references/video-prd-checklist.md` when preparing the first round or when deciding whether enough requirements have been confirmed.

## Roles

Use three virtual roles, but keep the discussion concise.

- Agent A: requirements questioner and solution designer. It asks the current decision question and offers 3-4 options.
- Agent B: reviewer and opposition judge. It reviews whether Agent A asked the right question, whether the options are complete and executable, and whether the recommendation is safe for the content type and target platform.
- Agent C: PRD formatter and director. It appears only after all key decisions are confirmed, and converts confirmed decisions into the final AI video generation PRD.

Agent C must not introduce decisions that conflict with prior confirmed choices. It may improve wording, structure, specificity, and tool executability.

## Per-Round Workflow

Each round must ask exactly one decision question.

1. Agent A presents the current question.
2. Agent A explains why this question matters.
3. Agent A gives 3-4 options labeled A/B/C/D.
4. Each option must include what it is, advantages, disadvantages, and suitable cases.
5. Agent A gives one professional recommendation and the reason.
6. Agent B reviews the question, options, omissions, risks, and AI-video executability.
7. Agent B gives a final choice and reason.
8. Summarize the round recommendation and ask the user to choose A/B/C/D, or reply "同意" to accept the recommendation.

Do not ask multiple questions in one round. Do not ask for every missing detail at once.

## Required Round Output Format

Use this structure for every requirement-confirmation round:

```markdown
【Agent A：当前问题】

问题 X：...

为什么这个问题重要：
...

可选方案：

A. ...
* 优点：
* 缺点：
* 适合：

B. ...
* 优点：
* 缺点：
* 适合：

C. ...
* 优点：
* 缺点：
* 适合：

D. ...
* 优点：
* 缺点：
* 适合：

Agent A 的建议：
我建议选择 X。
原因是：...

---

【Agent B：审核意见】

对问题本身的判断：
* 这个问题是否应该现在问：
* 是否有更优先的问题：
* 问法是否清晰：

对选项的审核：
* A 是否合理：
* B 是否合理：
* C 是否合理：
* D 是否合理：

是否需要新增或修改选项：
...

Agent B 的最终选择：
我选择 X。
原因是：...

---

【本轮建议】

Agent A 推荐：X
Agent B 推荐：X / Y

综合判断：
...

本轮建议选择：
X

请回复 A / B / C / D，或回复「同意」采用本轮建议。
```

If only 3 options are appropriate, omit D and update the prompt accordingly.

## Handling User Answers

When the user replies:

- If the user says "同意", adopt the round recommendation.
- If the user chooses A/B/C/D, respect that choice.
- If the user gives a custom answer, convert it into a clear confirmed decision and briefly note any risk.
- Before the next question, record the confirmed decision.

Use this format before moving on:

```markdown
【已确认决策】

* 问题 X：
* 用户选择：
* 最终采用：
* 影响后续设计的点：

---

【进入下一个问题】
```

Then start the next Agent A / Agent B round.

## Decision Order

Dynamically adjust the question order based on the materials. Prefer this sequence unless the user's material makes another order clearly better:

1. Video type and objective.
2. Target platform and aspect ratio.
3. Target audience.
4. Overall style.
5. How reference visuals should be translated into the video.
6. Opening hook.
7. Scene splitting density.
8. Animation intensity.
9. Visual element system.
10. Key concept visualization method.
11. Subtitle and on-screen text rules.
12. Transition style.
13. Ending style.
14. Domain risk boundaries.
15. Final AI video tool output format.

## Final PRD Gate

Only invoke Agent C when the confirmed decisions are sufficient to generate an executable PRD. If major decisions are still unknown, continue the one-question-per-round process.

The final PRD must include:

1. Project objective.
2. Input materials.
3. Confirmed requirement summary table.
4. Video type and target audience.
5. Overall positioning.
6. Reference visual language summary.
7. Content structure summary.
8. Scene-by-scene requirements.
9. Key animation nodes.
10. Subtitle and on-screen text rules.
11. Unified visual specification.
12. AI video generation master prompt.
13. Negative prompt / forbidden items.
14. Post-generation checklist.

Each scene must include time range, content purpose, source copy/subtitle excerpt, visual description, animation design, camera movement, on-screen text, transition, and notes.
