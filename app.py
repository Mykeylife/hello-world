"""
Flask Application - Social Media API Server
Entry point for Railway deployment
"""

import os
import json
import sqlite3  # Added for database logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from social_media_api import (
    SocialMediaManager,
    TwitterAPI,
    InstagramAPI,
    FacebookAPI,
    LinkedInAPI,
    TikTokAPI
)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Database file path configuration
DB_FILE = 'social_media.db'

def initialize_database():
    """Initializes local metadata control tables using the migration script."""
    try:
        # Check if the database or tables need to be created
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Look for the migration SQL script in your project root
        sql_script_path = 'v1_social_media_logging.sql'
        if os.path.exists(sql_script_path):
            with open(sql_script_path, 'r') as f:
                cursor.executescript(f.read())
            conn.commit()
            print("Database control tables initialized successfully.")
        else:
            print(f"Warning: {sql_script_path} not found. Skipping table auto-creation.")
        
        conn.close()
    except Exception as e:
        print(f"Error initializing local database: {e}")

def log_api_transaction(platform, content, status, response_data):
    """Helper function to log request outcomes into the SQLite control architecture."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # Custom logging parameters to track workflow activity
        cursor.execute(
            "INSERT INTO api_logs (platform, content, status, response) VALUES (?, ?, ?, ?)",
            (platform, content, status, json.dumps(response_data))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Failed to log transaction to database: {e}")

# Run database setup before loading platforms
initialize_database()

# Initialize Social Media Manager
manager = SocialMediaManager()

# Configure platforms from environment variables
def initialize_platforms():
    """Initialize all social media platforms with environment variables"""
    try:
        # Twitter
        if all([os.getenv('TWITTER_API_KEY'), os.getenv('TWITTER_ACCESS_TOKEN')]):
            manager.add_platform('twitter', TwitterAPI({
                'api_key': os.getenv('TWITTER_API_KEY'),
                'api_secret': os.getenv('TWITTER_API_SECRET', ''),
                'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
                'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')
            }))

        # Instagram
        if all([os.getenv('INSTAGRAM_API_KEY'), os.getenv('INSTAGRAM_ACCOUNT_ID')]):
            manager.add_platform('instagram', InstagramAPI({
                'api_key': os.getenv('INSTAGRAM_API_KEY'),
                'instagram_account_id': os.getenv('INSTAGRAM_ACCOUNT_ID')
            }))

        # Facebook
        if all([os.getenv('FACEBOOK_API_KEY'), os.getenv('FACEBOOK_PAGE_ID')]):
            manager.add_platform('facebook', FacebookAPI({
                'api_key': os.getenv('FACEBOOK_API_KEY'),
                'page_id': os.getenv('FACEBOOK_PAGE_ID')
            }))

        # LinkedIn
        if all([os.getenv('LINKEDIN_API_KEY'), os.getenv('LINKEDIN_PERSON_URN')]):
            manager.add_platform('linkedin', LinkedInAPI({
                'api_key': os.getenv('LINKEDIN_API_KEY'),
                'person_urn': os.getenv('LINKEDIN_PERSON_URN')
            }))

        # TikTok
        if all([os.getenv('TIKTOK_API_KEY'), os.getenv('TIKTOK_ACCESS_TOKEN')]):
            manager.add_platform('tiktok', TikTokAPI({
                'api_key': os.getenv('TIKTOK_API_KEY'),
                'access_token': os.getenv('TIKTOK_ACCESS_TOKEN')
            }))

    except Exception as e:
        print(f"Error initializing platforms: {e}")

initialize_platforms()

# Routes
@app.route('/', methods=['GET'])
def home():
    """Health Check endpoint"""
    return jsonify({
        "status": "success",
        "message": "Social Media API Server is running!",
        "platforms": list(manager.platforms.keys())
    }), 200

@app.route('/api/status', methods=['GET'])
def status():
    """Get status of all configured platforms"""
    platform_status = manager.get_platform_status()
    return jsonify({
        "status": "success",
        "platforms": platform_status
    }), 200

@app.route('/api/post', methods=['POST'])
def post_to_all():
    """Post content to all configured platforms"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'content' in request body"
            }), 400
            
        content = data.get('content')
        media_url = data.get('media_url')
        
        results = manager.post_to_all(content, media_url)
        
        # Log successful orchestrations across all targeted profiles
        log_api_transaction("all", content, "success", results)
        
        return jsonify({
            "status": "success",
            "data": results
        }), 200
        
    except Exception as e:
        log_api_transaction("all", data.get('content', ''), "failed", {"error": str(e)})
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/post/<platform>', methods=['POST'])
def post_to_platform(platform):
    """Post content to a specific platform"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing 'content' in request body"
            }), 400
            
        content = data.get('content')
        media_url = data.get('media_url')
        
        result = manager.post_to_platform(platform, content, media_url)
        
        if result.get('success'):
            log_api_transaction(platform, content, "success", result)
            return jsonify({
                "status": "success",
                "data": result
            }), 200
        else:
            log_api_transaction(platform, content, "failed", result)
            return jsonify({
                "status": "error",
                "data": result
            }), 400
            
    except Exception as e:
        log_api_transaction(platform, data.get('content', ''), "failed", {"error": str(e)})
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/platforms', methods=['GET'])
def get_platforms():
    """Get list of configured platforms"""
    return jsonify({
        "status": "success",
        "platforms": list(manager.platforms.keys()),
        "count": len(manager.platforms)
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found"
    }), 404

if __name__ == '__main__':
    # Railway passes the port dynamically via an environment variable
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
