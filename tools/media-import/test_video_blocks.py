import unittest

from video_blocks import VideoConversionError, convert_iframe, parse_youtube_url, scan_iframes

VIDEO = "rH5xuw_do4k"
URL = "https://www.youtube.com/embed/" + VIDEO


class VideoBlocksTest(unittest.TestCase):
    def test_supported_urls_and_timing(self):
        for url in (URL, "https://youtu.be/" + VIDEO,
                    "https://youtube.com/watch?v=" + VIDEO,
                    "https://m.youtube.com/shorts/" + VIDEO,
                    "https://youtube.com/live/" + VIDEO,
                    "https://www.youtube-nocookie.com/embed/" + VIDEO):
            with self.subTest(url=url):
                self.assertEqual(parse_youtube_url(url)["videoId"], VIDEO)
        self.assertEqual(parse_youtube_url(URL + "?start=62&end=120"),
                         {"provider": "youtube", "videoId": VIDEO, "startSeconds": 62, "endSeconds": 120})
        self.assertEqual(parse_youtube_url("https://youtu.be/" + VIDEO + "?t=1h2m3s")["startSeconds"], 3723)
        self.assertEqual(parse_youtube_url(URL + "#t=42")["startSeconds"], 42)

    def test_reject_unsafe_ambiguous_and_unreviewed_inputs(self):
        for url in ("javascript:alert(1)", "https://evil.test/embed/" + VIDEO,
                    "https://youtube.com.evil.test/embed/" + VIDEO,
                    "https://x@youtube.com/embed/" + VIDEO,
                    "https://youtube.com:443/embed/" + VIDEO,
                    "https://youtube.com/embed/not-an-id", URL + "?start=-1",
                    URL + "?start=1.5", URL + "?start=9007199254740992",
                    URL + "?start=5&end=5", URL + "?end=0",
                    URL + "?t=10&start=20", URL + "?start=1&start=2",
                    URL + "?list=PLAYLIST", URL + "?loop=1", URL + "?autoplay=1",
                    URL + "#other", URL + "?v=xxxxxxxxxxx", URL + "\n"):
            with self.subTest(url=url), self.assertRaises(VideoConversionError):
                parse_youtube_url(url)

    def test_legacy_attributes_title_and_identity(self):
        kwargs = {"source_url": "https://www.actum.com.ua/zmi/example", "source_path": "body.2",
                  "material_title": "Коментар адвоката"}
        block = convert_iframe({"src": URL, "start": "10", "endtime": "90", "title": "YouTube video player"}, **kwargs)
        self.assertEqual(block["content"], {"provider": "youtube", "videoId": VIDEO,
                                         "startSeconds": 10, "endSeconds": 90, "title": "Коментар адвоката"})
        edited = convert_iframe({"src": URL, "title": "Нова назва"}, **kwargs)
        self.assertEqual(block["blockId"], edited["blockId"])
        for attrs in ({"src": URL, "srcdoc": "<script>x</script>"},
                      {"src": URL, "onload": "alert(1)"},
                      {"src": URL, "start": "90", "endtime": "10"},
                      {"src": URL + "?start=1", "start": "2"},
                      {"src": URL, "loop": "true"}):
            with self.subTest(attrs=attrs), self.assertRaises(VideoConversionError):
                convert_iframe(attrs, **kwargs)

    def test_order_offsets_duplicate_ids_and_no_source_href_substitution(self):
        html = ("<p>До <a href='https://youtube.com/watch?v=xxxxxxxxxxx'>Джерело</a></p>\n"
                f"<div><iframe src='{URL}'></iframe></div><p>Між</p>"
                f"<iframe src='{URL}'></iframe><p>Після</p>")
        result = scan_iframes(html, source_url="https://actum.com.ua/zmi/test", material_title="Тема")
        self.assertTrue(result["complete"])
        entries = result["entries"]
        self.assertEqual([e["sourceOffset"] for e in entries], [html.index("<iframe"), html.rindex("<iframe")])
        self.assertNotEqual(entries[0]["block"]["blockId"], entries[1]["block"]["blockId"])
        self.assertEqual([e["block"]["content"]["videoId"] for e in entries], [VIDEO, VIDEO])

    def test_bad_video_retains_failure_and_position(self):
        for html in ("<iframe src='https://evil.test/v'></iframe>",
                     f"<iframe src='{URL}' src='{URL}'></iframe>"):
            result = scan_iframes(html, source_url="test", material_title="Тема")
            self.assertFalse(result["complete"])
            self.assertEqual(result["entries"][0]["sourceOffset"], 0)
            self.assertEqual(result["entries"][0]["issue"]["code"], "VIDEO_REVIEW_REQUIRED")


if __name__ == "__main__":
    unittest.main()
