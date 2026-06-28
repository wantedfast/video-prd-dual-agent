# video-prd-dual-agent

一个用于 Codex 的「通用视频 PRD 双 Agent 需求确认」Skill。

它会根据用户提供的参考素材、文案、字幕、SRT、脚本、产品说明或品牌资料，采用「一问一答 + Agent B 审核」的方式逐步确认视频生成需求，最后输出可直接交给 AI 视频生成工具使用的完整中文视频 PRD。

## 适用场景

适用于需要先确认需求、再生成视频制作 PRD 的任务，例如：

- 金融知识视频
- 产品宣传视频
- 教育课程视频
- 科技解释视频
- 企业介绍视频
- 情感故事视频
- 剧情短片
- 旅游视频
- 游戏解说视频
- 个人 IP 视频
- 社交媒体短视频
- 广告创意视频
- 动画科普视频
- 品牌视觉视频

Skill 不会默认假设视频类型，而是会根据素材自动判断内容领域，并应用对应的表达方式和风险边界。

## 能处理的输入素材

- 参考图、风格图、品牌图、产品图
- 视频截图、视觉样张、UI 截图
- 口播文案、脚本、字幕、SRT
- 产品说明、品牌资料、活动信息
- 目标平台、时长、比例、受众等制作约束

## 工作方式

每一轮只确认一个关键决策：

1. Agent A 提出当前问题，并给出 3-4 个可选方案。
2. 每个方案包含优点、缺点、适合场景。
3. Agent A 给出专业建议。
4. Agent B 审核问题和选项是否合理、完整、可执行。
5. 系统给出本轮建议。
6. 用户回复 `A / B / C / D`，或回复 `同意` 采用建议。

所有关键需求确认完成后，Agent C 才会输出完整 PRD。

## 最终 PRD 包含

- 项目目标
- 输入素材总结
- 已确认需求总表
- 视频类型与目标用户
- 视频整体定位
- 参考素材视觉语言总结
- 内容结构总结
- Scene-by-scene 分镜需求
- 关键动画节点
- 字幕与屏幕文字规范
- 全片统一视觉规范
- AI 视频工具可执行总提示词
- Negative Prompt / 禁止事项
- 生成后检查清单

## 安装方法

将本仓库克隆或复制到 Codex 的 skills 目录：

```powershell
git clone https://github.com/wantedfast/video-prd-dual-agent.git "$env:USERPROFILE\.codex\skills\video-prd-dual-agent"
```

如果你使用的是其他 `CODEX_HOME`，请复制到对应的 `skills/video-prd-dual-agent` 目录。

## 使用方法

在 Codex 中输入：

```text
Use $video-prd-dual-agent，根据我提供的参考图和脚本，一步一步确认视频 PRD。
```

也可以直接描述任务：

```text
我有一段口播文案和几张参考图，帮我逐步确认 AI 视频生成需求，最后输出 PRD。
```

## 目录结构

```text
video-prd-dual-agent/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/
    └── video-prd-checklist.md
```

## 文件说明

- `SKILL.md`：Skill 的核心触发描述、角色规则、逐轮确认流程和最终 PRD 门槛。
- `references/video-prd-checklist.md`：视频类型识别、素材分析清单、风险边界、问题顺序和最终 PRD 模板。
- `agents/openai.yaml`：Codex UI 展示用 metadata。

## 设计原则

- 每轮只问一个问题，避免一次性收集过多信息。
- Agent A 负责方案设计，Agent B 负责审核和反方评估。
- Agent C 只在需求确认充分后出现。
- 所有建议必须服务于最终视频 PRD。
- 对金融、医疗、教育、科技、广告、情感、剧情等不同内容领域使用不同风险边界。
