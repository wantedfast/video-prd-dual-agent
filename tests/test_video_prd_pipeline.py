import importlib.util
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("video_prd_pipeline", ROOT / "scripts" / "video_prd_pipeline.py")
PIPELINE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = PIPELINE
SPEC.loader.exec_module(PIPELINE)


class VideoPrdPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.srt = self.base / "input.srt"
        self.asset = self.base / "kpi.png"
        self.srt.write_text(
            "1\n00:00:00,000 --> 00:00:01,000\n结果是88.95%\n\n"
            "2\n00:00:01,000 --> 00:00:02,000\n历史不代表未来\n",
            encoding="utf-8",
        )
        self.asset.write_bytes(b"png")
        self.project_path = self.base / "project.json"
        self.project = {
            "schema_version": "1.0",
            "meta": {
                "title": "测试", "objective": "解释数据", "audience": "普通用户", "platform": "视频平台",
                "duration_ms": 2000, "aspect_ratio": "16:9", "resolution": "1920x1080",
                "target_tool": "HyperFrame / HyperFrames", "positioning": "数据解释", "style": "Apple UI",
                "pacing": "清晰", "risk_domain": "finance",
            },
            "source": {"srt_path": str(self.srt)},
            "execution": {"agents": [], "reviewer_verdict": "待审核"},
            "decisions": [],
            "assets": [{
                "id": "asset_kpi", "type": "image", "status": "source", "path": str(self.asset),
                "purpose": "核心指标", "locked_facts": ["88.95%"], "instructions": "原图引用",
            }],
            "facts": [{
                "id": "fact_rate", "display": "88.95%", "source_asset_id": "asset_kpi",
                "required_context": ["T+5", "最高价胜率"],
            }],
            "subtitles": PIPELINE.parse_srt(self.srt),
            "scenes": [{"id": "SC01", "title": "数据", "start_ms": 0, "end_ms": 2000, "purpose": "解释", "message": "结果", "asset_ids": ["asset_kpi"]}],
            "shots": [
                {
                    "id": "SH01", "scene_id": "SC01", "start_ms": 0, "end_ms": 1000, "srt_ids": ["1"],
                    "narration": "结果是88.95%", "visual": "T+5最高价胜率88.95%", "asset_ids": ["asset_kpi"],
                    "motion": [{"at_ms": 0, "object": "指标卡", "action": "淡入", "duration_ms": 300, "easing": "ease-out", "purpose": "聚焦"}],
                    "sfx": [{"at_ms": 0, "name": "玻璃提示音", "character": "清脆、短促", "purpose": "入场"}],
                    "screen_text": ["T+5最高价胜率88.95%"], "fact_refs": ["fact_rate"], "transition": "切换",
                    "prompt": "Apple UI数据卡，T+5最高价胜率88.95%", "risks": [],
                },
                {
                    "id": "SH02", "scene_id": "SC01", "start_ms": 1000, "end_ms": 2000, "srt_ids": ["2"],
                    "narration": "历史不代表未来", "visual": "风险提示", "asset_ids": [], "motion": [], "sfx": [],
                    "screen_text": ["历史不代表未来"], "fact_refs": [], "transition": "淡出", "prompt": "简洁风险提示：历史不代表未来", "risks": ["金融合规"],
                },
            ],
            "rules": {"banned_terms": ["稳赚"], "required_disclaimers": ["历史不代表未来"], "allowed_unregistered_numbers": []},
            "render": {
                "subtitle_rules": ["两行以内"], "keyword_highlights": ["数据"], "visual_language": ["深色"],
                "visual_spec": ["统一圆角"], "master_prompt": "Apple UI", "negative_prompt": ["避免杂乱"],
                "risk_checks": ["不构成投资建议"], "post_checks": ["核对字幕"],
            },
        }
        self.project_path.write_text(json.dumps(self.project, ensure_ascii=False), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_project_and_markdown(self):
        issues, report = PIPELINE.validate_project(self.project, self.project_path)
        self.assertEqual("OK", report["status"], issues)
        markdown = PIPELINE.render_markdown(self.project, report)
        for section in PIPELINE.PRD_SECTIONS:
            self.assertIn(f"## {section}", markdown)
        self.assertIn("清脆、短促", markdown)
        self.assertIn("88.95%", markdown)

    def test_sync_and_build_commands(self):
        self.project["subtitles"] = []
        self.project_path.write_text(json.dumps(self.project, ensure_ascii=False), encoding="utf-8")
        self.assertEqual(0, PIPELINE.command_sync(Namespace(project=str(self.project_path))))
        synced = PIPELINE.load_json(self.project_path)
        self.assertEqual("结果是88.95%", synced["subtitles"][0]["text"])
        output = self.base / "video-prd.md"
        report = self.base / "video-prd.validation.json"
        self.assertEqual(0, PIPELINE.command_build(Namespace(
            project=str(self.project_path), output=str(output), report=str(report), strict=False,
        )))
        self.assertTrue(output.is_file())
        self.assertEqual("OK", PIPELINE.load_json(report)["status"])

    def test_detects_srt_and_timeline_conflicts(self):
        self.project["subtitles"][0]["text"] = "错误字幕"
        self.project["shots"][1]["start_ms"] = 1100
        issues, report = PIPELINE.validate_project(self.project, self.project_path)
        codes = {issue.code for issue in issues}
        self.assertEqual("NOT OK", report["status"])
        self.assertIn("SRT_MISMATCH", codes)
        self.assertIn("TIMELINE_CONTINUITY", codes)

    def test_detects_missing_asset_banned_term_and_fact_context(self):
        self.project["assets"][0]["path"] = str(self.base / "missing.png")
        self.project["shots"][0]["prompt"] = "稳赚，88.95%"
        self.project["shots"][0]["visual"] = "88.95%"
        self.project["shots"][0]["screen_text"] = ["88.95%"]
        issues, _ = PIPELINE.validate_project(self.project, self.project_path)
        codes = {issue.code for issue in issues}
        self.assertTrue({"ASSET_MISSING", "BANNED_TERM", "FACT_CONTEXT"}.issubset(codes))


if __name__ == "__main__":
    unittest.main()
