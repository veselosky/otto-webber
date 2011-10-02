#!/usr/bin/env python
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import os.path

import otto.blog as blog

test_dir = os.path.dirname(__file__)

class BlogTest(unittest.TestCase):

    blog_dir = os.path.join(test_dir, 'blog')
    channel_file = os.path.join(test_dir, 'blog', 'channel.json')
    blog_url = 'http://example.com/blog/'
    fake_path = os.path.join(test_dir, 'does_not_exist')

    def test_load_channel_as_dir(self):
        """load_channel when passed a directory"""
        channel = blog.load_channel(self.blog_dir, self.blog_dir, self.blog_url)
        self.assertEqual(channel['title'], 'Test Title')
        self.assertEqual(channel['_path'], '.')
        self.assertEqual(channel['_url'], 'http://example.com/blog/')

    def test_load_channel_as_file(self):
        """load_channel when passed a file"""
        channel = blog.load_channel(self.channel_file, self.blog_dir, self.blog_url)
        self.assertEqual(channel['title'], 'Test Title')
        self.assertEqual(channel['_path'], '.')
        self.assertEqual(channel['_url'], 'http://example.com/blog/')

    def test_load_channel_invalid_path(self):
        """load_channel when passed an invalid path"""
        with self.assertRaises(ValueError):
            blog.load_channel(self.fake_path, test_dir, self.blog_url)

    def test_load_entry_markdown(self):
        """Markdown metadata and content parsed to dict."""
        entry_path = os.path.join(test_dir, 'blog', 'entry.md')
        entry = blog.load_entry_markdown(entry_path)
        self.assertEqual(entry['title'], 'Test Entry')
        self.assertEqual(entry['summary'], 'This is a test entry.')
        self.assertEqual(entry['date'], '2011-09-13T11:00:00+00:00')
        # Path relative to channel, minus extension:
        self.assertEqual(entry['_path'], 'entry')
        self.assertTrue( entry['content'].startswith('<p>Lorem ipsum'))

if __name__ == '__main__':
    unittest.main()
