# video-prd-dual-agent

面向 HyperFrame / HyperFrames 的中文视频 PRD Controller Skill。它强制调度真实、可见、职责受限的 Agent 团队，并使用统一结构化数据维护 Scene、Shot、字幕、素材、Motion、音效和数字事实。

最终 Markdown 不再由多个角色各自维护：所有角色把结果合并到 `video-prd.project.json`，自动门禁通过后再确定性生成 PRD，从源头减少字幕错位、时间空档、素材路径失效、禁词和数字冲突。

## 核心流程

```text
素材读取 + SRT 同步
        |
Agent A -> Agent B -> Agent A 统一决策
        |
Scene Planner -> Scene Director
        |
        +----------------------+----------------------+
        |                      |                      |
Visual Asset Agent       Text Agent          数字事实登记
        |
Motion Agent（Motion + 清脆音效）
        |
结构化合并 -> 自动校验 -> Markdown 生成 -> PRD Reviewer
```

独立任务并行，存在真实依赖的任务串行。Reviewer 之前，脚本自动检查：

- SRT 的字幕 ID、时间与文本是否完全一致
- Shot 时间轴是否连续、是否覆盖全部字幕且不重不漏
- Scene、Shot、字幕、素材、事实引用是否有效
- 源素材路径是否存在
- 禁词与必需风险提示是否满足
- 关键数字是否使用唯一规范值和必要上下文

Reviewer 继续负责机器无法可靠判断的叙事逻辑、视觉可执行性、节奏、信息层级和合规语境。

## 必需角色

- Agent A：需求设计
- Agent B：共同设计与反方审核
- Scene Planner：Scene 结构
- Scene Director：Shot 骨架与画面提示词
- Visual Asset Agent：素材边界、路径、用途与生成/处理说明
- Motion Agent：Motion 与 Shot 级清脆音效时间轴
- Text Agent：字幕、屏幕文字、关键词、禁词与风险措辞
- PRD Reviewer：`OK` / `NOT OK` 终审

Skill 禁止在无法调用可见子 Agent 时悄悄退化为单 Agent 虚拟扮演。

## 使用结构化流水线

从模板创建项目文件：

```powershell
Copy-Item assets/video-prd-project.template.json video-prd.project.json
```

设置 `source.srt_path` 后同步原始 SRT：

```powershell
python scripts/video_prd_pipeline.py sync-srt video-prd.project.json
```

角色产物合并完成后运行 Reviewer 前门禁：

```powershell
python scripts/video_prd_pipeline.py validate video-prd.project.json --report video-prd.validation.json
```

通过后生成 Markdown：

```powershell
python scripts/video_prd_pipeline.py build video-prd.project.json --output video-prd.md --report video-prd.validation.json
```

加上 `--strict` 可让“未登记数字”等 warning 也阻止交付。

## 安装

```powershell
git clone https://github.com/wantedfast/video-prd-dual-agent.git "$env:USERPROFILE\.codex\skills\video-prd-dual-agent"
```

## 调用示例

```text
使用 $video-prd-dual-agent，根据这份 SRT 和两张数据图制作苹果广告风格的视频 PRD；数字必须引用原图，界面音效要清脆。
```

## 目录

```text
video-prd-dual-agent/
├── SKILL.md
├── agents/openai.yaml
├── assets/video-prd-project.template.json
├── references/
│   ├── video-prd-checklist.md
│   ├── video-prd-output-spec.md
│   ├── video-prd-structured-workflow.md
│   └── video-visual-constraints.md
├── scripts/video_prd_pipeline.py
└── tests/test_video_prd_pipeline.py
```
