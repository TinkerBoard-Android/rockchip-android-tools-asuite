#!/usr/bin/env python3
#
# Copyright 2018, The Android Open Source Project
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

"""Unittests for common_util."""

import os
import unittest
from unittest import mock

from aidegen.lib import common_util
from aidegen.lib import errors
from aidegen import unittest_constants
from atest import module_info


#pylint: disable=protected-access
#pylint: disable=invalid-name
class AidegenCommonUtilUnittests(unittest.TestCase):
    """Unit tests for common_util.py"""

    @mock.patch.object(common_util, 'get_android_root_dir')
    @mock.patch.object(module_info.ModuleInfo, 'get_module_names')
    @mock.patch.object(module_info.ModuleInfo, 'get_paths')
    @mock.patch.object(module_info.ModuleInfo, 'is_module')
    def test_get_related_paths(self, mock_is_mod, mock_get, mock_names,
                               mock_get_root):
        """Test get_related_paths with different conditions."""
        mock_is_mod.return_value = True
        mock_get.return_value = []
        mod_info = module_info.ModuleInfo()
        self.assertEqual((None, None),
                         common_util.get_related_paths(
                             mod_info, unittest_constants.TEST_MODULE))
        mock_get_root.return_value = unittest_constants.TEST_PATH
        mock_get.return_value = [unittest_constants.TEST_MODULE]
        expected = (unittest_constants.TEST_MODULE, os.path.join(
            unittest_constants.TEST_PATH, unittest_constants.TEST_MODULE))
        self.assertEqual(
            expected, common_util.get_related_paths(
                mod_info, unittest_constants.TEST_MODULE))
        mock_is_mod.return_value = False
        mock_names.return_value = True
        self.assertEqual(
            expected, common_util.get_related_paths(
                mod_info, unittest_constants.TEST_MODULE))

    @mock.patch.object(common_util, 'get_android_root_dir')
    @mock.patch.object(common_util, 'get_related_paths')
    def test_is_target_android_root(self, mock_get_rel, mock_get_root):
        """Test is_target_android_root with different conditions."""
        mock_get_rel.return_value = None, unittest_constants.TEST_PATH
        mock_get_root.return_value = unittest_constants.TEST_PATH
        self.assertTrue(
            common_util.is_target_android_root(
                module_info.ModuleInfo(), [unittest_constants.TEST_MODULE]))
        mock_get_rel.return_value = None, ''
        self.assertFalse(
            common_util.is_target_android_root(
                module_info.ModuleInfo(), [unittest_constants.TEST_MODULE]))

    @mock.patch.object(common_util, 'get_android_root_dir')
    @mock.patch.object(common_util, 'has_build_target')
    @mock.patch('os.path.isdir')
    @mock.patch.object(common_util, 'get_related_paths')
    def test_check_module(self, mock_get, mock_isdir, mock_has_target,
                          mock_get_root):
        """Test if _check_module raises errors with different conditions."""
        mod_info = module_info.ModuleInfo()
        mock_get.return_value = None, None
        with self.assertRaises(errors.FakeModuleError) as ctx:
            common_util._check_module(mod_info, unittest_constants.TEST_MODULE)
            expected = common_util.FAKE_MODULE_ERROR.format(
                unittest_constants.TEST_MODULE)
            self.assertEqual(expected, str(ctx.exception))
        mock_get_root.return_value = unittest_constants.TEST_PATH
        mock_get.return_value = None, unittest_constants.TEST_MODULE
        with self.assertRaises(errors.ProjectOutsideAndroidRootError) as ctx:
            common_util._check_module(mod_info, unittest_constants.TEST_MODULE)
            expected = common_util.OUTSIDE_ROOT_ERROR.format(
                unittest_constants.TEST_MODULE)
            self.assertEqual(expected, str(ctx.exception))
        mock_get.return_value = None, unittest_constants.TEST_PATH
        mock_isdir.return_value = False
        with self.assertRaises(errors.ProjectPathNotExistError) as ctx:
            common_util._check_module(mod_info, unittest_constants.TEST_MODULE)
            expected = common_util.PATH_NOT_EXISTS_ERROR.format(
                unittest_constants.TEST_MODULE)
            self.assertEqual(expected, str(ctx.exception))
        mock_isdir.return_value = True
        mock_has_target.return_value = False
        mock_get.return_value = None, os.path.join(unittest_constants.TEST_PATH,
                                                   'test.jar')
        with self.assertRaises(errors.NoModuleDefinedInModuleInfoError) as ctx:
            common_util._check_module(mod_info, unittest_constants.TEST_MODULE)
            expected = common_util.NO_MODULE_DEFINED_ERROR.format(
                unittest_constants.TEST_MODULE)
            self.assertEqual(expected, str(ctx.exception))
        self.assertEqual(common_util._check_module(mod_info, '', False), False)
        self.assertEqual(common_util._check_module(mod_info, 'nothing', False),
                         False)

    @mock.patch.object(common_util, '_check_module')
    def test_check_modules(self, mock_check):
        """Test _check_modules with different module lists."""
        mod_info = module_info.ModuleInfo()
        common_util._check_modules(mod_info, [])
        self.assertEqual(mock_check.call_count, 0)
        common_util._check_modules(mod_info, ['module1', 'module2'])
        self.assertEqual(mock_check.call_count, 2)
        target = 'nothing'
        mock_check.return_value = False
        self.assertEqual(common_util._check_modules(mod_info, [target], False),
                         False)

    @mock.patch.object(common_util, 'get_android_root_dir')
    def test_get_abs_path(self, mock_get_root):
        """Test get_abs_path handling."""
        mock_get_root.return_value = unittest_constants.TEST_DATA_PATH
        self.assertEqual(unittest_constants.TEST_DATA_PATH,
                         common_util.get_abs_path(''))
        test_path = os.path.join(unittest_constants.TEST_DATA_PATH, 'test.jar')
        self.assertEqual(test_path, common_util.get_abs_path(test_path))
        self.assertEqual(test_path, common_util.get_abs_path('test.jar'))

    def test_is_target(self):
        """Test is_target handling."""
        self.assertEqual(
            common_util.is_target('packages/apps/tests/test.a', ['.so', '.a']),
            True)
        self.assertEqual(
            common_util.is_target('packages/apps/tests/test.so', ['.so', '.a']),
            True)
        self.assertEqual(
            common_util.is_target('packages/apps/tests/test.jar',
                                  ['.so', '.a']), False)


if __name__ == '__main__':
    unittest.main()
