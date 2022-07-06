# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for glazier.lib.actions.registry."""

from unittest import mock

from absl.testing import absltest
from glazier.lib import constants
from glazier.lib.actions import registry

ROOT = 'HKLM'
PATH = constants.REG_ROOT
NAME = 'some_name'
VALUE = 'some_data'
TYPE = 'REG_SZ'
USE_64 = constants.USE_REG_64
ARGS = [ROOT, PATH, NAME, VALUE, TYPE]


class RegistryTest(absltest.TestCase):

  @mock.patch('glazier.lib.buildinfo.BuildInfo', autospec=True)
  @mock.patch.object(registry.registry, 'set_value', autospec=True)
  def test_add(self, mock_set_value, mock_buildinfo):
    # Mock add registry keys
    ra = registry.RegAdd(ARGS, mock_buildinfo)
    ra.Run()
    mock_set_value.assert_called_with(NAME, VALUE, ROOT, PATH, TYPE, USE_64)

    # Registry error
    mock_set_value.side_effect = registry.registry.Error
    with self.assertRaises(registry.ActionError):
      ra.Run()

  # TODO(b/237812617): Parameterize this test.
  @mock.patch(
      'glazier.lib.buildinfo.BuildInfo', autospec=True)
  @mock.patch.object(registry.registry, 'set_value', autospec=True)
  def test_multi_add(self, mock_set_value, mock_buildinfo):
    ra = registry.RegAdd(ARGS, mock_buildinfo)
    ra.Run()
    mock_set_value.assert_called_with(NAME, VALUE, ROOT, PATH, TYPE, USE_64)

    # Missing arguments
    args = [ROOT, PATH, NAME, VALUE]
    ra = registry.RegAdd(args, mock_buildinfo)
    with self.assertRaises(registry.ActionError):
      ra.Run()

    # Multiple missing arguments
    args = [ARGS, [ROOT, PATH, NAME, VALUE]]
    ra = registry.MultiRegAdd(args, mock_buildinfo)
    with self.assertRaises(registry.ActionError):
      ra.Run()

  @mock.patch(
      'glazier.lib.buildinfo.BuildInfo', autospec=True)
  @mock.patch.object(registry.registry, 'remove_value', autospec=True)
  def test_del(self, mock_remove_value, mock_buildinfo):
    # Variable definition
    args = [ROOT, PATH, NAME]

    # Mock delete registry keys
    rd = registry.RegDel(args, mock_buildinfo)
    rd.Run()
    mock_remove_value.assert_called_with(NAME, ROOT, PATH, USE_64)

    # Registry error
    mock_remove_value.side_effect = registry.registry.Error
    with self.assertRaises(registry.ActionError):
      rd.Run()

  @mock.patch(
      'glazier.lib.buildinfo.BuildInfo', autospec=True)
  @mock.patch.object(registry.registry, 'remove_value', autospec=True)
  def test_multi_del(self, mock_remove_value, mock_buildinfo):
    # Mock delete registry keys
    args = [ROOT, PATH, NAME, False]
    rd = registry.RegDel(args, mock_buildinfo)
    rd.Run()
    mock_remove_value.assert_called_with(NAME, ROOT, PATH, False)

    # Missing arguments
    args = [ROOT, PATH]
    rd = registry.RegDel(args, mock_buildinfo)
    with self.assertRaises(registry.ActionError):
      rd.Run()

    # Multiple missing arguments
    args = [[ROOT, PATH], [ROOT]]
    rd = registry.MultiRegDel(args, mock_buildinfo)
    with self.assertRaises(registry.ActionError):
      rd.Run()

  # TODO(b/237812617): Parameterize this test.
  def test_add_validation(self):
    # List not passed
    r = registry.RegAdd(NAME, None)
    with self.assertRaises(registry.ValidationError):
      r.Validate()

    # Too many args
    r = registry.RegAdd([ROOT, PATH, NAME, NAME, TYPE, True, NAME], None)
    with self.assertRaises(registry.ValidationError):
      r.Validate()

    # Not enough args
    r = registry.RegAdd([PATH, NAME, NAME, TYPE], None)
    with self.assertRaises(registry.ValidationError):
      r.Validate()

    # Type error
    r = registry.RegAdd([ROOT, PATH, NAME, '1', 'REG_DWORD'], None)
    with self.assertRaises(registry.ValidationError):
      r.Validate()

    # Too many keys
    r = registry.RegAdd([
        [ROOT, PATH, NAME, 1, TYPE],
        [ROOT, PATH, NAME, 100, TYPE]], None)
    with self.assertRaises(registry.ValidationError):
      r.Validate()

    # Valid calls
    r = registry.RegAdd([ROOT, PATH, NAME, VALUE, TYPE], None)
    r.Validate()

  def test_multi_add_validation(self):
    # Valid calls
    r = registry.MultiRegAdd([ARGS, [ROOT, PATH, NAME, 100, 'REG_DWORD']], None)
    r.Validate()

  # TODO(b/237812617): Parameterize this test.
  def test_del_validation(self):
    # List not passed
    r = registry.RegDel(NAME, None)
    with self.assertRaises(registry.ValidationError):
      r.Validate()

    # Too many args
    r = registry.RegDel([ROOT, PATH, NAME, VALUE], None)
    with self.assertRaises(registry.ValidationError):
      r.Validate()

    # Not enough args
    r = registry.RegDel([PATH, NAME], None)
    with self.assertRaises(registry.ValidationError):
      r.Validate()

    # Too many keys
    r = registry.RegDel([[ROOT, PATH, NAME], [ROOT, PATH, NAME]], None)
    with self.assertRaises(registry.ValidationError):
      r.Validate()

    # Valid calls
    r = registry.RegDel([ROOT, PATH, NAME], None)
    r.Validate()

  def test_multi_del_validation(self):
    # Valid calls
    r = registry.MultiRegDel([[ROOT, PATH, NAME], [ROOT, PATH, NAME]], None)
    r.Validate()

if __name__ == '__main__':
  absltest.main()
