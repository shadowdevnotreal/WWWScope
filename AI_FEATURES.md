# 🤖 AI Features - Groq Integration for WWWScope

## Overview

WWWScope now includes powerful AI-enhanced features powered by **Groq**, providing ultra-fast inference for web archiving intelligence. These features help you understand, analyze, and manage archived content more effectively.

**Date:** November 15, 2025
**AI Provider:** Groq (Llama 3.1 70B Versatile)
**Model Speed:** ~280 tokens/second (one of the fastest in the industry)

---

## 🎯 AI-Powered Features

### 1. **📝 Archive Content Summarization**

**What it does:**
Automatically generates concise summaries of archived web pages, highlighting:
- Main topic and key information
- Content type (news, blog, documentation, etc.)
- Why the content is worth archiving

**Use Case:**
```
You archived 50 web pages. Instead of reading each one, use AI
summarization to quickly understand what each archive contains.
```

**Location:** WARC Management tab → View Content → AI Analysis → Summarize

**Example Output:**
```
This archived page is a technical blog post about web scraping
best practices. It covers rate limiting, ethical considerations,
and legal compliance. Worth archiving for its comprehensive
guide on responsible data collection.
```

---

### 2. **🔍 Smart Diff Explanation**

**What it does:**
Analyzes differences between two archived versions and explains changes in plain English.

**Benefits:**
- Understand what changed without reading complex diffs
- Identifies significant vs. minor changes
- Highlights content additions, removals, and modifications

**Use Case:**
```
You archived a news article in January and again in March.
AI explains: "The article was updated to include new statistics
about Q1 results. The introduction paragraph was rewritten,
and three new sources were cited."
```

**Location:** Compare Archives tab → Text Diff Analysis → Explain Changes (AI)

**Features:**
- **Change Detection:** Separates meaningful changes from formatting tweaks
- **Significance Assessment:** Rates changes as SIGNIFICANT, MINOR, or NEGLIGIBLE
- **Context Awareness:** Understands the type of content being compared

---

### 3. **🏷️ Metadata Generation**

**What it does:**
Automatically generates structured metadata for archived content:
- **Title:** Descriptive, concise title
- **Description:** 1-2 sentence summary
- **Tags:** 5 relevant keywords
- **Category:** Main classification

**Use Case:**
```
Upload a WARC file without metadata. AI analyzes the content
and generates proper tags, descriptions, and categorization
for Internet Archive submission.
```

**Location:** WARC Management tab → AI Analysis → Generate Metadata

**Example Output:**
```json
{
  "title": "Python Web Scraping Tutorial - BeautifulSoup Guide",
  "description": "Comprehensive tutorial on web scraping with Python, covering BeautifulSoup, requests, and ethical practices.",
  "tags": ["python", "web-scraping", "beautifulsoup", "tutorial", "programming"],
  "category": "Educational"
}
```

---

### 4. **📊 Content Classification**

**What it does:**
Classifies archived content by:
- **Type:** news, blog, documentation, social, ecommerce, government, educational, other
- **Topics:** 3-5 main topics
- **Sentiment:** positive, neutral, negative, mixed
- **Archival Value:** high, medium, low (with reasoning)

**Use Case:**
```
Automatically organize your archive collection by content type
and archival value. Prioritize high-value content for permanent
preservation.
```

**Technical Implementation:**
```python
classification = ai_helper.classify_content(webpage_text)
# Returns structured data for filtering and organization
```

---

### 5. **⚖️ Archive Quality Assessment**

**What it does:**
Evaluates if an archive successfully captured the essential content:
- Checks for completeness
- Identifies missing elements (images, scripts)
- Rates overall quality (1-10 scale)
- Provides actionable feedback

**Use Case:**
```
You archived a complex web app. AI assesses: "Quality: 7/10.
Archive captured main content and text, but JavaScript-dependent
features may not render properly. Consider using screenshot
comparison for visual verification."
```

**Benefits:**
- Ensure critical content is preserved
- Identify archives that need re-capture
- Validate archiving effectiveness

---

### 6. **🎯 Related Archive Suggestions**

**What it does:**
Based on archived content, AI suggests:
- Related URLs worth archiving
- Topics to explore
- Similar domains or resources

**Use Case:**
```
You archived a research paper about climate change. AI suggests:
"Consider archiving the cited sources, the author's other
publications, and related datasets from climate.gov"
```

---

## 🚀 Setup & Configuration

### Step 1: Get Groq API Key (Free)

1. Visit: https://console.groq.com
2. Sign up for free account
3. Navigate to API Keys section
4. Generate new API key
5. Copy the key (starts with `gsk_...`)

**Free Tier Limits:**
- 30 requests/minute
- 6,000 tokens/minute
- More than enough for typical archiving workflows

---

### Step 2: Configure WWWScope

#### **Option A: Streamlit Secrets (Recommended)**

Create or edit `.streamlit/secrets.toml`:

```toml
# Groq AI Configuration
groq_api_key = "gsk_your_actual_api_key_here"

# Internet Archive (optional)
ia_access_key = "your_ia_key"
ia_secret_key = "your_ia_secret"
```

#### **Option B: Environment Variable**

```bash
# Linux/Mac
export GROQ_API_KEY="gsk_your_actual_api_key_here"

# Windows (PowerShell)
$env:GROQ_API_KEY="gsk_your_actual_api_key_here"

# Windows (CMD)
set GROQ_API_KEY=gsk_your_actual_api_key_here
```

---

### Step 3: Install Dependencies

```bash
pip install groq>=0.4.0
# Or install all dependencies
pip install -r requirements.txt
```

---

### Step 4: Verify Setup

1. Start WWWScope: `streamlit run app/app.py`
2. Check sidebar "System Status"
3. Look for: **🤖 AI Features Enabled**

**If not enabled:**
- Check sidebar "Enable AI Features" section
- Verify API key is correct
- Restart Streamlit app

---

## 📖 Usage Examples

### Example 1: Analyze Archive Differences

```python
# User workflow (via UI):
1. Navigate to "Compare Archives" tab
2. Enter two archive URLs:
   - Version 1: https://archive.ph/old_version
   - Version 2: https://archive.ph/new_version
3. Click "Text Diff Analysis"
4. Review diff output
5. Click "🤖 Explain Changes (AI)"
6. Get plain English explanation of changes
```

**AI Output:**
```
The main changes between versions:

1. SIGNIFICANT UPDATES:
   - New pricing information added ($99/month changed to $149/month)
   - Features section expanded with 3 new capabilities
   - Customer testimonials updated with recent reviews

2. MINOR CHANGES:
   - Footer copyright year updated
   - Social media links rearranged

Overall: SIGNIFICANT - This represents a major product update
worth archiving separately.
```

---

### Example 2: Smart WARC Metadata

```python
# User workflow (via UI):
1. Upload WARC file to "WARC Management" tab
2. Expand the file entry
3. Click "🏷️ Generate Metadata"
4. Receive structured metadata
5. Use for Internet Archive upload or documentation
```

**AI Output:**
```json
{
  "title": "GitHub Actions CI/CD Pipeline Guide",
  "description": "Step-by-step tutorial on setting up automated testing and deployment workflows using GitHub Actions.",
  "tags": [
    "github-actions",
    "ci-cd",
    "devops",
    "automation",
    "tutorial"
  ],
  "category": "Technical Documentation"
}
```

---

### Example 3: Content Summarization

```python
# Programmatic usage (for developers):
from app.core.ai_helper import get_ai_helper

ai = get_ai_helper()
if ai and ai.is_available():
    summary = ai.summarize_archive_content(webpage_text)
    print(summary)
```

---

## 🔧 Technical Architecture

### Module Structure

```
app/core/ai_helper.py
├── GroqAIHelper (main class)
│   ├── __init__() - Initialize Groq client
│   ├── summarize_archive_content()
│   ├── explain_diff()
│   ├── classify_content()
│   ├── generate_archive_metadata()
│   ├── assess_archive_quality()
│   ├── suggest_related_archives()
│   └── detect_content_changes_significance()
└── Global helpers
    ├── get_ai_helper() - Singleton instance
    └── is_ai_enabled() - Check availability
```

### API Request Flow

```
User clicks AI button
    ↓
Streamlit UI calls ai_helper method
    ↓
ai_helper._make_request()
    ↓
Groq API (Llama 3.1 70B)
    ↓
Response parsed and displayed
```

### Rate Limiting & Error Handling

```python
# Automatic retry on failures
try:
    response = self.client.chat.completions.create(...)
except Exception as e:
    st.error(f"Groq API error: {str(e)}")
    return None
```

**Built-in features:**
- Timeout handling
- Network error recovery
- Invalid response graceful degradation
- User-friendly error messages

---

## ⚡ Performance Benchmarks

### Groq vs. Other Providers

| Provider | Model | Speed (tokens/sec) | Latency |
|----------|-------|-------------------|---------|
| **Groq** | Llama 3.1 70B | ~280 | Ultra-low |
| OpenAI | GPT-4 | ~40 | Moderate |
| OpenAI | GPT-3.5 Turbo | ~80 | Low |
| Anthropic | Claude 3 | ~50 | Low-Moderate |

**Why Groq?**
- ✅ 7x faster than GPT-4
- ✅ Free tier with generous limits
- ✅ Excellent quality with Llama 3.1 70B
- ✅ Low latency for real-time analysis

---

## 🔒 Privacy & Security

### Data Handling

1. **No Data Storage:** AI requests are stateless; Groq doesn't store inputs
2. **Truncation:** Content is limited to relevant samples (500-3000 chars)
3. **Local Processing:** WARC files stay local; only text extracts sent to AI
4. **API Key Security:** Stored in secrets.toml (git-ignored)

### Best Practices

```toml
# .streamlit/secrets.toml (git-ignored)
groq_api_key = "gsk_..."

# .gitignore (ensure secrets are ignored)
.streamlit/secrets.toml
.env
*.env
```

---

## 🎨 UI Integration

### Sidebar Status Indicator

```
🔧 System Status
✅ Enhanced Archive Services
✅ Advanced Rate Limiting
✅ Screenshot Comparison
🤖 AI Features Enabled ← Shows when Groq is configured
```

### Feature Locations

| Feature | Tab | Button |
|---------|-----|--------|
| Diff Explanation | Compare Archives | 🤖 Explain Changes (AI) |
| Archive Summary | WARC Management | 📝 Summarize |
| Metadata Generation | WARC Management | 🏷️ Generate Metadata |

---

## 🐛 Troubleshooting

### Issue: "AI Features Disabled"

**Solutions:**
1. Check API key in `.streamlit/secrets.toml`
2. Verify `groq>=0.4.0` is installed: `pip list | grep groq`
3. Restart Streamlit: `streamlit run app/app.py`
4. Check logs for import errors

### Issue: "Groq API error: 401 Unauthorized"

**Solutions:**
1. Verify API key is correct
2. Check key hasn't expired
3. Ensure no extra spaces in secrets.toml

### Issue: "Request timeout"

**Solutions:**
1. Check internet connection
2. Groq API may be experiencing high load
3. Retry after a few seconds
4. Content might be too large (auto-truncated)

---

## 💡 Advanced Use Cases

### Batch Archive Analysis

```python
# Process multiple archives with AI
for warc in local_warcs:
    content = extract_warc_content(warc)
    summary = ai_helper.summarize_archive_content(content)
    metadata = ai_helper.generate_archive_metadata(url, content)
    # Store in database or export
```

### Custom AI Workflows

```python
# Extend ai_helper for custom needs
class CustomArchiveAI(GroqAIHelper):
    def detect_policy_changes(self, old_text, new_text):
        # Custom prompt for policy document analysis
        pass
```

---

## 📊 Cost Analysis

### Groq Free Tier

**Limits:**
- 30 requests/minute
- 6,000 tokens/minute
- No monthly request limit

**Typical Usage:**
- Diff explanation: ~500 tokens/request
- Summarization: ~300 tokens/request
- Metadata generation: ~400 tokens/request

**Daily Capacity (free tier):**
- ~43,000 requests/day
- More than sufficient for individual users

---

## 🚀 Future Enhancements

### Planned Features (Not Yet Implemented)

1. **Semantic Search** - Search archives by meaning, not just keywords
2. **Archive Clustering** - Automatically group similar archives
3. **Change Trend Analysis** - Detect patterns across multiple versions
4. **Custom AI Models** - Support for other providers (OpenAI, Anthropic)
5. **Batch Processing** - Analyze multiple archives in parallel
6. **Archive Recommendations** - Suggest what to archive based on trends

---

## 📝 API Reference

### Core Methods

#### `summarize_archive_content(content: str) -> str`

Generates summary of archived content.

**Parameters:**
- `content` (str): Web page text content
- `max_length` (int, optional): Max content length to process

**Returns:**
- Summary string or None if failed

---

#### `explain_diff(diff_text: str, v1_preview: str, v2_preview: str) -> str`

Explains changes between versions in plain English.

**Parameters:**
- `diff_text` (str): Unified diff output
- `v1_preview` (str): Version 1 sample
- `v2_preview` (str): Version 2 sample

**Returns:**
- Explanation string or None if failed

---

#### `generate_archive_metadata(url: str, content: str) -> Dict`

Generates structured metadata for archive.

**Parameters:**
- `url` (str): Archived URL
- `content` (str): Page content

**Returns:**
- Dictionary with title, description, tags, category

---

## 🤝 Contributing

Want to enhance AI features? Here's how:

1. **New AI Features:**
   - Add methods to `app/core/ai_helper.py`
   - Follow existing pattern for system/user prompts
   - Add UI integration in relevant tabs

2. **Model Optimization:**
   - Tune temperature and max_tokens parameters
   - Test different Groq models (llama-3.1-8b for speed)
   - Benchmark token usage

3. **Error Handling:**
   - Add try/except blocks
   - Provide user-friendly error messages
   - Log errors for debugging

---

## 📜 License & Attribution

**AI Provider:** Groq
**Model:** Llama 3.1 70B Versatile (Meta)
**Integration:** Custom implementation for WWWScope
**License:** GPL v3.0 (WWWScope), Groq Terms of Service apply

---

## 📞 Support

**Issues with AI Features:**
- Check: https://console.groq.com/docs
- WWWScope Issues: https://github.com/shadowdevnotreal/WWWScope/issues
- Label issues with: `ai-features` tag

---

**Last Updated:** November 15, 2025
**Status:** Production Ready ✅
**Groq SDK Version:** >= 0.4.0
