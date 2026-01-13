import json
from datetime import datetime, timedelta
from anthropic import Anthropic
from app.core.config import settings

class ContentGenerator:
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def generate_campaign(self, campaign_data: dict) -> list:
        prompt = f"""Generate a social media content calendar for this campaign:

Business: {campaign_data.get('business_name', 'Business')}
Industry: {campaign_data.get('industry', 'General')}
Goals: {campaign_data.get('goals', 'Increase engagement')}
Target Audience: {campaign_data.get('target_audience', 'General audience')}
Tone: {campaign_data.get('tone', 'Professional')}
Platforms: {campaign_data.get('platforms', ['linkedin'])}
Duration: {campaign_data.get('weeks', 4)} weeks
Posts per week: {campaign_data.get('posts_per_week', 3)}

Generate posts as JSON array with this structure:
[{{
  "platform": "linkedin",
  "content": "Post text here",
  "scheduled_for": "2026-01-15T09:00:00Z",
  "theme": "educational",
  "hashtags": ["#tag1", "#tag2"]
}}]

Only output valid JSON, no other text."""

        response = self.client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        
        text = response.content[0].text
        # Extract JSON from response
        start = text.find('[')
        end = text.rfind(']') + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        return []
    
    async def regenerate_post(self, post_content: str, instruction: str) -> str:
        prompt = f"""Rewrite this social media post based on the instruction.

Original post:
{post_content}

Instruction: {instruction}

Output only the new post text, nothing else."""

        response = self.client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

content_generator = ContentGenerator()
