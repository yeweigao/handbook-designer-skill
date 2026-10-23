"""Folio font packaging keeps intermediate static weights addressable by PDF name."""
import os
import sys
import unittest

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "hb", "core"))
import family  # noqa: E402


class FamilyFontTest(unittest.TestCase):
    def test_intermediate_light_weight_gets_a_unique_static_postscript_name(self):
        font = TTFont(os.path.join(REPO, "dev", "fonts", "NotoSansSC-VF.ttf"))
        location = {axis.axisTag: axis.defaultValue for axis in font["fvar"].axes}
        location["wght"] = 250
        static = instancer.instantiateVariableFont(font, location, updateFontNames=False)
        family.name_static_instance(static, "Noto Sans SC", 250)

        self.assertNotIn("fvar", static)
        self.assertEqual(static["OS/2"].usWeightClass, 250)
        self.assertEqual(static["name"].getDebugName(6), "NotoSansSC-250")


if __name__ == "__main__":
    unittest.main()
