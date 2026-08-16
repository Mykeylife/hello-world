"""
Social Media API Integration Module
Unified interface for posting content across multiple social media platforms
Supports: Twitter/X, Instagram, Facebook, LinkedIn, TikTok
"""

import requests
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SocialMediaPlatformBase(ABC):
    """Abstract base class for social media platforms"""
    
    def __init__(self, api_key: str, api_secret: Optional[str] = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.platform_name = self.__class__.__name__
    
    @abstractmethod
    def post_content(self, content: str, **kwargs) -> Dict[str, Any]:
        """Post content to the platform"""
        pass
    
    @abstractmethod
    def post_with_media(self, content: str, media_url: str, **kwargs) -> Dict[str, Any]:
        """Post content with media attachment"""
        pass
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """Validate API credentials"""
        pass


class TwitterAPI(SocialMediaPlatformBase):
    """Twitter/X API Integration"""
    
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str):
        super().__init__(api_key, api_secret)
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.base_url = "https://api.twitter.com/2"
        self.headers = self._get_headers()
    
    def _get_headers(self) -> Dict[str, str]:
        """Generate authorization headers for Twitter API v2"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def validate_credentials(self) -> bool:
        """Validate Twitter API credentials"""
        try:
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=self.headers,
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Twitter credential validation failed: {e}")
            return False
    
    def post_content(self, content: str, **kwargs) -> Dict[str, Any]:
        """Post text content to Twitter"""
        try:
            payload = {"text": content[:280]}  # Twitter character limit
            response = requests.post(
                f"{self.base_url}/tweets",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Twitter post successful: {response.json()}")
                return {
                    "success": True,
                    "platform": "Twitter",
                    "post_id": response.json().get("data", {}).get("id"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": response.text, "platform": "Twitter"}
        except Exception as e:
            logger.error(f"Twitter post failed: {e}")
            return {"success": False, "error": str(e), "platform": "Twitter"}
    
    def post_with_media(self, content: str, media_url: str, **kwargs) -> Dict[str, Any]:
        """Post content with media to Twitter"""
        # Download and upload media to Twitter first
        try:
            media_response = self._upload_media(media_url)
            if not media_response.get("success"):
                return media_response
            
            payload = {
                "text": content[:280],
                "media": {"media_ids": [media_response.get("media_id")]}
            }
            response = requests.post(
                f"{self.base_url}/tweets",
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "platform": "Twitter",
                    "post_id": response.json().get("data", {}).get("id"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": response.text, "platform": "Twitter"}
        except Exception as e:
            logger.error(f"Twitter media post failed: {e}")
            return {"success": False, "error": str(e), "platform": "Twitter"}
    
    def _upload_media(self, media_url: str) -> Dict[str, Any]:
        """Upload media to Twitter"""
        try:
            media_data = requests.get(media_url, timeout=10).content
            # Note: Requires additional setup with Twitter media upload endpoint
            return {"success": True, "media_id": "mock_media_id"}
        except Exception as e:
            logger.error(f"Media upload failed: {e}")
            return {"success": False, "error": str(e)}


class InstagramAPI(SocialMediaPlatformBase):
    """Instagram API Integration (via Meta Business API)"""
    
    def __init__(self, api_key: str, instagram_account_id: str):
        super().__init__(api_key)
        self.instagram_account_id = instagram_account_id
        self.base_url = f"https://graph.instagram.com/v18.0/{instagram_account_id}"
    
    def validate_credentials(self) -> bool:
        """Validate Instagram API credentials"""
        try:
            response = requests.get(
                f"{self.base_url}?fields=id,username&access_token={self.api_key}",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Instagram credential validation failed: {e}")
            return False
    
    def post_content(self, content: str, **kwargs) -> Dict[str, Any]:
        """Post text content to Instagram (captions only, requires media)"""
        logger.warning("Instagram requires media for posts. Use post_with_media instead.")
        return {
            "success": False,
            "error": "Instagram requires media attachment",
            "platform": "Instagram"
        }
    
    def post_with_media(self, content: str, media_url: str, **kwargs) -> Dict[str, Any]:
        """Post content with image/video to Instagram"""
        try:
            payload = {
                "image_url": media_url,
                "caption": content,
                "access_token": self.api_key
            }
            
            response = requests.post(
                f"{self.base_url}/media",
                data=payload,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                media_id = response.json().get("id")
                # Publish the media
                publish_response = requests.post(
                    f"{self.base_url}/media_publish",
                    data={"creation_id": media_id, "access_token": self.api_key},
                    timeout=10
                )
                
                if publish_response.status_code == 200:
                    logger.info(f"Instagram post successful: {media_id}")
                    return {
                        "success": True,
                        "platform": "Instagram",
                        "post_id": media_id,
                        "timestamp": datetime.now().isoformat()
                    }
            
            return {"success": False, "error": response.text, "platform": "Instagram"}
        except Exception as e:
            logger.error(f"Instagram post failed: {e}")
            return {"success": False, "error": str(e), "platform": "Instagram"}


class FacebookAPI(SocialMediaPlatformBase):
    """Facebook API Integration (via Meta Business API)"""
    
    def __init__(self, api_key: str, page_id: str):
        super().__init__(api_key)
        self.page_id = page_id
        self.base_url = f"https://graph.facebook.com/v18.0/{page_id}"
    
    def validate_credentials(self) -> bool:
        """Validate Facebook API credentials"""
        try:
            response = requests.get(
                f"{self.base_url}?fields=id,name&access_token={self.api_key}",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Facebook credential validation failed: {e}")
            return False
    
    def post_content(self, content: str, **kwargs) -> Dict[str, Any]:
        """Post text content to Facebook"""
        try:
            payload = {
                "message": content,
                "access_token": self.api_key
            }
            
            response = requests.post(
                f"{self.base_url}/feed",
                data=payload,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Facebook post successful: {response.json()}")
                return {
                    "success": True,
                    "platform": "Facebook",
                    "post_id": response.json().get("id"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": response.text, "platform": "Facebook"}
        except Exception as e:
            logger.error(f"Facebook post failed: {e}")
            return {"success": False, "error": str(e), "platform": "Facebook"}
    
    def post_with_media(self, content: str, media_url: str, **kwargs) -> Dict[str, Any]:
        """Post content with image to Facebook"""
        try:
            payload = {
                "url": media_url,
                "caption": content,
                "access_token": self.api_key
            }
            
            response = requests.post(
                f"{self.base_url}/photos",
                data=payload,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "platform": "Facebook",
                    "post_id": response.json().get("id"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": response.text, "platform": "Facebook"}
        except Exception as e:
            logger.error(f"Facebook media post failed: {e}")
            return {"success": False, "error": str(e), "platform": "Facebook"}


class LinkedInAPI(SocialMediaPlatformBase):
    """LinkedIn API Integration"""
    
    def __init__(self, api_key: str, person_urn: str):
        super().__init__(api_key)
        self.person_urn = person_urn
        self.base_url = "https://api.linkedin.com/v2"
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def validate_credentials(self) -> bool:
        """Validate LinkedIn API credentials"""
        try:
            response = requests.get(
                f"{self.base_url}/me",
                headers=self._get_headers(),
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"LinkedIn credential validation failed: {e}")
            return False
    
    def post_content(self, content: str, **kwargs) -> Dict[str, Any]:
        """Post text content to LinkedIn"""
        try:
            payload = {
                "author": self.person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": content},
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
            }
            
            response = requests.post(
                f"{self.base_url}/ugcPosts",
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"LinkedIn post successful: {response.json()}")
                return {
                    "success": True,
                    "platform": "LinkedIn",
                    "post_id": response.json().get("id"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": response.text, "platform": "LinkedIn"}
        except Exception as e:
            logger.error(f"LinkedIn post failed: {e}")
            return {"success": False, "error": str(e), "platform": "LinkedIn"}
    
    def post_with_media(self, content: str, media_url: str, **kwargs) -> Dict[str, Any]:
        """Post content with media to LinkedIn"""
        try:
            # Upload asset first
            asset_response = self._upload_asset(media_url)
            if not asset_response.get("success"):
                return asset_response
            
            payload = {
                "author": self.person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": content},
                        "shareMediaCategory": "IMAGE",
                        "media": [{"status": "READY", "media": asset_response.get("asset")}]
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
            }
            
            response = requests.post(
                f"{self.base_url}/ugcPosts",
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                return {
                    "success": True,
                    "platform": "LinkedIn",
                    "post_id": response.json().get("id"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": response.text, "platform": "LinkedIn"}
        except Exception as e:
            logger.error(f"LinkedIn media post failed: {e}")
            return {"success": False, "error": str(e), "platform": "LinkedIn"}
    
    def _upload_asset(self, media_url: str) -> Dict[str, Any]:
        """Upload asset to LinkedIn"""
        try:
            # Simplified asset upload - in production, follow LinkedIn's full asset upload process
            return {"success": True, "asset": media_url}
        except Exception as e:
            logger.error(f"Asset upload failed: {e}")
            return {"success": False, "error": str(e)}


class TikTokAPI(SocialMediaPlatformBase):
    """TikTok API Integration"""
    
    def __init__(self, api_key: str, access_token: str):
        super().__init__(api_key)
        self.access_token = access_token
        self.base_url = "https://open.tiktokapis.com/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def validate_credentials(self) -> bool:
        """Validate TikTok API credentials"""
        try:
            response = requests.get(
                f"{self.base_url}/user/info/",
                headers=self._get_headers(),
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"TikTok credential validation failed: {e}")
            return False
    
    def post_content(self, content: str, **kwargs) -> Dict[str, Any]:
        """Post text content to TikTok (requires media)"""
        logger.warning("TikTok requires video content. Use post_with_media instead.")
        return {
            "success": False,
            "error": "TikTok requires video/media attachment",
            "platform": "TikTok"
        }
    
    def post_with_media(self, content: str, media_url: str, **kwargs) -> Dict[str, Any]:
        """Post video content to TikTok"""
        try:
            payload = {
                "video_url": media_url,
                "caption": content,
                "privacy_level": "PUBLIC"
            }
            
            response = requests.post(
                f"{self.base_url}/video/publish/",
                json=payload,
                headers=self._get_headers(),
                timeout=30  # TikTok uploads can take longer
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"TikTok post successful: {response.json()}")
                return {
                    "success": True,
                    "platform": "TikTok",
                    "post_id": response.json().get("data", {}).get("video_id"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": response.text, "platform": "TikTok"}
        except Exception as e:
            logger.error(f"TikTok post failed: {e}")
            return {"success": False, "error": str(e), "platform": "TikTok"}


class SocialMediaManager:
    """Unified manager for all social media platforms"""
    
    def __init__(self):
        self.platforms: Dict[str, SocialMediaPlatformBase] = {}
    
    def add_platform(self, platform_name: str, platform_instance: SocialMediaPlatformBase) -> None:
        """Add a social media platform"""
        self.platforms[platform_name.lower()] = platform_instance
        logger.info(f"Platform added: {platform_name}")
    
    def post_to_all(self, content: str, media_url: Optional[str] = None) -> Dict[str, Any]:
        """Post content to all configured platforms"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "platforms": {}
        }
        
        for platform_name, platform in self.platforms.items():
            try:
                if not platform.validate_credentials():
                    results["platforms"][platform_name] = {
                        "success": False,
                        "error": "Invalid credentials"
                    }
                    continue
                
                if media_url:
                    result = platform.post_with_media(content, media_url)
                else:
                    result = platform.post_content(content)
                
                results["platforms"][platform_name] = result
            except Exception as e:
                logger.error(f"Failed to post to {platform_name}: {e}")
                results["platforms"][platform_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def post_to_platform(self, platform_name: str, content: str, 
                        media_url: Optional[str] = None) -> Dict[str, Any]:
        """Post content to a specific platform"""
        platform = self.platforms.get(platform_name.lower())
        
        if not platform:
            return {"success": False, "error": f"Platform '{platform_name}' not configured"}
        
        try:
            if not platform.validate_credentials():
                return {"success": False, "error": "Invalid credentials"}
            
            if media_url:
                return platform.post_with_media(content, media_url)
            else:
                return platform.post_content(content)
        except Exception as e:
            logger.error(f"Failed to post to {platform_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_platform_status(self) -> Dict[str, bool]:
        """Get validation status of all platforms"""
        status = {}
        for platform_name, platform in self.platforms.items():
            status[platform_name] = platform.validate_credentials()
        return status


# Example usage and initialization
if __name__ == "__main__":
    # Initialize the manager
    manager = SocialMediaManager()
    
    # Add platforms with credentials (replace with actual credentials)
    # Twitter
    manager.add_platform("twitter", TwitterAPI(
        api_key="YOUR_TWITTER_API_KEY",
        api_secret="YOUR_TWITTER_API_SECRET",
        access_token="YOUR_TWITTER_ACCESS_TOKEN",
        access_token_secret="YOUR_TWITTER_ACCESS_TOKEN_SECRET"
    ))
    
    # Instagram
    manager.add_platform("instagram", InstagramAPI(
        api_key="YOUR_INSTAGRAM_API_KEY",
        instagram_account_id="YOUR_INSTAGRAM_ACCOUNT_ID"
    ))
    
    # Facebook
    manager.add_platform("facebook", FacebookAPI(
        api_key="YOUR_FACEBOOK_API_KEY",
        page_id="YOUR_FACEBOOK_PAGE_ID"
    ))
    
    # LinkedIn
    manager.add_platform("linkedin", LinkedInAPI(
        api_key="YOUR_LINKEDIN_API_KEY",
        person_urn="YOUR_LINKEDIN_PERSON_URN"
    ))
    
    # TikTok
    manager.add_platform("tiktok", TikTokAPI(
        api_key="YOUR_TIKTOK_API_KEY",
        access_token="YOUR_TIKTOK_ACCESS_TOKEN"
    ))
    
    # Example 1: Post text-only content to a single platform
    result = manager.post_to_platform(
        "twitter",
        "Check out my AI project! #AI #Python"
    )
    print("Single Platform Post:", json.dumps(result, indent=2))
    
    # Example 2: Post content with media to all platforms
    results = manager.post_to_all(
        content="AI-powered content generation at its finest! #AI #Tech",
        media_url="https://example.com/image.jpg"
    )
    print("Multi-Platform Post:", json.dumps(results, indent=2))
    
    # Example 3: Check platform status
    status = manager.get_platform_status()
    print("Platform Status:", json.dumps(status, indent=2))
