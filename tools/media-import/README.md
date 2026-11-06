# Legacy Media video adapter

`video_blocks.py` converts one YouTube iframe to the shared editorial `video`
contract. It is a pure, local helper: no HTTP calls, uploads, CMS writes or video
downloads. It does not decide the Media publication mode, source, date or author.

Call `convert_iframe(attrs, source_url=..., source_path=..., material_title=...)`
when the full Media importer visits that iframe in the HTML tree. Insert the
returned block immediately at that position among the converted text blocks.
Use a stable source path; block IDs follow the existing article converter's
`src-<sha256(source_url|source_path)[:24]>` convention.

`scan_iframes` is an ordered audit, not a replacement for full text conversion.
It records source offsets and failed occurrences so loss cannot be mistaken for
successful migration. Source links in `<a>` never substitute for an iframe's ID.

Supported URL forms: YouTube watch, short share link, embed, shorts, live and
youtube-nocookie embed. `start`, `t`, `end`, legacy `start`/`endtime` attributes
preserve timing in seconds. End is absolute from the beginning of the video.
Unknown playback parameters, active playlist/loop/autoplay settings, conflicting
timings, non-YouTube sources and executable attributes raise
`VideoConversionError` for the migration register. The player uses normal
controls without automatic playback. URL tracking parameters are not stored.

Use the meaningful iframe title when available, otherwise the material title.
Only provider, ID, title and optional start/end enter the saved block; original
URLs/attributes remain in the separate source evidence. Video availability must
still be checked during import/acceptance: parsing a URL does not verify playback.

Run unit checks:

```powershell
python -m unittest discover -s tools/media-import -p 'test_*.py' -v
```

Audit locally saved old API responses (the output directory must exist):

```powershell
python tools/media-import/video_blocks.py --sources-dir outputs/media-import-research-2026-11-06/sources --output outputs/media-video-block-2026-11-06/legacy-video-audit.json
```

2026-11-06 source fixture audit: 29 materials, 23 iframes, all 23 converted, zero
conversion issues. No materials were imported by this audit. The historical
October Blog/case converter is unchanged; the forthcoming Media importer must
call this helper explicitly.

YouTube's [player parameters](https://developers.google.com/youtube/player_parameters)
define absolute end timing and require a player viewport of at least 200 × 200.
