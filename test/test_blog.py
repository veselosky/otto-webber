#!/usr/bin/env python
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import os.path

import otto.blog as blog

test_dir = os.path.dirname(__file__)

class BlogTest(unittest.TestCase):

    good_channel = {'title':'The Title', 'subtitle':'The Subtitle'}
    incomplete_channel = {'title':'I got a title!'}
    bad_obj = {'whut':'I got no title!'}
    good_entry = {
            'title':'Entry Title',
            'summary':'The Summary',
            'date': '2011-09-13T00:00:00Z',
            'body': '<h1>I WIN!</h1>',
            }

    def test_load_channel_as_dir(self):
        """load_channel when passed a directory"""
        channel = blog.load_channel(os.path.join(test_dir, 'blog'))
        self.assertEqual(channel['title'], 'Test Title')

    def test_load_channel_as_file(self):
        """load_channel when passed a file"""
        channel = blog.load_channel(os.path.join(test_dir, 'blog', 'channel.json'))
        self.assertEqual(channel['title'], 'Test Title')

    def test_load_channel_invalid_path(self):
        """load_channel when passed an invalid path"""
        with self.assertRaises(ValueError):
            blog.load_channel(os.path.join(test_dir, 'does_not_exist'))

    def test_load_entry_markdown(self):
        """Markdown metadata and content parsed to dict."""
        entry = blog.load_entry_markdown(os.path.join(test_dir, 'blog', 'entry.md'))
        self.assertEqual(entry['title'], 'Test Entry')
        self.assertEqual(entry['summary'], 'This is a test entry.')
        self.assertEqual(entry['date'], '2011-09-13T11:00:00+00:00')
        self.assertTrue( entry['content'].startswith('<p>Lorem ipsum'))

if __name__ == '__main__':
    unittest.main()
