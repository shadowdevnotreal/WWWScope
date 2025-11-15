#!/usr/bin/env python3
"""
Check available Groq models via API
Usage: GROQ_API_KEY='your_key' python3 check_groq_models.py
"""

import os
import sys
import json
import requests

def check_groq_models():
    """Query Groq API for available models"""

    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        print("❌ Error: GROQ_API_KEY environment variable not set")
        print("\nUsage:")
        print("  export GROQ_API_KEY='your_key_here'")
        print("  python3 check_groq_models.py")
        print("\nOr:")
        print("  GROQ_API_KEY='your_key' python3 check_groq_models.py")
        return False

    print("🔍 Querying Groq API for available models...")
    print(f"   API Key: {api_key[:20]}...{api_key[-4:]}\n")

    try:
        response = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=10
        )

        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

        data = response.json()
        models = data.get("data", [])

        print(f"✅ Found {len(models)} available models:\n")
        print("=" * 80)

        # Models in our app
        app_models = {
            "llama-3.3-70b-versatile",
            "llama-3.3-70b-specdec",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "llama3-groq-70b-8192-tool-use-preview",
            "llama3-groq-8b-8192-tool-use-preview",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        }

        found_models = set()

        for model in sorted(models, key=lambda x: x.get("id", "")):
            model_id = model.get("id", "unknown")
            created = model.get("created", "unknown")
            owned_by = model.get("owned_by", "unknown")
            context_window = model.get("context_window", "N/A")

            found_models.add(model_id)

            # Check if model is in our app
            in_app = "✅" if model_id in app_models else "  "

            print(f"{in_app} {model_id}")
            print(f"   Owner: {owned_by}")
            print(f"   Context: {context_window}")
            print(f"   Created: {created}")
            print()

        print("=" * 80)
        print("\n📊 Summary:")
        print(f"   Total models available: {len(models)}")
        print(f"   Models in WWWScope: {len(app_models)}")

        # Check for models in app but not in API
        missing = app_models - found_models
        if missing:
            print(f"\n⚠️  Models in app but not found in API:")
            for model in sorted(missing):
                print(f"   - {model}")

        # Check for new models not in app
        new_models = found_models - app_models
        if new_models:
            print(f"\n🆕 New models available (not in app yet):")
            for model in sorted(new_models):
                print(f"   - {model}")
        else:
            print(f"\n✅ All API models are in the app!")

        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = check_groq_models()
    sys.exit(0 if success else 1)
