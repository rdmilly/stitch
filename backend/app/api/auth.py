import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt

from app.core.config import settings
from app.core.database import get_db
from app.models.models import User, PlatformConnection, Platform
from app.services.linkedin import LinkedInService

router = APIRouter()

def create_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = None) -> User:
    if not token:
        raise HTTPException(401, "Not authenticated")
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(401, "User not found")
        return user
    except:
        raise HTTPException(401, "Invalid token")

@router.get("/linkedin")
async def linkedin_auth():
    state = str(uuid.uuid4())
    url = LinkedInService.get_auth_url(state)
    return {"url": url, "state": state}

@router.get("/linkedin/callback")
async def linkedin_callback(code: str, state: str = None, db: AsyncSession = Depends(get_db)):
    # Exchange code for token
    token_data = await LinkedInService.exchange_code(code)
    if "error" in token_data:
        raise HTTPException(400, token_data.get("error_description", "OAuth failed"))
    
    access_token = token_data["access_token"]
    
    # Get profile
    profile = await LinkedInService.get_profile(access_token)
    email = profile.get("email")
    if not email:
        raise HTTPException(400, "Could not get email from LinkedIn")
    
    # Find or create user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            email=email,
            name=profile.get("name"),
            avatar_url=profile.get("picture")
        )
        db.add(user)
        await db.flush()
    
    # Save connection
    result = await db.execute(
        select(PlatformConnection).where(
            PlatformConnection.user_id == user.id,
            PlatformConnection.platform == Platform.LINKEDIN
        )
    )
    conn = result.scalar_one_or_none()
    
    if conn:
        conn.access_token = access_token
        conn.expires_at = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 5184000))
        conn.profile_data = profile
    else:
        conn = PlatformConnection(
            user_id=user.id,
            platform=Platform.LINKEDIN,
            platform_user_id=profile.get("sub"),
            access_token=access_token,
            expires_at=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 5184000)),
            profile_data=profile
        )
        db.add(conn)
    
    await db.commit()
    
    # Create JWT and redirect
    jwt_token = create_token(str(user.id))
    return RedirectResponse(f"{settings.FRONTEND_URL}/auth/callback?token={jwt_token}")

@router.get("/me")
async def get_me(token: str, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(db, token)
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "avatar_url": user.avatar_url
    }

@router.get("/connections")
async def get_connections(token: str, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(db, token)
    result = await db.execute(
        select(PlatformConnection).where(PlatformConnection.user_id == user.id)
    )
    connections = result.scalars().all()
    return [{"platform": c.platform.value, "connected": True} for c in connections]
