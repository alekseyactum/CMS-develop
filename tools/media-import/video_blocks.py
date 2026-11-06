"""Pure legacy iframe adapter. No network, CMS writes or video downloads.

Call convert_iframe at the iframe's position while traversing the source DOM;
append the returned block alongside text blocks. Never append all videos at the end.
scan_iframes supplies an ordered audit with source offsets, not a full HTML importer.
"""
from __future__ import annotations

import hashlib
from html.parser import HTMLParser
import re
from urllib.parse import parse_qs, urlsplit

MAX_SAFE_INTEGER = 9007199254740991
VIDEO_ID = re.compile(r"[A-Za-z0-9_-]{11}")
HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be",
         "www.youtu.be", "youtube-nocookie.com", "www.youtube-nocookie.com"}


class VideoConversionError(ValueError):
    """Record in the migration register; never silently omit the source player."""


def seconds(value: str) -> int:
    if re.fullmatch(r"[0-9]+", value):
        result = int(value)
    elif match := re.fullmatch(r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", value):
        if not any(match.groups()):
            raise VideoConversionError("Empty video timing")
        result = sum(int(part or 0) * scale for part, scale in zip(match.groups(), (3600, 60, 1)))
    else:
        raise VideoConversionError("Unsupported video timing")
    if result > MAX_SAFE_INTEGER:
        raise VideoConversionError("Video timing exceeds the contract's safe integer range")
    return result


def parse_youtube_url(value: str) -> dict:
    if not isinstance(value, str) or re.search(r"[\s\\]", value):
        raise VideoConversionError("Invalid video URL")
    try:
        url = urlsplit(value)
        if (url.scheme not in {"https", "http"} or url.hostname not in HOSTS
                or url.username is not None or url.password is not None or url.port is not None):
            raise VideoConversionError("Unsupported video origin")
    except ValueError as error:
        raise VideoConversionError("Invalid video URL") from error
    query = parse_qs(url.query, keep_blank_values=True)
    if url.fragment:
        fragment = parse_qs(url.fragment, keep_blank_values=True)
        if set(fragment) != {"t"} or "t" in query:
            raise VideoConversionError("Unreviewed video fragment")
        query.update(fragment)
    if any(len(values) != 1 for values in query.values()):
        raise VideoConversionError("Ambiguous repeated video parameter")
    # Tracking and deprecated presentation flags are safe to discard. Other
    # playback behaviour (playlist/loop/autoplay, etc.) needs an explicit review.
    ignored = {"si", "feature", "rel", "modestbranding", "showinfo"}
    if set(query) - ignored - {"v", "t", "start", "end"}:
        raise VideoConversionError("Unsupported video playback parameter")
    path = url.path.rstrip("/")
    if url.hostname in {"youtu.be", "www.youtu.be"}:
        video_id = path.removeprefix("/")
    elif url.hostname in {"youtube-nocookie.com", "www.youtube-nocookie.com"}:
        video_id = path.removeprefix("/embed/") if path.startswith("/embed/") else ""
    elif path == "/watch":
        video_id = query.get("v", [""])[0]
    else:
        match = re.fullmatch(r"/(?:embed|shorts|live)/([A-Za-z0-9_-]{11})", path)
        video_id = match[1] if match else ""
    if not VIDEO_ID.fullmatch(video_id):
        raise VideoConversionError("Invalid YouTube video ID")
    if "v" in query and query["v"][0] != video_id:
        raise VideoConversionError("Conflicting video IDs")
    content = {"provider": "youtube", "videoId": video_id}
    for parameter, field in (("start", "startSeconds"), ("t", "startSeconds"), ("end", "endSeconds")):
        if parameter in query:
            timing = seconds(query[parameter][0])
            if field in content and content[field] != timing:
                raise VideoConversionError("Conflicting video start times")
            content[field] = timing
    if "endSeconds" in content and content["endSeconds"] <= content.get("startSeconds", 0):
        raise VideoConversionError("Video end must follow start")
    return content


def convert_iframe(attrs: dict, *, source_url: str, source_path: str, material_title: str) -> dict:
    """Convert one DOM iframe, preserving its deterministic source-based block ID."""
    if "srcdoc" in attrs or any(name.lower().startswith("on") for name in attrs):
        raise VideoConversionError("Executable iframe attributes require review")
    content = parse_youtube_url(attrs.get("src", ""))
    # Legacy TipTap attributes may carry timing outside the URL. endtime=0 means
    # no end limit; positive endtime is measured from the start of the whole video.
    for attribute, field in (("start", "startSeconds"), ("endtime", "endSeconds")):
        value = attrs.get(attribute)
        if value not in (None, "", "0"):
            timing = seconds(value)
            if field in content and content[field] != timing:
                raise VideoConversionError("Conflicting iframe and URL timing")
            content[field] = timing
    for attribute in ("autoplay", "loop", "playlist", "disablekbcontrols", "enableiframeapi"):
        if attrs.get(attribute) not in (None, "", "false", "0"):
            raise VideoConversionError("Unsupported iframe playback behaviour: " + attribute)
    if "endSeconds" in content and content["endSeconds"] <= content.get("startSeconds", 0):
        raise VideoConversionError("Video end must follow start")
    title = " ".join((attrs.get("title") or "").split())
    if not title or title.lower() in {"youtube video player", "youtube", "video player"}:
        title = " ".join(material_title.split())
    if not title:
        raise VideoConversionError("A meaningful video title is required")
    content["title"] = title
    digest = hashlib.sha256((source_url + "|" + source_path).encode("utf-8")).hexdigest()[:24]
    return {"blockId": "src-" + digest, "blockType": "video", "variant": "default", "content": content}


def scan_iframes(source_html: str, *, source_url: str, material_title: str) -> dict:
    """Audit all iframe occurrences in source order, retaining failed positions too."""
    line_offsets = [0]
    for match in re.finditer("\n", source_html):
        line_offsets.append(match.end())

    class Scanner(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.entries = []

        def handle_starttag(self, tag, attributes):
            if tag != "iframe":
                return
            line, column = self.getpos()
            path = f"topic_text.iframe[{len(self.entries)}]"
            item = {"sourcePath": path, "sourceOffset": line_offsets[line - 1] + column}
            try:
                if len(dict(attributes)) != len(attributes):
                    raise VideoConversionError("Duplicate iframe attributes")
                item["block"] = convert_iframe(dict(attributes), source_url=source_url,
                                                source_path=path, material_title=material_title)
            except VideoConversionError as error:
                item["issue"] = {"code": "VIDEO_REVIEW_REQUIRED", "message": str(error)}
            self.entries.append(item)

    scanner = Scanner()
    scanner.feed(source_html)
    scanner.close()
    return {"complete": all("block" in entry for entry in scanner.entries), "entries": scanner.entries}


if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Read-only video conversion audit of saved legacy Media JSON")
    parser.add_argument("--sources-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    materials = []
    for source_file in sorted(args.sources_dir.glob("*.json")):
        source = json.loads(source_file.read_text(encoding="utf-8-sig"))["data"]["news"]
        url = "https://www.actum.com.ua/zmi/" + source["name_page"]
        audit = scan_iframes(source["Blog"]["topic_text"], source_url=url,
                             material_title=source["Blog"]["title"])
        materials.append({"sourceUrl": url, **audit})
    summary = {"materials": len(materials),
               "iframes": sum(len(material["entries"]) for material in materials),
               "converted": sum("block" in entry for material in materials for entry in material["entries"]),
               "issues": sum("issue" in entry for material in materials for entry in material["entries"])}
    args.output.write_text(json.dumps({"summary": summary, "materials": materials}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary))
    raise SystemExit(1 if summary["issues"] or not materials else 0)
