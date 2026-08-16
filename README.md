# Social Media API - Multi-Platform Content Posting

A comprehensive Python API for posting content across multiple social media platforms simultaneously. Perfect for AI-powered content generation and automation.

## 🚀 Features

- **Multi-Platform Support**: Twitter/X, Instagram, Facebook, LinkedIn, TikTok
- **Unified Interface**: Single API to manage all platforms
- **Text & Media**: Support for text-only and media-rich posts
- **Credential Validation**: Automatic API credential verification
- **Error Handling**: Comprehensive error management and logging
- **Flask REST API**: Easy-to-use HTTP endpoints

## 📋 Prerequisites

- Python 3.8+
- API credentials for desired platforms
- pip (Python package manager)

## 🔧 Installation

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/Mykeylife/hello-world.git
cd hello-world
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your credentials:
```bash
cp .env.example .env
# Edit .env and add your API credentials
```

4. Run the application:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## 🌐 Deployment on Railway

### Step 1: Connect Your Repository
1. Go to [Railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select your `hello-world` repository

### Step 2: Configure Environment Variables
1. Go to your Railway project settings
2. Add variables from `.env.example`:
   - `TWITTER_API_KEY`
   - `INSTAGRAM_API_KEY`
   - `FACEBOOK_API_KEY`
   - `LINKEDIN_API_KEY`
   - `TIKTOK_API_KEY`
   - (and other required credentials)

### Step 3: Deploy
Railway will automatically:
- Detect Python project
- Install dependencies from `requirements.txt`
- Run using the `Procfile` configuration
- Assign a public URL

## 📚 API Endpoints

### 1. Health Check
```
GET /
```
Response:
```json
{
  "status": "success",
  "message": "Social Media API Server is running!",
  "platforms": ["twitter", "instagram", "facebook", "linkedin", "tiktok"]
}
```

### 2. Platform Status
```
GET /api/status
```
Response:
```json
{
  "status": "success",
  "platforms": {
    "twitter": true,
    "instagram": false,
    "facebook": true
  }
}
```

### 3. Post to All Platforms
```
POST /api/post
Content-Type: application/json

{
  "content": "Check out my AI project! #AI #Python",
  "media_url": "https://example.com/image.jpg"  // optional
}
```

### 4. Post to Specific Platform
```
POST /api/post/{platform}
Content-Type: application/json

{
  "content": "Your message here",
  "media_url": "https://example.com/image.jpg"  // optional
}
```

Supported platforms: `twitter`, `instagram`, `facebook`, `linkedin`, `tiktok`

### 5. Get Configured Platforms
```
GET /api/platforms
```
Response:
```json
{
  "status": "success",
  "platforms": ["twitter", "facebook"],
  "count": 2
}
```

## 💻 Usage Examples

### Python Script
```python
from social_media_api import SocialMediaManager, TwitterAPI

manager = SocialMediaManager()
manager.add_platform("twitter", TwitterAPI(
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    access_token="YOUR_ACCESS_TOKEN",
    access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
))

result = manager.post_to_platform(
    "twitter",
    "Hello from my AI project! 🚀"
)
print(result)
```

### cURL
```bash
curl -X POST http://localhost:5000/api/post \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Amazing AI content!",
    "media_url": "https://example.com/image.jpg"
  }'
```

### Python Requests
```python
import requests

response = requests.post(
    'http://localhost:5000/api/post',
    json={
        'content': 'Check out my AI project!',
        'media_url': 'https://example.com/image.jpg'
    }
)

print(response.json())
```

## 🔑 Getting API Credentials

### Twitter/X
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create an app and get API keys
3. Generate access tokens

### Instagram/Facebook
1. Go to [Meta Business Suite](https://business.facebook.com/)
2. Create an app
3. Get your Graph API access token

### LinkedIn
1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Create an app
3. Get your access token and person URN

### TikTok
1. Go to [TikTok Developer](https://developers.tiktok.com/)
2. Create an app
3. Get your access token

## 📝 Project Structure

```
hello-world/
├── app.py                    # Flask application entry point
├── social_media_api.py       # Core API implementation
├── requirements.txt          # Python dependencies
├── Procfile                  # Deployment configuration
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
INSTAGRAM_API_KEY=your_key
# ... add other credentials
PORT=5000
```

## 🐛 Troubleshooting

### Platform Not Posting
1. Check credentials are correct in `.env`
2. Verify platform status: `GET /api/status`
3. Check application logs for errors

### Railway Deployment Failed
1. Ensure `requirements.txt` exists
2. Check `Procfile` is configured correctly
3. Verify environment variables are set in Railway dashboard
4. Check build logs for specific errors

### API Key Errors
- Ensure API keys are not expired
- Verify you have the correct permissions
- Check rate limits haven't been exceeded

## 📊 Response Format

All API responses follow this format:

```json
{
  "status": "success" | "error",
  "message": "Description of result",
  "data": { ... },
  "timestamp": "2024-01-01T12:00:00"
}
```

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements!

## 📄 License

This project is open source and available under the MIT License.

## 💡 Tips for Clients

- **Demonstrate Scale**: Show posting to 5+ platforms simultaneously
- **Error Handling**: Highlight robust error management
- **Flexibility**: Show how easy it is to add new platforms
- **Integration**: Show integration with AI content generators
- **Monitoring**: Use `/api/status` for platform health checks

## 🎯 Next Steps

1. Get API credentials for your desired platforms
2. Add them to Railway environment variables
3. Deploy and test with `POST /api/post`
4. Integrate with your AI content generator
5. Monitor with `/api/status` endpoint

## 📞 Support

For issues or questions:
1. Check the README and examples
2. Review error messages in logs
3. Test endpoints with cURL or Postman

---

**Built with ❤️ for AI-powered social media automation**
