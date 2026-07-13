"""
services/brand_voice_service.py

Manages brand profiles and dynamically injects brand guidelines into prompts.
Now accepts both BrandProfile objects and plain dicts for maximum flexibility.
"""
from models.brand_profile import BrandProfile
from prompts.brand_voice_prompt import BRAND_VOICE_INTEGRATION_PROMPT


class BrandVoiceService:
    """
    Service responsible for managing brand profiles and dynamically injecting
    brand guidelines into the AI content generation context.
    """

    def __init__(self):
        # Database session dependency would go here in the future
        pass

    def format_brand_context(self, profile) -> str:
        """
        Converts a BrandProfile (Pydantic model or plain dict) into a structured
        string context that can be seamlessly appended to the main content generation prompt.

        Accepts both ``BrandProfile`` instances and raw ``dict`` payloads so that
        tool inputs flattened for Groq compatibility still work seamlessly.
        """
        # If the caller passed a plain string, return it directly (calendar service)
        if isinstance(profile, str):
            return profile

        # If the caller passed a dict, coerce it into a BrandProfile
        if isinstance(profile, dict):
            profile = BrandProfile(**profile)

        # Join lists into human-readable strings for the prompt
        preferred_vocab_str = ", ".join(profile.preferred_vocabulary) if profile.preferred_vocabulary else "None specified"
        avoid_vocab_str = ", ".join(profile.words_to_avoid) if profile.words_to_avoid else "None specified"
        values_str = ", ".join(profile.brand_values) if profile.brand_values else "None specified"
        mission_str = profile.brand_mission if profile.brand_mission else "None specified"

        # Interpolate variables into the prompt template
        brand_context = BRAND_VOICE_INTEGRATION_PROMPT.format(
            brand_name=profile.brand_name,
            industry=profile.industry,
            brand_description=profile.brand_description,
            brand_mission=mission_str,
            brand_values=values_str,
            target_audience=profile.target_audience,
            writing_style=profile.writing_style,
            tone_of_voice=profile.tone_of_voice,
            emoji_preference=profile.emoji_preference,
            cta_style=profile.cta_style,
            preferred_vocabulary=preferred_vocab_str,
            words_to_avoid=avoid_vocab_str
        )

        return brand_context

    def save_profile(self, profile: BrandProfile):
        """
        Placeholder for persisting a new or updated brand profile to SQLite.
        """
        # TODO: Implement DB insertion logic once SQLAlchemy models are set up.
        pass

    def get_profile(self, profile_id: int) -> BrandProfile:
        """
        Placeholder for fetching a brand profile from SQLite.
        """
        # TODO: Implement DB retrieval logic.
        raise NotImplementedError("Database integration for Brand Profiles is not yet implemented.")
