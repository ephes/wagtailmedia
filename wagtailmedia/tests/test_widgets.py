import importlib

from unittest.mock import patch

from django.test import TestCase

from wagtailmedia import widgets


class WidgetTests(TestCase):
    @patch.dict("sys.modules", {"wagtail.core.telepath": None})
    def test_import_telepath_older_wagtail_versions_workaround(self):
        importlib.reload(widgets)
        from wagtailmedia.widgets import WidgetAdapter

        self.assertFalse(hasattr(WidgetAdapter, "js_constructor"))

    def test_get_value_data(self):
        class StubModelManager:
            def get(self, pk):
                return StubMediaModel(pk)

        class StubMediaModel:
            objects = StubModelManager()

            def __init__(self, pk):
                self.pk = pk
                self.id = pk
                self.title = "foo"

        test_data = [
            # (input value, expected output value)
            (None, None),
            (3, {"id": 3, "title": "foo", "edit_link": "/edit/3/"}),
            (StubMediaModel(3), {"id": 3, "title": "foo", "edit_link": "/edit/3/"}),
        ]

        media_chooser = widgets.AdminMediaChooser()
        media_chooser.media_model = StubMediaModel
        for input_value, expected_output in test_data:
            with patch("wagtailmedia.widgets.reverse", return_value="/edit/3/"):
                actual = media_chooser.get_value_data(input_value)
                self.assertEqual(expected_output, actual)

    def test_render_html_wagtail_version(self):
        """
        Assert that widget.get_value_data is called for older wagtail versions
        but not for newer ones.
        """
        wagtail_versions = [
            # (wagtail_version, get_value_data.called)
            ((2, 11, 8, "final", 1), True),
            ((2, 13, 4, "final", 1), False),
        ]
        media_chooser = widgets.AdminMediaChooser()

        for wagtail_version, expected_called in wagtail_versions:
            with patch("wagtailmedia.widgets.WAGTAIL_VERSION", new=wagtail_version):
                with patch.object(media_chooser, "get_value_data") as get_value_data:
                    _ = media_chooser.render_html("foo", None, {})
                    self.assertEqual(expected_called, get_value_data.called)
