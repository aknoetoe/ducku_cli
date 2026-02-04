import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from src.use_cases.link_checker import LinkChecker
from src.core.project import Project
from src.core.documentation import DocString


class TestLinkChecker(unittest.TestCase):
    
    def setUp(self):
        self.project = Mock(spec=Project)
        self.project.project_root = Path("/fake/project")
        self.link_checker = LinkChecker(self.project)
    
    def test_extract_links(self):
        """Test URL extraction from text."""
        text = """
        Check out https://example.com for more info.
        Also see http://test.org/path/to/page
        Link in markdown: [Example](https://github.com/user/repo)
        Multiple links: https://google.com and https://stackoverflow.com
        """
        
        links = self.link_checker.extract_links(text)
        
        expected_links = [
            "https://example.com",
            "http://test.org/path/to/page",
            "https://github.com/user/repo",
            "https://google.com",
            "https://stackoverflow.com"
        ]
        
        self.assertEqual(len(links), len(expected_links))
        for expected in expected_links:
            self.assertIn(expected, links)
    
    def test_extract_links_with_punctuation(self):
        """Test that trailing punctuation is removed from URLs."""
        text = """
        Visit https://example.com.
        Check (https://test.org).
        See https://github.com/repo,
        """
        
        links = self.link_checker.extract_links(text)
        
        # Should not include trailing punctuation
        self.assertIn("https://example.com", links)
        self.assertIn("https://test.org", links)
        self.assertIn("https://github.com/repo", links)
    
    def test_no_links(self):
        """Test text with no HTTP links."""
        text = "This is just plain text with no URLs."
        links = self.link_checker.extract_links(text)
        self.assertEqual(len(links), 0)
    
    @patch('urllib.request.urlopen')
    def test_check_link_success(self, mock_urlopen):
        """Test checking a successful link."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        is_accessible, error_msg, http_code = self.link_checker.check_link("https://example.com")
        
        self.assertTrue(is_accessible)
        self.assertEqual(error_msg, "")
        self.assertEqual(http_code, 200)
    
    @patch('urllib.request.urlopen')
    def test_check_link_timeout(self, mock_urlopen):
        """Test checking a link that times out."""
        import socket
        mock_urlopen.side_effect = socket.timeout()
        
        is_accessible, error_msg, http_code = self.link_checker.check_link("https://example.com")
        
        self.assertFalse(is_accessible)
        self.assertEqual(error_msg, "Timeout")
        self.assertIsNone(http_code)
    
    @patch('urllib.request.urlopen')
    def test_check_link_404_error(self, mock_urlopen):
        """Test checking a link that returns 404 error."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "https://example.com", 404, "Not Found", {}, None
        )
        
        is_accessible, error_msg, http_code = self.link_checker.check_link("https://example.com")
        
        self.assertFalse(is_accessible)
        self.assertEqual(error_msg, "HTTP 404")
        self.assertEqual(http_code, 404)
    
    @patch('urllib.request.urlopen')
    def test_check_link_403_error(self, mock_urlopen):
        """Test checking a link that returns 403 error."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "https://example.com", 403, "Forbidden", {}, None
        )
        
        is_accessible, error_msg, http_code = self.link_checker.check_link("https://example.com")
        
        self.assertFalse(is_accessible)
        self.assertEqual(error_msg, "HTTP 403")
        self.assertEqual(http_code, 403)
    
    @patch('urllib.request.urlopen')
    def test_check_link_500_error(self, mock_urlopen):
        """Test checking a link that returns 500 error."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "https://example.com", 500, "Internal Server Error", {}, None
        )
        
        is_accessible, error_msg, http_code = self.link_checker.check_link("https://example.com")
        
        self.assertFalse(is_accessible)
        self.assertEqual(error_msg, "HTTP 500")
        self.assertEqual(http_code, 500)
    
    def test_timeout_is_low(self):
        """Test that timeout is set to a low value for enterprise networks."""
        self.assertLessEqual(self.link_checker.timeout, 5)
        self.assertGreaterEqual(self.link_checker.timeout, 1)


if __name__ == "__main__":
    unittest.main()