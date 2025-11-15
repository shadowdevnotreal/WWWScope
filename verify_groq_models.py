#!/usr/bin/env python3
"""
Quick Groq Model Verification Script
Run this locally to verify all models work correctly
"""

import requests
import json
import os
import sys

# Get API key from environment variable
API_KEY = os.environ.get("GROQ_API_KEY")

if not API_KEY:
    print("❌ Error: GROQ_API_KEY environment variable not set")
    print("\nUsage:")
    print("  export GROQ_API_KEY='your_key_here'")
    print("  python3 verify_groq_models.py")
    print("\nOr:")
    print("  GROQ_API_KEY='your_key' python3 verify_groq_models.py")
    sys.exit(1)

# Models we use in WWWScope
OUR_MODELS = {
    "llama-3.3-70b-versatile": "Llama 3.3 70B Versatile (8K context)",
    "llama-3.3-70b-specdec": "Llama 3.3 70B Speculative Decoding (8K context)",
    "llama-3.1-70b-versatile": "Llama 3.1 70B Versatile (128K context)",
    "llama-3.1-8b-instant": "Llama 3.1 8B Instant (128K context)",
    "llama3-groq-70b-8192-tool-use-preview": "Llama 3 Groq 70B Tool Use (8K context)",
    "llama3-groq-8b-8192-tool-use-preview": "Llama 3 Groq 8B Tool Use (8K context)",
    "mixtral-8x7b-32768": "Mixtral 8x7B (32K context)",
    "gemma2-9b-it": "Gemma 2 9B (8K context)"
}

def test_model(model_id, model_name):
    """Test a single model"""
    print(f"\n🧪 Testing: {model_name}")
    print(f"   Model ID: {model_id}")

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model_id,
                "messages": [
                    {"role": "user", "content": "Respond with exactly: 'Model working'"}
                ],
                "temperature": 0.1,
                "max_tokens": 10
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            tokens_used = data['usage']['total_tokens']

            print(f"   ✅ SUCCESS")
            print(f"   Response: {content}")
            print(f"   Tokens: {tokens_used}")
            return True
        else:
            print(f"   ❌ FAILED: HTTP {response.status_code}")
            print(f"   Error: {response.text}")
            return False

    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def list_available_models():
    """List all available models from Groq API"""
    print("\n" + "="*80)
    print("📋 Fetching available models from Groq API...")
    print("="*80)

    try:
        response = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            models = data.get('data', [])

            print(f"\n✅ Found {len(models)} models available:\n")

            for model in sorted(models, key=lambda x: x.get('id', '')):
                model_id = model.get('id', 'unknown')
                context = model.get('context_window', 'N/A')
                owned_by = model.get('owned_by', 'unknown')

                # Check if model is in our app
                in_app = "✅" if model_id in OUR_MODELS else "  "

                print(f"{in_app} {model_id}")
                print(f"   Owner: {owned_by}")
                print(f"   Context: {context:,}" if isinstance(context, int) else f"   Context: {context}")
                print()

            # Check for models in app but not in API
            api_model_ids = {m.get('id') for m in models}
            missing = set(OUR_MODELS.keys()) - api_model_ids

            if missing:
                print("\n⚠️  Models in WWWScope but NOT in API:")
                for model_id in sorted(missing):
                    print(f"   - {model_id}")

            # Check for new models
            new_models = api_model_ids - set(OUR_MODELS.keys())
            if new_models:
                print("\n🆕 New models available (not in WWWScope yet):")
                for model_id in sorted(new_models):
                    print(f"   - {model_id}")

            return True

        else:
            print(f"❌ Failed to fetch models: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error fetching models: {e}")
        return False

def main():
    print("="*80)
    print("🔍 WWWScope Groq Model Verification")
    print("="*80)

    # First, list all available models
    list_available_models()

    # Test each model in our app
    print("\n" + "="*80)
    print("🧪 Testing WWWScope Models (8 total)")
    print("="*80)

    passed = 0
    failed = 0

    for model_id, model_name in OUR_MODELS.items():
        if test_model(model_id, model_name):
            passed += 1
        else:
            failed += 1

    # Summary
    print("\n" + "="*80)
    print("📊 Test Results Summary")
    print("="*80)
    print(f"Total Models: {len(OUR_MODELS)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")

    if failed == 0:
        print("\n🎉 All models working correctly!")
    else:
        print(f"\n⚠️  {failed} model(s) need attention")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()
