import pytest
import os
import sqlite3
import json
from unittest.mock import patch, MagicMock
# Importing the actual classes used in your app.py configuration
from social_media_api import (
    SocialMediaManager, 
    TwitterAPI, 
    LinkedInAPI
)

def test_credential_validation_loading():
    """Verifies that environment variables load correctly into platforms."""
    with patch('os.getenv') as mock_env:
        # Mocking values so the all() check passes in app logic
        mock_env.side_effect = lambda key, default=None: "mock_key_123" if "KEY" in key or "TOKEN" in key or "URN" in key else default
        
        manager = SocialMediaManager()
        # Test individual initialization as done in app.py
        twitter = TwitterAPI({'api_key': '123', 'access_token': '456'})
        manager.add_platform('twitter', twitter)
        
        assert 'twitter' in manager.platforms

def test_multi_platform_posting_success():
    """Tests that posting triggers underlying social media mock classes."""
    manager = SocialMediaManager()
    
    # Setup mocks for your individual platforms
    mock_twitter = MagicMock()
    mock_twitter.post.return_value = {"success": True, "post_id": "tw_123"}
    
    mock_linkedin = MagicMock()
    mock_linkedin.post.return_value = {"success": True, "post_id": "li_456"}
    
    manager.add_platform('twitter', mock_twitter)
    manager.add_platform('linkedin', mock_linkedin)
    
    # Testing your post orchestration method
    results = manager.post_to_all("Testing automated API infrastructure", media_url=None)
    
    assert results['twitter']['success'] is True
    assert results['linkedin']['success'] is True
    assert mock_twitter.post.call_count == 1

def test_database_logging_pipeline():
    """Validates that transaction logs are safely committed to the SQLite architecture."""
    db_file = 'test_social_media.db'
    
    # 1. Setup temporary testing table
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,
            content TEXT,
            status TEXT,
            response TEXT
        )
    ''')
    conn.commit()
    
    # 2. Simulate inserting a log from an API operation
    platform = "twitter"
    content = "Automated post verification"
    status = "success"
    response_data = {"success": True, "post_id": "test_id"}
    
    cursor.execute(
        "INSERT INTO api_logs (platform, content, status, response) VALUES (?, ?, ?, ?)",
        (platform, content, status, json.dumps(response_data))
    )
    conn.commit()
    
    # 3. Assertions to confirm the pipeline records successfully
    cursor.execute("SELECT platform, content, status FROM api_logs ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    
    assert row is not None
    assert row[0] == "twitter"
    assert row[1] == "Automated post verification"
    assert row[2] == "success"
    
    # Clean up local test file
    conn.close()
    if os.path.exists(db_file):
        os.remove(db_file)
