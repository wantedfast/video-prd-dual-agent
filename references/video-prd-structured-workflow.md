# Structured Video PRD Workflow

`video-prd.project.json` is the single source of truth. Agents must update this data model; they must not maintain independent Markdown tables that can drift from the SRT, Shot timing, asset list, Motion timeline, sound effects, or facts.

## Canonical files

- `video-prd.project.json`: editable source of truth, copied from `assets/video-prd-project.template.json`.
- Original `.srt`: immutable timing and narration source.
- `video-prd.validation.json`: machine-readable pre-review report.
- `video-prd.md`: generated delivery document. Never edit this file by hand.

## Commands

Run commands from the skill directory or use an absolute script path.

```powershell
python scripts/video_prd_pipeline.py sync-srt video-prd.project.json
python scripts/video_prd_pipeline.py validate video-prd.project.json --report video-prd.validation.json
python scripts/video_prd_pipeline.py build video-prd.project.json --output video-prd.md --report video-prd.validation.json
```

`build` refuses to render when an error exists. Use `--strict` when warnings such as an unregistered number must also block delivery.

## Data ownership

| Data | Owner | Required fields / rule |
| --- | --- | --- |
| `meta`, `decisions`, `execution` | Controller after Agent A/B reconciliation | objective, audience, platform, duration, style, risk boundary, agent evidence |
| `subtitles` | `sync-srt` only | exact ID, start, end, and text copied from the original SRT |
| `scenes` | Scene Planner | unique ID, continuous range, purpose, message, asset IDs |
| `shots[].visual`, `prompt`, `transition` | Scene Director | executable visual, camera, transition, HyperFrame prompt |
| `assets` | Visual Asset Agent | unique ID, source/generated status, path, purpose, processing/generation instruction |
| `shots[].motion`, `shots[].sfx` | Motion Agent | Shot-relative timing, object, action/sound, duration/character, purpose |
| `shots[].screen_text`, `rules` | Text Agent | screen copy, banned terms, highlights, disclaimers |
| `facts`, `shots[].fact_refs` | Controller + source owner | one canonical display string and source asset for each critical number |
| `render` | Controller | global visual, subtitle, prompt, risk and post-check policies |

Every Shot must have all fields declared in the template contract, including empty arrays for intentionally unused `motion`, `sfx`, `fact_refs`, or `risks`. This makes omissions distinguishable from deliberate decisions.

## Parallel execution graph

Only true dependencies are serialized. The Controller may dispatch independent roles at the same time, but merges results into the canonical JSON after each wave.

```text
Material intake + SRT sync
        |
Agent A -> Agent B -> Agent A reconciliation
        |
Scene Planner
        |
Scene Director (Shot skeleton)
        |
        +----------------------+----------------------+
        |                      |                      |
Visual Asset Agent       Text Agent        Controller fact registry
        |
Motion Agent (Motion + crisp SFX)
        |
Structured merge -> automated preflight -> Markdown build -> PRD Reviewer
```

The Text Agent can work from the Shot skeleton while the Visual Asset Agent resolves paths and generation briefs. Fact registration can run alongside both. Motion Agent starts after asset IDs and visual objects are stable, so its timeline does not target renamed objects.

## Automated pre-review gates

The validator reports a code, severity, location, and explanation for each problem.

- SRT consistency: embedded subtitles must exactly match cue ID, timing, and text from the original file.
- Time continuity: Shots must cover `0..duration_ms` with no gap or overlap and remain inside their Scene.
- SRT coverage: every subtitle cue must belong to exactly one Shot.
- Required fields and references: Scene, Shot, subtitle, asset, and fact IDs must exist and be unique.
- Asset paths: every `status: source` asset must resolve to a real file. Generated/planned assets may omit a path until production.
- Forbidden terms and disclaimers: banned terms are scanned; required disclaimers must appear in the final Shot.
- Numeric conflicts: critical numbers live in `facts`; a Shot must use the canonical `display` string and required context. Unregistered numbers generate warnings.

The automated gate detects structural and deterministic conflicts. The PRD Reviewer still judges narrative logic, visual feasibility, pacing, hierarchy, compliance nuance, and whether the generated Markdown faithfully communicates the structured source.

## Fact example

```json
{
  "id": "fact_t5_win_rate",
  "display": "88.95%",
  "source_asset_id": "asset_kpi",
  "required_context": ["T+5", "最高价胜率"]
}
```

The Shot that cites `fact_t5_win_rate` must list it in `fact_refs` and include `88.95%`, `T+5`, and `最高价胜率` in its visual, screen text, or prompt.
