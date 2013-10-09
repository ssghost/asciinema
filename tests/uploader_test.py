import json
import bz2
from nose.tools import assert_equal
from .test_helper import Test, FakeAsciicast
from asciinema.uploader import Uploader


class FakeHttpAdapter(object):

    def __init__(self):
        self.url = None
        self.files = None

    def post(self, url, files):
        self.url = url
        self.files = files

        return (200, { 'Content-type': 'text/plain' }, b'success!')


class FakeStdout(object):

    def __init__(self, data=None, timing=None):
        self.data = data or b''
        self.timing = timing or b''


class TestUploader(Test):

    def setUp(self):
        Test.setUp(self)
        self.http_adapter = FakeHttpAdapter()
        self.stdout = FakeStdout(b'data123', b'timing456')
        self.asciicast = FakeAsciicast(cmd='ls -l', title='tit',
                stdout=self.stdout, meta_data={ 'shell': '/bin/sh' })

    def test_upload(self):
        uploader = Uploader(self.http_adapter)

        response_body = uploader.upload('http://api/url', 'a1b2c3', self.asciicast)

        assert_equal(b'success!', response_body)
        assert_equal('http://api/url/api/asciicasts', self.http_adapter.url)
        assert_equal(self._expected_files(), self.http_adapter.files)

    def _expected_files(self):
        return {
            'asciicast[meta]':
                ('meta.json', json.dumps({ 'shell': '/bin/sh',
                                           'user_token': 'a1b2c3' })),
            'asciicast[stdout]':
                ('stdout', bz2.compress(b'data123')),
            'asciicast[stdout_timing]':
                ('stdout.time', bz2.compress(b'timing456'))
        }
