"""
AI Helper Module for WWWScope
Provides Groq-powered AI enhancements for web archiving
"""

import os
import time
from typing import Optional, Dict, List, Any
import streamlit as st

# Groq API client
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class GroqAIHelper:
    """
    AI-powered helper using Groq for fast inference
    Provides archive analysis, summarization, and insights
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq AI Helper

        Args:
            api_key: Groq API key (optional, will try to get from secrets)
        """
        self.api_key = api_key
        self.client = None
        self.model = "llama-3.3-70b-versatile"  # Recommended: fast & accurate
        self.available = False

        if not GROQ_AVAILABLE:
            return

        # Try to get API key from multiple sources
        if not self.api_key:
            self.api_key = self._get_api_key()

        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                self.available = True
            except Exception as e:
                st.warning(f"⚠️ Groq initialization failed: {str(e)}")

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or Streamlit secrets"""
        # Try Streamlit secrets first
        try:
            return st.secrets.get("groq_api_key")
        except:
            pass

        # Try environment variable
        return os.environ.get("GROQ_API_KEY")

    def is_available(self) -> bool:
        """Check if AI helper is available"""
        return self.available and self.client is not None

    def _make_request(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> Optional[str]:
        """
        Make a request to Groq API

        Args:
            system_prompt: System instruction
            user_prompt: User message
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum response tokens

        Returns:
            AI response or None if failed
        """
        if not self.is_available():
            return None

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1,
                stream=False
            )

            return response.choices[0].message.content

        except Exception as e:
            st.error(f"Groq API error: {str(e)}")
            return None

    def summarize_archive_content(self, content: str, max_length: int = 500) -> Optional[str]:
        """
        Generate a concise summary of archived web content

        Args:
            content: Archived web page content (text)
            max_length: Maximum content length to process

        Returns:
            Summary or None if failed
        """
        # Truncate content if too long
        truncated_content = content[:max_length * 4] if len(content) > max_length * 4 else content

        system_prompt = (
            "You are a web archiving assistant. Summarize archived web content concisely. "
            "Focus on: main topic, key information, content type, and why it might be worth archiving. "
            "Keep summaries under 150 words."
        )

        user_prompt = f"Summarize this archived web content:\n\n{truncated_content}"

        return self._make_request(system_prompt, user_prompt, temperature=0.5, max_tokens=300)

    def explain_diff(self, diff_text: str, version1_preview: str, version2_preview: str) -> Optional[str]:
        """
        Explain what changed between two archived versions in plain English

        Args:
            diff_text: Unified diff output
            version1_preview: Preview of version 1
            version2_preview: Preview of version 2

        Returns:
            Plain English explanation or None if failed
        """
        system_prompt = (
            "You are a web archiving expert. Analyze differences between two archived versions "
            "of a web page and explain the changes in clear, plain English. "
            "Focus on: what was added, removed, or modified. Ignore minor formatting changes. "
            "Be concise and highlight significant changes."
        )

        # Limit diff size
        diff_sample = diff_text[:2000] if len(diff_text) > 2000 else diff_text
        v1_sample = version1_preview[:500] if len(version1_preview) > 500 else version1_preview
        v2_sample = version2_preview[:500] if len(version2_preview) > 500 else version2_preview

        user_prompt = (
            f"**Diff Output:**\n{diff_sample}\n\n"
            f"**Version 1 Preview:**\n{v1_sample}\n\n"
            f"**Version 2 Preview:**\n{v2_sample}\n\n"
            f"Explain what changed between these versions:"
        )

        return self._make_request(system_prompt, user_prompt, temperature=0.3, max_tokens=500)

    def classify_content(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Classify archived content by type, topics, and relevance

        Args:
            content: Web page content

        Returns:
            Classification dictionary or None if failed
        """
        truncated = content[:3000] if len(content) > 3000 else content

        system_prompt = (
            "You are a content classifier for web archives. Analyze web content and classify it. "
            "Respond ONLY with a JSON object containing:\n"
            '{\n'
            '  "type": "news|blog|documentation|social|ecommerce|government|educational|other",\n'
            '  "topics": ["topic1", "topic2", "topic3"],\n'
            '  "sentiment": "positive|neutral|negative|mixed",\n'
            '  "archival_value": "high|medium|low",\n'
            '  "reason": "brief explanation of archival value"\n'
            '}\n'
            "Be concise and accurate."
        )

        user_prompt = f"Classify this web content:\n\n{truncated}"

        response = self._make_request(system_prompt, user_prompt, temperature=0.3, max_tokens=400)

        if response:
            try:
                # Try to extract JSON from response
                import json
                # Find JSON in response (might have extra text)
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = response[start:end]
                    return json.loads(json_str)
            except Exception as e:
                st.warning(f"Failed to parse classification: {str(e)}")

        return None

    def generate_archive_metadata(self, url: str, content: str) -> Optional[Dict[str, str]]:
        """
        Generate metadata tags and description for an archive

        Args:
            url: Archived URL
            content: Page content

        Returns:
            Metadata dictionary or None if failed
        """
        truncated = content[:2000] if len(content) > 2000 else content

        system_prompt = (
            "You are a metadata generator for web archives. Create useful metadata. "
            "Respond ONLY with a JSON object containing:\n"
            '{\n'
            '  "title": "concise descriptive title",\n'
            '  "description": "brief description (1-2 sentences)",\n'
            '  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],\n'
            '  "category": "main category"\n'
            '}\n'
        )

        user_prompt = (
            f"Generate metadata for this archived page:\n\n"
            f"**URL:** {url}\n\n"
            f"**Content:**\n{truncated}"
        )

        response = self._make_request(system_prompt, user_prompt, temperature=0.5, max_tokens=400)

        if response:
            try:
                import json
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = response[start:end]
                    return json.loads(json_str)
            except Exception as e:
                st.warning(f"Failed to parse metadata: {str(e)}")

        return None

    def assess_archive_quality(self, url: str, archived_content: str) -> Optional[str]:
        """
        Assess if the archive captured essential content properly

        Args:
            url: Original URL
            archived_content: Archived content

        Returns:
            Quality assessment or None if failed
        """
        truncated = archived_content[:2000] if len(archived_content) > 2000 else archived_content

        system_prompt = (
            "You are a web archive quality assessor. Evaluate if an archive captured "
            "the essential content of a web page. Check for: completeness, readability, "
            "missing elements (images, scripts), and overall quality. "
            "Provide a brief assessment with a quality score (1-10)."
        )

        user_prompt = (
            f"**Original URL:** {url}\n\n"
            f"**Archived Content:**\n{truncated}\n\n"
            f"Assess the archive quality:"
        )

        return self._make_request(system_prompt, user_prompt, temperature=0.3, max_tokens=300)

    def suggest_related_archives(self, content: str, topics: List[str]) -> Optional[str]:
        """
        Suggest related URLs or topics worth archiving

        Args:
            content: Current archive content
            topics: Known topics

        Returns:
            Suggestions or None if failed
        """
        truncated = content[:1500] if len(content) > 1500 else content
        topics_str = ", ".join(topics) if topics else "general web content"

        system_prompt = (
            "You are a web archiving advisor. Based on archived content, suggest "
            "related URLs, topics, or domains worth archiving. Be specific and practical."
        )

        user_prompt = (
            f"Based on this content about {topics_str}, suggest related archives:\n\n"
            f"{truncated}\n\n"
            f"Provide 3-5 specific suggestions with brief explanations."
        )

        return self._make_request(system_prompt, user_prompt, temperature=0.7, max_tokens=500)

    def detect_content_changes_significance(self, diff: str) -> Optional[str]:
        """
        Determine if changes between versions are significant

        Args:
            diff: Diff output

        Returns:
            Significance assessment or None if failed
        """
        diff_sample = diff[:2000] if len(diff) > 2000 else diff

        system_prompt = (
            "You are a change detection expert for web archives. Analyze diffs and determine "
            "if changes are significant (content updates) or minor (formatting, timestamps, ads). "
            "Respond with: SIGNIFICANT, MINOR, or NEGLIGIBLE, followed by a brief reason."
        )

        user_prompt = f"Analyze this diff:\n\n{diff_sample}\n\nIs this change significant?"

        return self._make_request(system_prompt, user_prompt, temperature=0.2, max_tokens=200)


# Global instance
_ai_helper = None

def get_ai_helper() -> Optional[GroqAIHelper]:
    """Get or create AI helper instance"""
    global _ai_helper

    if not GROQ_AVAILABLE:
        return None

    if _ai_helper is None:
        _ai_helper = GroqAIHelper()

    return _ai_helper if _ai_helper.is_available() else None


def is_ai_enabled() -> bool:
    """Check if AI features are enabled"""
    helper = get_ai_helper()
    return helper is not None and helper.is_available()
