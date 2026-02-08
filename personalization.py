from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import asyncio
import json
from datetime import datetime
from database import SessionLocal, User, ChatSession, Message
from sqlalchemy.orm import Session
from sqlalchemy import desc

class UserBackground(BaseModel):
    """
    Model for user background information
    """
    education_level: str = "undergraduate"  # high_school, undergraduate, graduate, phd, professional
    field_of_study: str = "general"  # general, computer_science, robotics, engineering, physics, math
    experience_level: str = "beginner"  # beginner, intermediate, advanced, expert
    native_language: str = "english"  # english, urdu, etc.
    preferred_language: str = "english"  # language for content delivery
    learning_goals: List[str] = []
    special_needs: List[str] = []  # visual, hearing, cognitive, etc.

class UserPreference(BaseModel):
    """
    Model for user preferences and settings
    """
    learning_style: str = "comprehensive"  # comprehensive, concise, example-focused
    difficulty_level: str = "intermediate"  # beginner, intermediate, advanced
    preferred_topics: List[str] = []
    notification_preferences: Dict[str, bool] = {"email": True, "push": False}
    content_format: str = "text"  # text, visual, audio, mixed
    background: UserBackground = UserBackground()

class PersonalizationEngine:
    """
    Engine to handle user personalization and content adaptation
    """
    def __init__(self):
        self.user_profiles = {}

    async def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """
        Retrieve user profile and preferences from database
        """
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]

        db = SessionLocal()
        try:
            # Get user information
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return self._get_default_profile()

            # Get user profile with background information
            user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

            # Get user's recent interactions to understand preferences
            recent_sessions = db.query(ChatSession).filter(
                ChatSession.user_id == user_id
            ).order_by(desc(ChatSession.updated_at)).limit(10).all()

            # Get recent messages to understand topics of interest
            recent_messages = db.query(Message).join(ChatSession).filter(
                ChatSession.user_id == user_id
            ).order_by(desc(Message.timestamp)).limit(20).all()

            # Analyze the user's interaction patterns
            topics_of_interest = self._analyze_topics_of_interest(recent_messages)
            interaction_patterns = self._analyze_interaction_patterns(recent_sessions, recent_messages)

            # Create profile with background information
            profile_data = {
                "user_id": user_id,
                "username": user.username,
                "full_name": user.full_name or user.username,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "topics_of_interest": topics_of_interest,
                "interaction_patterns": interaction_patterns,
                "engagement_metrics": self._calculate_engagement_metrics(recent_sessions, recent_messages)
            }

            # Add background information if available
            if user_profile:
                profile_data["background"] = {
                    "education_level": user_profile.education_level,
                    "field_of_study": user_profile.field_of_study,
                    "experience_level": user_profile.experience_level,
                    "native_language": user_profile.native_language,
                    "preferred_language": user_profile.preferred_language,
                    "learning_goals": json.loads(user_profile.learning_goals) if user_profile.learning_goals else [],
                    "special_needs": json.loads(user_profile.special_needs) if user_profile.special_needs else []
                }
                # Use stored preferences
                profile_data["preferences"] = self._get_default_preferences()
                profile_data["preferences"]["background"] = UserBackground(
                    education_level=user_profile.education_level,
                    field_of_study=user_profile.field_of_study,
                    experience_level=user_profile.experience_level,
                    native_language=user_profile.native_language,
                    preferred_language=user_profile.preferred_language,
                    learning_goals=json.loads(user_profile.learning_goals) if user_profile.learning_goals else [],
                    special_needs=json.loads(user_profile.special_needs) if user_profile.special_needs else []
                ).dict()
            else:
                # Create default profile with default background
                profile_data["background"] = UserBackground().dict()
                profile_data["preferences"] = self._get_default_preferences()

            # Cache the profile
            self.user_profiles[user_id] = profile_data
            return profile_data

        finally:
            db.close()

    def _get_default_profile(self) -> Dict[str, Any]:
        """
        Get default profile for new users
        """
        return {
            "user_id": None,
            "username": "guest",
            "full_name": "Guest User",
            "created_at": datetime.utcnow().isoformat(),
            "topics_of_interest": [],
            "interaction_patterns": {},
            "preferences": self._get_default_preferences(),
            "engagement_metrics": self._get_default_engagement_metrics()
        }

    def _get_default_preferences(self) -> UserPreference:
        """
        Get default user preferences
        """
        return UserPreference().dict()

    def _get_default_engagement_metrics(self) -> Dict[str, Any]:
        """
        Get default engagement metrics
        """
        return {
            "total_sessions": 0,
            "total_messages": 0,
            "avg_session_length": 0,
            "last_active": datetime.utcnow().isoformat(),
            "favorite_topics": [],
            "learning_progress": {}
        }

    def _analyze_topics_of_interest(self, messages: List[Message]) -> List[str]:
        """
        Analyze messages to determine topics of interest
        """
        # This is a simplified analysis - in a real implementation,
        # you would use NLP techniques to extract topics
        topics = set()
        for message in messages:
            content = message.content.lower()
            # Look for keywords related to the Physical AI textbook topics
            if any(keyword in content for keyword in ["robot", "ai", "embodiment", "manipulation", "ros", "gazebo", "isaac", "urdf", "simulation"]):
                topics.add("robotics")
            if any(keyword in content for keyword in ["learning", "algorithm", "model", "training", "neural", "deep"]):
                topics.add("machine learning")
            if any(keyword in content for keyword in ["physics", "dynamics", "kinematics", "motion", "force", "torque"]):
                topics.add("physics")

        return list(topics)

    def _analyze_interaction_patterns(self, sessions: List[ChatSession], messages: List[Message]) -> Dict[str, Any]:
        """
        Analyze user interaction patterns
        """
        patterns = {
            "session_frequency": len(sessions),
            "message_density": len(messages) / max(len(sessions), 1),
            "active_hours": [],  # Would be calculated from timestamps in a real implementation
            "preferred_interaction_style": "question_answer"  # Default assumption
        }
        return patterns

    def _calculate_engagement_metrics(self, sessions: List[ChatSession], messages: List[Message]) -> Dict[str, Any]:
        """
        Calculate engagement metrics for the user
        """
        metrics = {
            "total_sessions": len(sessions),
            "total_messages": len(messages),
            "avg_session_length": len(messages) / max(len(sessions), 1),
            "last_active": max([msg.timestamp for msg in messages]) if messages else datetime.utcnow(),
            "favorite_topics": self._analyze_topics_of_interest(messages)[:5],  # Top 5 topics
            "learning_progress": {}  # Would be implemented with actual progress tracking
        }
        return metrics

    async def personalize_content(self, content: str, user_id: int) -> str:
        """
        Adapt content based on user preferences and profile
        """
        profile = await self.get_user_profile(user_id)

        # Get user preferences
        user_pref = profile.get("preferences", self._get_default_preferences())
        user_background = user_pref.get("background", UserBackground().dict())

        # Adapt content based on learning style
        if user_pref["learning_style"] == "concise":
            # Provide a more concise version of the content
            content = self._make_concise(content)
        elif user_pref["learning_style"] == "example-focused":
            # Emphasize examples in the content
            content = self._emphasize_examples(content)

        # Adjust complexity based on difficulty level
        if user_pref["difficulty_level"] == "beginner":
            content = self._simplify_content(content)
        elif user_pref["difficulty_level"] == "advanced":
            content = self._add_advanced_details(content)

        # Adapt content based on user background
        content = await self._adapt_content_for_background(content, user_background)

        return content

    async def _adapt_content_for_background(self, content: str, background: Dict[str, Any]) -> str:
        """
        Adapt content based on user's background information
        """
        # Adapt based on education level
        if background["education_level"] in ["high_school"]:
            content = self._adapt_for_high_school_level(content)
        elif background["education_level"] in ["undergraduate"]:
            content = self._adapt_for_undergraduate_level(content)
        elif background["education_level"] in ["graduate", "phd"]:
            content = self._adapt_for_advanced_academic_level(content)

        # Adapt based on field of study
        if background["field_of_study"] in ["computer_science", "engineering"]:
            content = self._include_technical_details(content)
        elif background["field_of_study"] == "physics":
            content = self._include_physics_perspective(content)
        elif background["field_of_study"] == "math":
            content = self._include_mathematical_details(content)

        # Adapt based on experience level
        if background["experience_level"] == "beginner":
            content = self._add_beginner_explanations(content)
        elif background["experience_level"] == "expert":
            content = self._add_expert_perspective(content)

        # Adapt based on preferred language
        if background["preferred_language"] == "urdu" and background["native_language"] == "urdu":
            content = await self._translate_to_urdu(content)

        return content

    def _adapt_for_high_school_level(self, content: str) -> str:
        """
        Adapt content for high school level learners
        """
        # Simplify complex terminology and add more basic explanations
        return content

    def _adapt_for_undergraduate_level(self, content: str) -> str:
        """
        Adapt content for undergraduate level learners
        """
        # Add moderate technical details
        return content

    def _adapt_for_advanced_academic_level(self, content: str) -> str:
        """
        Adapt content for graduate/PhD level learners
        """
        # Add advanced technical details and research perspectives
        return content

    def _include_technical_details(self, content: str) -> str:
        """
        Include technical details relevant to CS/engineering students
        """
        return content

    def _include_physics_perspective(self, content: str) -> str:
        """
        Include physics perspective in content
        """
        return content

    def _include_mathematical_details(self, content: str) -> str:
        """
        Include mathematical details relevant to math students
        """
        return content

    def _add_beginner_explanations(self, content: str) -> str:
        """
        Add explanations for beginners
        """
        return content

    def _add_expert_perspective(self, content: str) -> str:
        """
        Add expert perspective and advanced concepts
        """
        return content

    async def _translate_to_urdu(self, content: str) -> str:
        """
        Translate content to Urdu (placeholder implementation)
        In a real implementation, this would use a translation service
        """
        # For now, return the original content with a note
        # In a real implementation, you would integrate with a translation API
        return content

    def _make_concise(self, content: str) -> str:
        """
        Make content more concise
        """
        # This is a simplified implementation
        # In a real implementation, you would use NLP to summarize content
        lines = content.split('\n')
        # Keep main points, remove excessive details
        concise_lines = [line for line in lines if len(line.strip()) > 10 and len(line.strip()) < 200]
        return '\n'.join(concise_lines[:10])  # Limit to first 10 meaningful lines

    def _emphasize_examples(self, content: str) -> str:
        """
        Emphasize examples in the content
        """
        # This is a simplified implementation
        # In a real implementation, you would extract and highlight examples
        return content

    def _simplify_content(self, content: str) -> str:
        """
        Simplify content for beginners
        """
        # This is a simplified implementation
        # In a real implementation, you would use NLP to simplify language
        return content

    def _add_advanced_details(self, content: str) -> str:
        """
        Add advanced details for advanced users
        """
        # This is a simplified implementation
        # In a real implementation, you would add technical details
        return content

    async def update_user_preferences(self, user_id: int, preferences: UserPreference) -> Dict[str, Any]:
        """
        Update user preferences in the system
        """
        db = SessionLocal()
        try:
            # Get or create user profile
            user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

            if user_profile:
                # Update existing profile
                user_profile.education_level = preferences.background.education_level
                user_profile.field_of_study = preferences.background.field_of_study
                user_profile.experience_level = preferences.background.experience_level
                user_profile.native_language = preferences.background.native_language
                user_profile.preferred_language = preferences.background.preferred_language
                user_profile.learning_goals = json.dumps(preferences.background.learning_goals)
                user_profile.special_needs = json.dumps(preferences.background.special_needs)
                user_profile.updated_at = datetime.utcnow()
            else:
                # Create new profile
                user_profile = UserProfile(
                    user_id=user_id,
                    education_level=preferences.background.education_level,
                    field_of_study=preferences.background.field_of_study,
                    experience_level=preferences.background.experience_level,
                    native_language=preferences.background.native_language,
                    preferred_language=preferences.background.preferred_language,
                    learning_goals=json.dumps(preferences.background.learning_goals),
                    special_needs=json.dumps(preferences.background.special_needs)
                )
                db.add(user_profile)

            db.commit()

            # Update cached profile
            if user_id in self.user_profiles:
                self.user_profiles[user_id]["preferences"] = preferences.dict()
                self.user_profiles[user_id]["background"] = preferences.background.dict()
            else:
                # Fetch and update the profile
                profile = await self.get_user_profile(user_id)
                profile["preferences"] = preferences.dict()
                profile["background"] = preferences.background.dict()
                self.user_profiles[user_id] = profile

            return {"status": "success", "preferences": preferences.dict()}
        finally:
            db.close()

# Global instance
personalization_engine = PersonalizationEngine()