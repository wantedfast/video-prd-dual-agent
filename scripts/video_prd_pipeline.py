#!/usr/bin/env python3
"""Validate one canonical video-PRD JSON file and render deterministic Markdown."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable


SRT_TIME_RE = re.compile(
    r"^(?P<start>\d{2}:\d{2}:\d{2}[,.]\d{3})\s+-->\s+"
    r"(?P<end>\d{2}:\d{2}:\d{2}[,.]\d{3})(?:\s+.*)?$"
)
NUMBER_RE = re.compile(r"(?<![\w.])[-+]?\d+(?:\.\d+)?(?:%|％|倍|万|亿|元|天|笔|个)?")
REQUIRED_SHOT_KEYS = (
    "id", "scene_id", "start_ms", "end_ms", "srt_ids", "narration", "visual",
    "asset_ids", "motion", "sfx", "screen_text", "fact_refs", "prompt", "risks",
)
PRD_SECTIONS = (
    "0. 多 Agent 执行摘要", "1. 项目目标", "2. 输入素材分析", "3. 需求决策总表",
    "4. 视频定位", "5. Scene 总览", "6. Scene-by-Scene 结构",
    "7. Shot-by-Shot 分镜 PRD", "7A. 视觉包装素材 PRD", "8. Motion 动画时间轴",
    "9. 字幕与关键词高亮规则", "10. 视觉语言", "11. 统一视觉规范",
    "12. AI 视频生成总提示词", "13. Negative Prompt / 禁止事项",
    "14. 风险与合规检查", "15. 生成后检查清单",
)


@dataclass
class Issue:
    level: str
    code: str
    message: str
    location: str = ""


def read_text(path: Path) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"无法识别文本编码：{path}")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(read_text(path))
    if not isinstance(value, dict):
        raise ValueError("项目文件根节点必须是 JSON object")
    return value


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_time(value: str) -> int:
    value = value.replace(".", ",")
    hours, minutes, rest = value.split(":")
    seconds, millis = rest.split(",")
    return (((int(hours) * 60) + int(minutes)) * 60 + int(seconds)) * 1000 + int(millis)


def timecode(ms: int) -> str:
    ms = int(ms)
    hours, rem = divmod(ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    seconds, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"


def parse_srt(path: Path) -> list[dict[str, Any]]:
    text = read_text(path).replace("\r\n", "\n").replace("\r", "\n").strip()
    cues: list[dict[str, Any]] = []
    for block in re.split(r"\n{2,}", text):
        lines = [line.rstrip() for line in block.split("\n")]
        if len(lines) < 2:
            continue
        if SRT_TIME_RE.match(lines[0]):
            cue_id, timing_line, body = str(len(cues) + 1), lines[0], lines[1:]
        else:
            cue_id, timing_line, body = lines[0].strip(), lines[1], lines[2:]
        match = SRT_TIME_RE.match(timing_line.strip())
        if not match:
            raise ValueError(f"SRT 时间行无效：{timing_line}")
        cues.append({
            "id": cue_id,
            "start_ms": parse_time(match.group("start")),
            "end_ms": parse_time(match.group("end")),
            "text": "\n".join(body).strip(),
        })
    if not cues:
        raise ValueError(f"SRT 中没有可读取的字幕：{path}")
    return cues


def resolve_path(project_path: Path, raw: str) -> Path:
    path = Path(raw).expanduser()
    return path if path.is_absolute() else (project_path.parent / path).resolve()


def walk_text(value: Any, location: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield location, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from walk_text(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_text(child, f"{location}[{index}]")


def duplicate_ids(items: list[dict[str, Any]]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in items:
        item_id = str(item.get("id", ""))
        if item_id in seen:
            duplicates.add(item_id)
        seen.add(item_id)
    return duplicates


def validate_project(project: dict[str, Any], project_path: Path) -> tuple[list[Issue], dict[str, Any]]:
    issues: list[Issue] = []

    def error(code: str, message: str, location: str = "") -> None:
        issues.append(Issue("error", code, message, location))

    def warning(code: str, message: str, location: str = "") -> None:
        issues.append(Issue("warning", code, message, location))

    meta = project.get("meta", {})
    if project.get("schema_version") != "1.0":
        error("SCHEMA_VERSION", "schema_version 必须为 1.0", "$.schema_version")
    for key in ("title", "duration_ms", "aspect_ratio", "resolution", "target_tool"):
        if not meta.get(key):
            error("META_REQUIRED", f"meta.{key} 不能为空", f"$.meta.{key}")
    duration = int(meta.get("duration_ms") or 0)

    source = project.get("source", {})
    srt_raw = source.get("srt_path", "")
    srt_cues: list[dict[str, Any]] = []
    if not srt_raw:
        error("SRT_PATH", "source.srt_path 不能为空", "$.source.srt_path")
    else:
        srt_path = resolve_path(project_path, srt_raw)
        if not srt_path.is_file():
            error("SRT_MISSING", f"SRT 文件不存在：{srt_path}", "$.source.srt_path")
        else:
            try:
                srt_cues = parse_srt(srt_path)
            except ValueError as exc:
                error("SRT_PARSE", str(exc), "$.source.srt_path")

    embedded = project.get("subtitles", [])
    if srt_cues:
        if len(embedded) != len(srt_cues):
            error("SRT_COUNT", f"结构化字幕 {len(embedded)} 条，原 SRT {len(srt_cues)} 条", "$.subtitles")
        for index, actual in enumerate(srt_cues):
            if index >= len(embedded):
                break
            expected = embedded[index]
            for key in ("id", "start_ms", "end_ms", "text"):
                if str(expected.get(key, "")) != str(actual[key]):
                    error(
                        "SRT_MISMATCH",
                        f"第 {index + 1} 条字幕的 {key} 与原 SRT 不一致：{expected.get(key)!r} != {actual[key]!r}",
                        f"$.subtitles[{index}].{key}",
                    )

    assets = project.get("assets", [])
    asset_ids = {str(item.get("id", "")) for item in assets}
    for dup in duplicate_ids(assets):
        error("ASSET_DUPLICATE", f"素材 ID 重复：{dup}", "$.assets")
    for index, asset in enumerate(assets):
        if not asset.get("id") or not asset.get("type"):
            error("ASSET_REQUIRED", "素材必须包含 id 和 type", f"$.assets[{index}]")
        status = asset.get("status", "source")
        raw_path = asset.get("path", "")
        if status == "source":
            if not raw_path:
                error("ASSET_PATH", "源素材必须提供 path", f"$.assets[{index}].path")
            elif not resolve_path(project_path, raw_path).is_file():
                error("ASSET_MISSING", f"素材路径不存在：{resolve_path(project_path, raw_path)}", f"$.assets[{index}].path")

    scenes = project.get("scenes", [])
    shots = project.get("shots", [])
    scene_by_id = {str(item.get("id", "")): item for item in scenes}
    subtitle_ids = {str(item.get("id", "")) for item in embedded}
    subtitle_by_id = {str(item.get("id", "")): item for item in embedded}
    for collection_name, collection in (("scenes", scenes), ("shots", shots), ("subtitles", embedded)):
        for dup in duplicate_ids(collection):
            error("ID_DUPLICATE", f"{collection_name} ID 重复：{dup}", f"$.{collection_name}")

    ordered_shots = sorted(shots, key=lambda item: (int(item.get("start_ms", 0)), str(item.get("id", ""))))
    previous_end = 0
    covered_srt: list[str] = []
    for index, shot in enumerate(ordered_shots):
        location = f"$.shots[{shots.index(shot)}]"
        missing = [key for key in REQUIRED_SHOT_KEYS if key not in shot]
        if missing:
            error("SHOT_REQUIRED", f"Shot 缺少字段：{', '.join(missing)}", location)
        shot_id = str(shot.get("id", ""))
        start, end = int(shot.get("start_ms", 0)), int(shot.get("end_ms", 0))
        if end <= start:
            error("SHOT_DURATION", f"{shot_id} 的 end_ms 必须大于 start_ms", location)
        if start != previous_end:
            kind = "空档" if start > previous_end else "重叠"
            error("TIMELINE_CONTINUITY", f"{shot_id} 前存在时间{kind}：{previous_end} -> {start}", location)
        previous_end = max(previous_end, end)
        scene = scene_by_id.get(str(shot.get("scene_id", "")))
        if not scene:
            error("SCENE_REFERENCE", f"{shot_id} 引用了不存在的 Scene", f"{location}.scene_id")
        elif start < int(scene.get("start_ms", 0)) or end > int(scene.get("end_ms", 0)):
            error("SCENE_CONTAINMENT", f"{shot_id} 超出所属 Scene 时间范围", location)
        for asset_id in shot.get("asset_ids", []):
            if str(asset_id) not in asset_ids:
                error("ASSET_REFERENCE", f"{shot_id} 引用了不存在的素材：{asset_id}", f"{location}.asset_ids")
        for cue_id in shot.get("srt_ids", []):
            cue_id = str(cue_id)
            covered_srt.append(cue_id)
            if cue_id not in subtitle_ids:
                error("SRT_REFERENCE", f"{shot_id} 引用了不存在的字幕：{cue_id}", f"{location}.srt_ids")
            else:
                cue = subtitle_by_id[cue_id]
                if int(cue.get("start_ms", 0)) < start or int(cue.get("end_ms", 0)) > end:
                    error("SRT_SHOT_TIMING", f"字幕 {cue_id} 的时间超出 {shot_id}", f"{location}.srt_ids")
        mapped_cues = [subtitle_by_id[str(cue_id)] for cue_id in shot.get("srt_ids", []) if str(cue_id) in subtitle_by_id]
        expected_narration = "\n".join(str(cue.get("text", "")) for cue in mapped_cues)
        if mapped_cues and str(shot.get("narration", "")) != expected_narration:
            error("SRT_NARRATION", f"{shot_id} 的 narration 与所引用 SRT 原文不一致", f"{location}.narration")
        if not shot.get("motion"):
            warning("MOTION_EMPTY", f"{shot_id} 没有 Motion 指令", f"{location}.motion")
        if not shot.get("prompt"):
            error("PROMPT_EMPTY", f"{shot_id} 没有生成提示词", f"{location}.prompt")
    if ordered_shots and previous_end != duration:
        error("TIMELINE_END", f"Shot 时间轴结束于 {previous_end}ms，项目时长为 {duration}ms", "$.shots")
    if not ordered_shots:
        error("SHOTS_EMPTY", "至少需要一个 Shot", "$.shots")

    for cue_id in sorted(subtitle_ids):
        count = covered_srt.count(cue_id)
        if count != 1:
            error("SRT_COVERAGE", f"字幕 {cue_id} 必须被恰好一个 Shot 引用，当前 {count} 次", "$.shots[*].srt_ids")

    ordered_scenes = sorted(scenes, key=lambda item: (int(item.get("start_ms", 0)), str(item.get("id", ""))))
    previous_scene_end = 0
    for index, scene in enumerate(ordered_scenes):
        sid = str(scene.get("id", ""))
        start, end = int(scene.get("start_ms", 0)), int(scene.get("end_ms", 0))
        members = [shot for shot in shots if str(shot.get("scene_id", "")) == sid]
        if end <= start:
            error("SCENE_DURATION", f"{sid} 时间范围无效", f"$.scenes[{index}]")
        if start != previous_scene_end:
            kind = "空档" if start > previous_scene_end else "重叠"
            error("SCENE_CONTINUITY", f"{sid} 前存在时间{kind}：{previous_scene_end} -> {start}", f"$.scenes[{index}]")
        previous_scene_end = max(previous_scene_end, end)
        if not members:
            error("SCENE_EMPTY", f"{sid} 没有关联 Shot", f"$.scenes[{index}]")
    if ordered_scenes and previous_scene_end != duration:
        error("SCENE_END", f"Scene 时间轴结束于 {previous_scene_end}ms，项目时长为 {duration}ms", "$.scenes")

    banned_terms = project.get("rules", {}).get("banned_terms", [])
    generated_shot_text = [{
        "id": shot.get("id"), "visual": shot.get("visual"), "screen_text": shot.get("screen_text"),
        "prompt": shot.get("prompt"), "transition": shot.get("transition"), "risks": shot.get("risks"),
    } for shot in shots]
    for location, value in walk_text({"meta": meta, "scenes": scenes, "shots": generated_shot_text, "render": project.get("render", {})}):
        for term in banned_terms:
            if term and str(term) in value:
                error("BANNED_TERM", f"发现禁词：{term}", location)

    facts = project.get("facts", [])
    fact_by_id: dict[str, dict[str, Any]] = {}
    for dup in duplicate_ids(facts):
        error("FACT_DUPLICATE", f"事实 ID 重复：{dup}", "$.facts")
    for index, fact in enumerate(facts):
        fact_id = str(fact.get("id", ""))
        if not fact_id:
            error("FACT_ID", "事实必须提供 id", f"$.facts[{index}]")
        elif fact_id in fact_by_id and fact_by_id[fact_id] != fact:
            error("FACT_CONFLICT", f"事实 {fact_id} 存在冲突定义", f"$.facts[{index}]")
        fact_by_id[fact_id] = fact
        if not fact.get("display") or not fact.get("source_asset_id"):
            error("FACT_REQUIRED", "事实必须包含 display 和 source_asset_id", f"$.facts[{index}]")
        elif str(fact.get("source_asset_id")) not in asset_ids:
            error("FACT_SOURCE", f"事实 {fact_id} 引用了不存在的源素材", f"$.facts[{index}].source_asset_id")

    canonical_displays = {str(fact.get("display", "")) for fact in facts if fact.get("display")}
    allowed_numbers = {str(item) for item in project.get("rules", {}).get("allowed_unregistered_numbers", [])}
    for index, shot in enumerate(shots):
        location = f"$.shots[{index}]"
        refs = [str(item) for item in shot.get("fact_refs", [])]
        text_blob = " ".join(text for _, text in walk_text({
            "narration": shot.get("narration"), "screen_text": shot.get("screen_text"),
            "visual": shot.get("visual"), "prompt": shot.get("prompt"),
        }))
        for ref in refs:
            fact = fact_by_id.get(ref)
            if not fact:
                error("FACT_REFERENCE", f"Shot 引用了不存在的事实：{ref}", f"{location}.fact_refs")
                continue
            display = str(fact.get("display", ""))
            if display and display not in text_blob:
                error("FACT_DISPLAY", f"Shot 引用 {ref}，但画面/提示词中未出现规范数字“{display}”", location)
            for required in fact.get("required_context", []):
                if str(required) not in text_blob:
                    error("FACT_CONTEXT", f"事实 {ref} 缺少必要上下文：{required}", location)
        for number in NUMBER_RE.findall(text_blob):
            if number not in canonical_displays and number not in allowed_numbers and not re.fullmatch(r"[+-]?[01](?:\.0+)?", number):
                warning("NUMBER_UNREGISTERED", f"未登记数字：{number}；请加入 facts 或 allowed_unregistered_numbers", location)

    required_disclaimers = project.get("rules", {}).get("required_disclaimers", [])
    final_text = " ".join(text for _, text in walk_text(shots[-1] if shots else {}))
    for disclaimer in required_disclaimers:
        if str(disclaimer) not in final_text:
            error("DISCLAIMER_MISSING", f"片尾缺少必需提示：{disclaimer}", "$.shots[-1]")

    summary = {
        "status": "OK" if not any(issue.level == "error" for issue in issues) else "NOT OK",
        "errors": sum(issue.level == "error" for issue in issues),
        "warnings": sum(issue.level == "warning" for issue in issues),
        "checks": {
            "srt_cues": len(srt_cues), "scenes": len(scenes), "shots": len(shots),
            "assets": len(assets), "facts": len(facts), "duration_ms": duration,
        },
        "issues": [asdict(issue) for issue in issues],
    }
    return issues, summary


def md(value: Any, fallback: str = "—") -> str:
    if value is None or value == "":
        return fallback
    if isinstance(value, list):
        return "、".join(str(item) for item in value) or fallback
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(md(cell) for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def bullets(items: Any) -> str:
    if not items:
        return "- —"
    if isinstance(items, str):
        return f"- {items}"
    return "\n".join(f"- {md(item)}" for item in items)


def render_markdown(project: dict[str, Any], validation: dict[str, Any]) -> str:
    meta, source = project["meta"], project.get("source", {})
    agents = project.get("execution", {}).get("agents", [])
    scenes, shots, assets = project.get("scenes", []), project.get("shots", []), project.get("assets", [])
    render = project.get("render", {})
    sections: list[str] = [f"# AI 视频生成 PRD：{meta['title']}", "", f"> 结构化预检：**{validation['status']}**；错误 {validation['errors']}，警告 {validation['warnings']}。", ""]
    sections += ["## 0. 多 Agent 执行摘要", "", table(
        ["角色", "产物", "状态"],
        [[a.get("role"), a.get("artifact"), a.get("status")] for a in agents],
    ), "", f"Reviewer 结论：**{project.get('execution', {}).get('reviewer_verdict', '待审核')}**", ""]
    sections += ["## 1. 项目目标", "", bullets([
        f"目标：{meta.get('objective', '—')}", f"受众：{meta.get('audience', '—')}",
        f"平台：{meta.get('platform', '—')}", f"时长：{timecode(meta['duration_ms'])}",
        f"画幅与分辨率：{meta.get('aspect_ratio')} / {meta.get('resolution')}", f"生成工具：{meta.get('target_tool')}",
    ]), ""]
    sections += ["## 2. 输入素材分析", "", f"SRT：`{source.get('srt_path', '—')}`", "", table(
        ["素材 ID", "类型", "路径/状态", "用途", "不可改事实"],
        [[a.get("id"), a.get("type"), a.get("path") or a.get("status"), a.get("purpose"), a.get("locked_facts")] for a in assets],
    ), ""]
    decisions = project.get("decisions", [])
    sections += ["## 3. 需求决策总表", "", table(
        ["决策项", "最终结论", "依据"], [[d.get("item"), d.get("decision"), d.get("rationale")] for d in decisions],
    ), ""]
    sections += ["## 4. 视频定位", "", bullets([
        f"内容定位：{meta.get('positioning', '—')}", f"视觉风格：{meta.get('style', '—')}",
        f"节奏：{meta.get('pacing', '—')}", f"风险领域：{meta.get('risk_domain', '—')}",
    ]), ""]
    sections += ["## 5. Scene 总览", "", table(
        ["Scene", "时间", "叙事功能", "核心信息", "素材"],
        [[s.get("id"), f"{timecode(s.get('start_ms', 0))}–{timecode(s.get('end_ms', 0))}", s.get("purpose"), s.get("message"), s.get("asset_ids")] for s in scenes],
    ), ""]
    sections += ["## 6. Scene-by-Scene 结构", ""]
    for scene in scenes:
        scene_shots = [s for s in shots if s.get("scene_id") == scene.get("id")]
        sections += [f"### {scene.get('id')} · {scene.get('title', '')}", "", bullets([
            f"时间：{timecode(scene.get('start_ms', 0))}–{timecode(scene.get('end_ms', 0))}",
            f"叙事功能：{scene.get('purpose', '—')}", f"核心信息：{scene.get('message', '—')}",
            f"Shot：{', '.join(str(s.get('id')) for s in scene_shots)}",
        ]), ""]
    sections += ["## 7. Shot-by-Shot 分镜 PRD", ""]
    for shot in shots:
        sections += [f"### {shot.get('id')} · {timecode(shot.get('start_ms', 0))}–{timecode(shot.get('end_ms', 0))}", "", table(
            ["字段", "要求"], [
                ["所属 Scene", shot.get("scene_id")], ["SRT", shot.get("srt_ids")], ["口播", shot.get("narration")],
                ["画面", shot.get("visual")], ["素材", shot.get("asset_ids")], ["屏幕文字", shot.get("screen_text")],
                ["事实引用", shot.get("fact_refs")], ["转场", shot.get("transition")], ["提示词", shot.get("prompt")], ["风险", shot.get("risks")],
            ],
        ), ""]
    sections += ["## 7A. 视觉包装素材 PRD", "", table(
        ["素材 ID", "来源状态", "用途", "生成/处理要求"],
        [[a.get("id"), a.get("status"), a.get("purpose"), a.get("instructions")] for a in assets],
    ), ""]
    motion_rows, sfx_rows = [], []
    for shot in shots:
        for motion in shot.get("motion", []):
            motion_rows.append([shot.get("id"), motion.get("at_ms"), motion.get("object"), motion.get("action"), motion.get("duration_ms"), motion.get("easing"), motion.get("purpose")])
        for sfx in shot.get("sfx", []):
            sfx_rows.append([shot.get("id"), sfx.get("at_ms"), sfx.get("name"), sfx.get("character"), sfx.get("purpose")])
    sections += ["## 8. Motion 动画时间轴", "", table(
        ["Shot", "相对时间(ms)", "对象", "动作", "时长(ms)", "缓动", "目的"], motion_rows,
    ), "", "### 音效时间轴", "", table(["Shot", "相对时间(ms)", "音效", "质感", "目的"], sfx_rows), ""]
    sections += ["## 9. 字幕与关键词高亮规则", "", bullets(render.get("subtitle_rules", [])), "", "关键词高亮：", "", bullets(render.get("keyword_highlights", [])), ""]
    sections += ["## 10. 视觉语言", "", bullets(render.get("visual_language", [])), ""]
    sections += ["## 11. 统一视觉规范", "", bullets(render.get("visual_spec", [])), ""]
    sections += ["## 12. AI 视频生成总提示词", "", render.get("master_prompt", "—"), ""]
    sections += ["## 13. Negative Prompt / 禁止事项", "", bullets(render.get("negative_prompt", [])), ""]
    sections += ["## 14. 风险与合规检查", "", bullets(render.get("risk_checks", [])), "", "必需提示：", "", bullets(project.get("rules", {}).get("required_disclaimers", [])), ""]
    sections += ["## 15. 生成后检查清单", "", bullets(render.get("post_checks", [])), ""]
    return "\n".join(sections).rstrip() + "\n"


def command_sync(args: argparse.Namespace) -> int:
    project_path = Path(args.project).resolve()
    project = load_json(project_path)
    srt_path = resolve_path(project_path, project.get("source", {}).get("srt_path", ""))
    project["subtitles"] = parse_srt(srt_path)
    if project["subtitles"] and not project.get("meta", {}).get("duration_ms"):
        project.setdefault("meta", {})["duration_ms"] = project["subtitles"][-1]["end_ms"]
    save_json(project_path, project)
    print(f"已同步 {len(project['subtitles'])} 条字幕：{project_path}")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    project_path = Path(args.project).resolve()
    project = load_json(project_path)
    issues, summary = validate_project(project, project_path)
    if args.report:
        save_json(Path(args.report).resolve(), summary)
    for issue in issues:
        print(f"[{issue.level.upper()}] {issue.code} {issue.location}: {issue.message}")
    print(f"{summary['status']}: {summary['errors']} error(s), {summary['warnings']} warning(s)")
    return 0 if summary["status"] == "OK" and (not args.strict or summary["warnings"] == 0) else 1


def command_build(args: argparse.Namespace) -> int:
    project_path = Path(args.project).resolve()
    project = load_json(project_path)
    _, summary = validate_project(project, project_path)
    if args.report:
        save_json(Path(args.report).resolve(), summary)
    if summary["status"] != "OK" or (args.strict and summary["warnings"]):
        print(f"NOT OK: Markdown 未生成；{summary['errors']} error(s), {summary['warnings']} warning(s)", file=sys.stderr)
        return 1
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(project, summary), encoding="utf-8")
    print(f"OK: 已生成 {output_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sync = sub.add_parser("sync-srt", help="把原 SRT 精确同步到项目 JSON")
    sync.add_argument("project")
    sync.set_defaults(func=command_sync)
    validate = sub.add_parser("validate", help="运行 Reviewer 前自动检查")
    validate.add_argument("project")
    validate.add_argument("--report", help="写入 JSON 校验报告")
    validate.add_argument("--strict", action="store_true", help="将 warning 也视为失败")
    validate.set_defaults(func=command_validate)
    build = sub.add_parser("build", help="先校验，再生成 Markdown PRD")
    build.add_argument("project")
    build.add_argument("--output", required=True)
    build.add_argument("--report", help="写入 JSON 校验报告")
    build.add_argument("--strict", action="store_true")
    build.set_defaults(func=command_build)
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
