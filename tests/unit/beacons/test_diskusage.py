# coding: utf-8

# Python libs
from __future__ import absolute_import
from collections import namedtuple

# Salt testing libs
from tests.support.unit import skipIf, TestCase
from tests.support.mock import NO_MOCK, NO_MOCK_REASON, patch, MagicMock, Mock
from tests.support.mixins import LoaderModuleMockMixin

# Salt libs
import salt.beacons.diskusage as diskusage

STUB_DISK_PARTITION = [
    namedtuple(
        'partition',
        'device mountpoint fstype, opts')(
            'tmpfs', '/mnt/tmp', 'tmpfs',
            'rw,nosuid,nodev,relatime,size=10240k'),
    namedtuple(
        'partition',
        'device mountpoint fstype, opts')(
            '/dev/disk0s2', '/', 'hfs',
            'rw,local,rootfs,dovolfs,journaled,multilabel')]
STUB_DISK_USAGE = [namedtuple('usage',
                              'total used free percent')(1000, 500, 500, 50),
                   namedtuple('usage',
                              'total used free percent')(100, 75, 25, 25)]


@skipIf(NO_MOCK, NO_MOCK_REASON)
class DiskUsageBeaconTestCase(TestCase, LoaderModuleMockMixin):
    '''
    Test case for salt.beacons.adb
    '''

    def setup_loader_modules(self):
        return {}

    def test_non_list_config(self):
        config = {}

        ret = diskusage.validate(config)

        self.assertEqual(ret, (False, 'Configuration for diskusage beacon must'
                                      ' be a list.'))

    def test_empty_config(self):
        config = [{}]

        ret = diskusage.validate(config)

        self.assertEqual(ret, (True, 'Valid beacon configuration'))

    def test_diskusage_match(self):
        disk_usage_mock = Mock(side_effect=STUB_DISK_USAGE)
        with patch('psutil.disk_partitions',
                   MagicMock(return_value=STUB_DISK_PARTITION)), \
                patch('psutil.disk_usage', disk_usage_mock):
            config = [{'/': '50%'}]

            ret = diskusage.validate(config)

            self.assertEqual(ret, (True, 'Valid beacon configuration'))

            ret = diskusage.beacon(config)
            self.assertEqual(ret, [{'diskusage': 50, 'mount': '/'}])

    def test_diskusage_nomatch(self):
        disk_usage_mock = Mock(side_effect=STUB_DISK_USAGE)
        with patch('psutil.disk_partitions',
                   MagicMock(return_value=STUB_DISK_PARTITION)), \
                patch('psutil.disk_usage', disk_usage_mock):
            config = [{'/': '70%'}]

            ret = diskusage.validate(config)

            self.assertEqual(ret, (True, 'Valid beacon configuration'))

            ret = diskusage.beacon(config)
            self.assertNotEqual(ret, [{'diskusage': 50, 'mount': '/'}])

    def test_diskusage_match_regex(self):
        disk_usage_mock = Mock(side_effect=STUB_DISK_USAGE)
        with patch('psutil.disk_partitions',
                   MagicMock(return_value=STUB_DISK_PARTITION)), \
                patch('psutil.disk_usage', disk_usage_mock):
            config = [{r'^\/': '50%'}]

            ret = diskusage.validate(config)

            self.assertEqual(ret, (True, 'Valid beacon configuration'))

            ret = diskusage.beacon(config)
            self.assertEqual(ret, [{'diskusage': 50, 'mount': '/'}])
