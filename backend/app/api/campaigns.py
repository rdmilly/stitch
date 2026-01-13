from datetime import datetime
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.models import Campaign, Post, PostStatus, Platform, User, PlatformConnection
from app.api.auth import get_current_user
from app.services.content_generator import content_generator
from app.services.linkedin import LinkedInService

router = APIRouter()

class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    business_context: Optional[dict] = None
    platforms: List[str] = ["linkedin"]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class PostUpdate(BaseModel):
    content: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    status: Optional[str] = None

class GenerateRequest(BaseModel):
    business_name: str
    industry: str = "General"
    goals: str = "Increase engagement"
    target_audience: str = "Professionals"
    tone: str = "Professional"
    weeks: int = 4
    posts_per_week: int = 3

@router.get("")
async def list_campaigns(token: str, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(db, token)
    result = await db.execute(
        select(Campaign)
        .where(Campaign.user_id == user.id)
        .options(selectinload(Campaign.posts))
        .order_by(Campaign.created_at.desc())
    )
    campaigns = result.scalars().all()
    return [{
        "id": str(c.id),
        "name": c.name,
        "description": c.description,
        "platforms": c.platforms,
        "post_count": len(c.posts),
        "created_at": c.created_at.isoformat()
    } for c in campaigns]

@router.post("")
async def create_campaign(data: CampaignCreate, token: str, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(db, token)
    campaign = Campaign(
        user_id=user.id,
        name=data.name,
        description=data.description,
        business_context=data.business_context,
        platforms=data.platforms,
        start_date=data.start_date,
        end_date=data.end_date
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return {"id": str(campaign.id), "name": campaign.name}

@router.get("/{campaign_id}")
async def get_campaign(campaign_id: UUID, token: str, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(db, token)
    result = await db.execute(
        select(Campaign)
        .where(Campaign.id == campaign_id, Campaign.user_id == user.id)
        .options(selectinload(Campaign.posts))
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    return {
        "id": str(campaign.id),
        "name": campaign.name,
        "description": campaign.description,
        "business_context": campaign.business_context,
        "platforms": campaign.platforms,
        "posts": [{
            "id": str(p.id),
            "platform": p.platform.value,
            "content": p.content,
            "scheduled_for": p.scheduled_for.isoformat() if p.scheduled_for else None,
            "status": p.status.value,
            "series_id": p.series_id
        } for p in campaign.posts]
    }

@router.post("/{campaign_id}/generate")
async def generate_content(campaign_id: UUID, data: GenerateRequest, token: str, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(db, token)
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.user_id == user.id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    
    # Generate posts with AI
    posts_data = await content_generator.generate_campaign({
        "business_name": data.business_name,
        "industry": data.industry,
        "goals": data.goals,
        "target_audience": data.target_audience,
        "tone": data.tone,
        "platforms": campaign.platforms,
        "weeks": data.weeks,
        "posts_per_week": data.posts_per_week
    })
    
    created = []
    for p in posts_data:
        post = Post(
            campaign_id=campaign.id,
            platform=Platform(p.get("platform", "linkedin")),
            content=p.get("content", ""),
            scheduled_for=datetime.fromisoformat(p["scheduled_for"].replace("Z", "+00:00")) if p.get("scheduled_for") else None,
            status=PostStatus.PENDING,
            ai_metadata={"theme": p.get("theme"), "hashtags": p.get("hashtags")}
        )
        db.add(post)
        created.append(post)
    
    await db.commit()
    return {"generated": len(created)}

@router.patch("/{campaign_id}/posts/{post_id}")
async def update_post(campaign_id: UUID, post_id: UUID, data: PostUpdate, token: str, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(db, token)
    result = await db.execute(
        select(Post).join(Campaign).where(
            Post.id == post_id,
            Campaign.id == campaign_id,
            Campaign.user_id == user.id
        )
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Post not found")
    
    if data.content is not None:
        post.content = data.content
    if data.scheduled_for is not None:
        post.scheduled_for = data.scheduled_for
    if data.status is not None:
        post.status = PostStatus(data.status)
    
    await db.commit()
    return {"updated": True}

@router.post("/{campaign_id}/posts/{post_id}/approve")
async def approve_post(campaign_id: UUID, post_id: UUID, token: str, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(db, token)
    result = await db.execute(
        select(Post).join(Campaign).where(
            Post.id == post_id,
            Campaign.id == campaign_id,
            Campaign.user_id == user.id
        )
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Post not found")
    
    post.status = PostStatus.APPROVED
    await db.commit()
    return {"status": "approved"}

@router.post("/{campaign_id}/posts/{post_id}/publish")
async def publish_post(campaign_id: UUID, post_id: UUID, token: str, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(db, token)
    result = await db.execute(
        select(Post).join(Campaign).where(
            Post.id == post_id,
            Campaign.id == campaign_id,
            Campaign.user_id == user.id
        )
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Post not found")
    
    # Get LinkedIn connection
    conn_result = await db.execute(
        select(PlatformConnection).where(
            PlatformConnection.user_id == user.id,
            PlatformConnection.platform == Platform.LINKEDIN
        )
    )
    conn = conn_result.scalar_one_or_none()
    if not conn:
        raise HTTPException(400, "LinkedIn not connected")
    
    # Post to LinkedIn
    user_urn = f"urn:li:person:{conn.platform_user_id}"
    result = await LinkedInService.create_post(conn.access_token, user_urn, post.content)
    
    if "id" in result:
        post.status = PostStatus.PUBLISHED
        post.published_at = datetime.utcnow()
        post.platform_post_id = result["id"]
        await db.commit()
        return {"published": True, "post_id": result["id"]}
    else:
        post.status = PostStatus.FAILED
        await db.commit()
        raise HTTPException(500, f"Failed to publish: {result}")

@router.post("/{campaign_id}/posts/{post_id}/regenerate")
async def regenerate_post(campaign_id: UUID, post_id: UUID, instruction: str, token: str, db: AsyncSession = Depends(get_db)):
    user = await get_current_user(db, token)
    result = await db.execute(
        select(Post).join(Campaign).where(
            Post.id == post_id,
            Campaign.id == campaign_id,
            Campaign.user_id == user.id
        )
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(404, "Post not found")
    
    new_content = await content_generator.regenerate_post(post.content, instruction)
    post.content = new_content
    post.status = PostStatus.PENDING
    await db.commit()
    return {"content": new_content}
