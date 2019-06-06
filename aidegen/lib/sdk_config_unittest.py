#!/usr/bin/env python3
#
# Copyright 2019, The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unittests for checking the jdk is generated in jdk.table.xml.."""

import os
import shutil
import tempfile
import unittest

from aidegen import constant
from aidegen import unittest_constants
from aidegen.lib import sdk_config


# pylint: disable=protected-access
# pylint: disable=invalid-name
class SDKConfigUnittests(unittest.TestCase):
    """Unit tests for sdk_config.py"""
    _JDK_FILE_NAME = 'jdk.table.xml'
    _JDK_SAMPLE = os.path.join(unittest_constants.TEST_DATA_PATH,
                               'jdk_table_xml', 'jdk18.xml')
    _JDK_SAMPLE2 = os.path.join(unittest_constants.TEST_DATA_PATH,
                                'jdk_table_xml', 'jdk_other.xml')
    _JDK_TEMPLATE = os.path.join(constant.AIDEGEN_ROOT_PATH,
                                 'templates', 'jdkTable', 'part.jdk.table.xml')
    _JDK_PATH = os.path.join('/path', 'to', 'android', 'root',
                             'prebuilts', 'jdk', 'jdk8', 'linux-x86')
    _JDK_OTHER_CONTENT = """<application>
  <component name="ProjectJdkTable">
    <jdk version="2">
      <name value="JDK_OTHER" />
      <type value="JavaSDK" />
    </jdk>
  </component>
</application>
"""

    def test_generate_new_sdk_config(self):
        """Test generating new jdk config."""
        expected_content = ''
        tmp_folder = tempfile.mkdtemp()
        config_file = os.path.join(tmp_folder, self._JDK_FILE_NAME)
        try:
            with open(self._JDK_SAMPLE) as sample:
                expected_content = sample.read()
            jdk = sdk_config.SDKConfig(config_file, self._JDK_TEMPLATE,
                                       self._JDK_PATH)
            jdk.generate_jdk_config()
            generated_content = jdk.config_string
            self.assertEqual(generated_content, expected_content)
        finally:
            shutil.rmtree(tmp_folder)

    def test_jdk_config_no_change(self):
        """The config file exists and the JDK18 also exists.

        In this case, there is nothing to do, make sure the config content is
        not changed.
        """
        expected_content = ''
        tmp_folder = tempfile.mkdtemp()
        config_file = os.path.join(tmp_folder, self._JDK_FILE_NAME)
        try:
            with open(self._JDK_SAMPLE) as sample:
                expected_content = sample.read()
            # Reset the content of config file.
            with open(config_file, 'w') as cf:
                cf.write(expected_content)
            jdk = sdk_config.SDKConfig(config_file, self._JDK_TEMPLATE,
                                       self._JDK_PATH)
            jdk.generate_jdk_config()
            generated_content = jdk.config_string
            self.assertEqual(generated_content, expected_content)
        finally:
            shutil.rmtree(tmp_folder)

    def test_append_jdk_config(self):
        """The config file exists, test on the JDK18 does not exist."""
        expected_content = ''
        tmp_folder = tempfile.mkdtemp()
        config_file = os.path.join(tmp_folder, self._JDK_FILE_NAME)
        try:
            with open(self._JDK_SAMPLE2) as sample:
                expected_content = sample.read()
            # Reset the content of config file.
            with open(config_file, 'w') as cf:
                cf.write(self._JDK_OTHER_CONTENT)
            jdk = sdk_config.SDKConfig(config_file, self._JDK_TEMPLATE,
                                       self._JDK_PATH)
            jdk.generate_jdk_config()
            generated_content = jdk.config_string
            self.assertEqual(generated_content, expected_content)
        finally:
            shutil.rmtree(tmp_folder)


if __name__ == '__main__':
    unittest.main()