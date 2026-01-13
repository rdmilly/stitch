import httpx
from datetime import datetime, timedelta
from app.core.config import settings

class LinkedInService:
    AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    API_URL = "https://api.linkedin.com/v2"
    
    @classmethod
    def get_auth_url(cls, state: str) -> str:
        params = {
            "response_type": "code",
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
            "state": state,
            "scope": "openid profile email w_member_social"
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{cls.AUTH_URL}?{query}"
    
    @classmethod
    async def exchange_code(cls, code: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(cls.TOKEN_URL, data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
                "client_id": settings.LINKEDIN_CLIENT_ID,
                "client_secret": settings.LINKEDIN_CLIENT_SECRET
            })
            return resp.json()
    
    @classmethod
    async def get_profile(cls, access_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.linkedin.com/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            return resp.json()
    
    @classmethod
    async def create_post(cls, access_token: str, user_urn: str, text: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{cls.API_URL}/ugcPosts",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "X-Restli-Protocol-Version": "2.0.0"
                },
                json={
                    "author": user_urn,
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {"text": text},
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
                }
            )
            return resp.json()
