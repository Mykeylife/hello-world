import pytest
from unittest.mock import patch, MagicMock
from social_media_api import SocialMediaAPI  # Assumes your core poster class name

def test_credential_validation_loading():
    """Verifies that environment variables load correctly from the configuration schema."""
    with patch('os.getenv') as mock_env:
        mock_env.side_effect = lambda key, default=None: "mock_key_123" if "TWITTER" in key else None
        api = SocialMediaAPI()
        assert api.has_twitter_auth() is True
        assert api.has_linkedin_auth() is False

def test_multi_platform_posting_success():
    """Tests that a text-and-media post loops through active profiles cleanly."""
    api = SocialMediaAPI()
    
    # Mocking external API responses safely offline
    api.post_to_twitter = MagicMock(return_value={"status": "success", "post_id": "tw_991"})
    api.post_to_linkedin = MagicMock(return_value={"status": "success", "post_id": "li_442"})
    
    platforms = ["twitter", "linkedin"]
    results = api.broadcast_content(message="Testing automated API infrastructure portfolios!", targets=platforms)
    
    assert results["twitter"]["status"] == "success"
    assert results["linkedin"]["status"] == "success"
    assert api.post_to_twitter.call_count == 1
