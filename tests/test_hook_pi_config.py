import os
import subprocess

from .basetest import HookTest

mock_config_txt = """
# For more options and information see
# http://www.raspberrypi.org/documentation/configuration/config-txt.md
# Some settings may impact device functionality. See link above for details

# uncomment if you get no picture on HDMI for a default "safe" mode
#hdmi_safe=1

# uncomment this if your display has a black border of unused pixels visible
# and your display can output without overscan
#disable_overscan=1

unrelated_options=are-keept
"""

class TestPiConfigFromConfigureHook(HookTest):

    def mock_uboot_config(self, txt):
        self.mock_uboot_config = os.path.join(self.tmp, "config.txt")
        with open(self.mock_uboot_config, "w") as fp:
            fp.write(txt)
        os.environ["TEST_UBOOT_CONFIG"]=self.mock_uboot_config

    def read_mock_uboot_config(self):
        with open(self.mock_uboot_config) as fp:
            content=fp.read()
        return content

    def test_configure_pi_config_uncomment_existing(self):
        self.mock_uboot_config(mock_config_txt)
        self.mock_snapctl("pi-config.disable-overscan", "1")
        expected=mock_config_txt.replace("#disable_overscan=1","disable_overscan=1")
        subprocess.check_call(["hooks/configure"])
        self.assertEqual(self.read_mock_uboot_config(), expected)

    def test_configure_pi_config_comment_existing(self):
        self.mock_uboot_config(mock_config_txt+"\navoid_warnings=1\n")
        self.mock_snapctl("pi-config.avoid-warnings", "")
        expected=mock_config_txt+"\n#avoid_warnings=1\n"
        subprocess.check_call(["hooks/configure"])
        self.assertEqual(self.read_mock_uboot_config(), expected)

    def test_configure_pi_config_add_new_option(self):
        self.mock_uboot_config(mock_config_txt)
        self.mock_snapctl("pi-config.framebuffer-depth", "16")
        expected=mock_config_txt+"framebuffer_depth=16\n"
        subprocess.check_call(["hooks/configure"])
        self.assertEqual(self.read_mock_uboot_config(), expected)
        # add again, verify its not added twice but updated
        self.mock_snapctl("pi-config.framebuffer-depth", "32")
        expected=mock_config_txt+"framebuffer_depth=32\n"
        subprocess.check_call(["hooks/configure"])
        self.assertEqual(self.read_mock_uboot_config(), expected)
