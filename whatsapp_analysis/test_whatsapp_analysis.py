from unittest import TestCase


class TestWhatsApp(TestCase):
    def test_split_msg(self):
        msg = '19.5.2016, 21:01 - bob: hi'
        expected_speaker = 'bob'

    def test_split_msg_content_only(self):
        pass