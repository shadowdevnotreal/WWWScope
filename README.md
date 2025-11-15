<div align="center">

# 🌍 WWWScope

![WWWScope](2025-10-15_20-07-12.jpg)

### ✨ Archive, compare, and sync web history with ease - Preserve the internet, one page at a time

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/shadowdevnotreal/WWWScope)
[![License](https://img.shields.io/badge/license-GPL%20v3.0-green.svg)](LICENSE)
[![Made with Love](https://img.shields.io/badge/made%20with-❤️-red.svg)](https://github.com/shadowdevnotreal/WWWScope)
[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen.svg)](https://wwwscope.streamlit.app)
[![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Selenium](https://img.shields.io/badge/selenium-4.15+-green.svg)](https://www.selenium.dev/)

[![GitHub Stars](https://img.shields.io/github/stars/shadowdevnotreal/WWWScope?style=social)](https://github.com/shadowdevnotreal/WWWScope/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/shadowdevnotreal/WWWScope?style=social)](https://github.com/shadowdevnotreal/WWWScope/network)
[![GitHub Watchers](https://img.shields.io/github/watchers/shadowdevnotreal/WWWScope?style=social)](https://github.com/shadowdevnotreal/WWWScope/watchers)

**🚀 [Live Demo](https://wwwscope.streamlit.app) | 📚 [Documentation](https://github.com/shadowdevnotreal/WWWScope/wiki) | 💬 [Community](https://github.com/shadowdevnotreal/WWWScope/discussions)**

*Professional web archiving solution for researchers, journalists, and digital preservationists. Capture snapshots, track changes, and maintain a historical record of the web.*

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/shadowdevnotreal/WWWScope)
[![Deploy to Streamlit Cloud](https://img.shields.io/badge/Deploy%20to-Streamlit%20Cloud-FF4B4B?logo=streamlit)](https://share.streamlit.io/)

</div>

---

## 🎯 **What is WWWScope?**

WWWScope is a comprehensive web archiving and comparison platform that transforms how you preserve and analyze web content. Built with Python and Streamlit, it provides professional-grade tools for archiving web pages across multiple services, comparing historical versions, and maintaining WARC (Web ARChive) files.

### 🌟 **Key Highlights**

```
📸 Multi-Service Archiving    🔄 Version Comparison      📦 WARC Management
🤖 AI-Powered Analysis        🔍 Visual Diff Tools       ☁️ Cloud Integration
🔒 Privacy-Focused            ✨ Modern UI/UX            📊 Real-time Analytics
⚡ High Performance           🌐 Internet Archive Sync   🎯 Research-Grade
🧠 Smart Summarization        🏷️ Auto-Metadata          ⚡ Ultra-Fast Inference
```

### 🎯 **Perfect For**

- **📰 Journalists** - Archive sources and track content changes over time
- **🔬 Researchers** - Maintain reproducible web citations and historical records
- **⚖️ Legal Professionals** - Preserve evidence and document web-based information
- **🛡️ Digital Archivists** - Build comprehensive web preservation collections
- **📚 Librarians** - Curate digital collections with proper versioning

---

## ✨ **Features Overview**

### 🤖 **AI-Powered Archive Analysis** ⚡ NEW!
<details open>
<summary><strong>Groq-Powered Intelligence for Smart Archiving</strong> - Ultra-fast AI insights (~280 tokens/sec)</summary>

Transform your web archiving workflow with cutting-edge AI capabilities powered by **Groq's Lightning-Fast Inference**:

- **🧠 Archive Content Summarization** - AI-generated summaries of archived pages
  - Automatically extract main topics and key information
  - Identify content type and archival value
  - Generate concise 150-word summaries in seconds
  - Perfect for quickly understanding large archive collections

- **🔍 Smart Diff Explanation** - Plain English change analysis
  - Explain what changed between two archive versions
  - Identify significant vs. minor modifications
  - Highlight content additions, removals, and updates
  - AI-powered significance detection (SIGNIFICANT/MINOR/NEGLIGIBLE)

- **🏷️ Automatic Metadata Generation** - Smart tagging and categorization
  - Generate descriptive titles and descriptions
  - Auto-create relevant tags (5 keywords)
  - Classify content by category
  - Perfect for Internet Archive submissions

- **📊 Content Classification** - Intelligent content analysis
  - Type detection (news, blog, documentation, social, ecommerce, etc.)
  - Topic extraction (3-5 main topics)
  - Sentiment analysis (positive, neutral, negative, mixed)
  - Archival value assessment (high, medium, low with reasoning)

- **⚖️ Archive Quality Assessment** - Completeness verification
  - Evaluate if essential content was captured
  - Identify missing elements (images, scripts, interactive features)
  - Quality scoring (1-10 scale)
  - Actionable recommendations for re-archiving

- **🎯 Related Archive Suggestions** - Discover what else to preserve
  - AI suggests related URLs worth archiving
  - Identifies connected topics and domains
  - Helps build comprehensive archive collections

**Powered By:**
- **Provider:** Groq (Industry-leading inference speed)
- **Default Model:** Llama 3.3 70B Versatile
- **Speed:** ~280 tokens/second (7x faster than GPT-4)
- **Cost:** Free tier includes 30 requests/minute, 6,000 tokens/minute

**Available Models (8 total):**
- **Llama 3.3 70B Versatile** - Recommended (8K context, fast & accurate)
- **Llama 3.3 70B Speculative Decoding** - Optimized speed (8K context)
- **Llama 3.1 70B Versatile** - Long documents (128K context) 🔥
- **Llama 3.1 8B Instant** - Fastest (128K context, ~800 tok/s) ⚡
- **Llama 3 Groq 70B Tool Use** - Function calling (8K context)
- **Llama 3 Groq 8B Tool Use** - Fast tool use (8K context)
- **Mixtral 8x7B** - Balanced performance (32K context)
- **Gemma 2 9B** - Lightweight & efficient (8K context)

**Quick Setup:**
1. Get free API key from [console.groq.com](https://console.groq.com)
2. Configure in sidebar: Settings → Enable AI Features
3. Enter API key, test connection, and save
4. Choose your preferred model
5. Start using AI features in Compare Archives and WARC Management tabs!

See [AI_FEATURES.md](AI_FEATURES.md) for complete documentation.

</details>

### 🌐 **Multi-Service Web Archiving**
<details>
<summary><strong>Archive to Multiple Services Simultaneously</strong> - Comprehensive backup across platforms</summary>

- **🏛️ Wayback Machine Integration** - Archive.org's premier archiving service
  - Automatic submission and verification
  - Historical snapshot retrieval
  - Rate limit handling with smart retry logic

- **📦 Archive.today Support** - Fast archiving with CAPTCHA bypass
  - Multiple mirror fallback (archive.ph, archive.is, archive.fo)
  - Exponential backoff retry mechanism
  - User-friendly CAPTCHA guidance

- **🕰️ Memento TimeTravel** - Aggregated archive search across services
  - JSON API integration
  - Multi-source historical version discovery

- **💾 Local WARC Creation** - Industry-standard WARC 1.0 format
  - Full HTTP headers preservation
  - Automatic gzip compression
  - Metadata embedding
  - Portable archive files

</details>

### 🔄 **Advanced Archive Comparison**
<details>
<summary><strong>Visual and Textual Diff Analysis</strong> - Track changes with precision</summary>

- **📸 Screenshot Comparison** - Visual side-by-side analysis
  - Full HD (1920x1080) screenshot capture using Selenium
  - Automated Chrome/Chromium integration via webdriver-manager
  - Full-size expandable views for detail examination
  - Error handling with graceful fallback

- **📊 Text Diff Analysis** - Line-by-line content comparison
  - BeautifulSoup HTML parsing with cleanup
  - Python difflib unified diff format
  - Changed line metrics (excluding diff headers)
  - Color-coded diff display with syntax highlighting
  - Export-ready comparison reports

- **🤖 AI-Powered Diff Explanation** - Plain English change analysis ⚡ NEW!
  - Automatically explain what changed between versions
  - Identify significant vs. minor modifications
  - AI-powered significance detection (SIGNIFICANT/MINOR/NEGLIGIBLE)
  - Context-aware analysis with actionable insights
  - Powered by Groq's ultra-fast Llama 3.3 70B model

- **🖼️ Live Iframe Preview** - Real-time archive viewing
  - Side-by-side iframe display (Version 1 vs Version 2)
  - XSS protection with HTML escaping
  - Iframe sandboxing for security (allow-same-origin, allow-scripts, allow-forms)
  - CORS warning for blocked content
  - Responsive column layout

- **🔍 Smart Error Handling** - Rate limit and access control detection
  - HTTP 429 (Rate Limit) detection with retry guidance
  - HTTP 403 (Forbidden) handling with CAPTCHA instructions
  - HTTP 404 (Not Found) with alternative suggestions
  - Connection timeout recovery
  - SSL error handling

</details>

### 📦 **WARC File Management**
<details>
<summary><strong>Professional Archive Storage & Synchronization</strong> - Industry-standard preservation</summary>

- **📤 Upload & Storage** - Centralized WARC repository
  - `.warc` and `.warc.gz` file support
  - Automatic gzip compression for space efficiency
  - File size tracking and metadata display
  - Last modified timestamps

- **☁️ Internet Archive Sync** - Cloud backup and distribution
  - `internetarchive` Python library integration
  - Comprehensive metadata tagging (title, mediatype, collection, description, creator, subject, date, language, source, license)
  - Batch sync for multiple files
  - Individual file upload with progress indication
  - Archive.org URL generation for shared access
  - Enhanced retry logic with progressive backoff (5s, 10s, 15s, 20s, 30s)
  - Smart mirror rotation for Archive.today (archive.ph, archive.is, archive.fo)
  - Improved CAPTCHA handling with user-friendly guidance

- **👁️ Dual-Mode WARC Content Viewer** - Professional archive inspection ⚡ NEW!
  - **ReplayWeb.page (Recommended)** - Professional WARC viewer
    - Full JavaScript and CSS rendering
    - Interactive web page replay with perfect fidelity
    - No server required - runs entirely in browser
    - Download WARC file and open in [ReplayWeb.page](https://replayweb.page)
    - Best for complex pages with dynamic content

  - **Basic Viewer** - Quick in-app preview
    - `warcio` ArchiveIterator parsing
    - HTTP headers display per record
    - HTML content rendering in iframe (600px height)
    - Download button for individual pages
    - Expandable sections per URL
    - Error handling for corrupt files
    - Best for simple text-based content

- **🤖 AI-Enhanced Features** - Intelligent WARC analysis ⚡ NEW!
  - Content summarization for archived pages
  - Automatic metadata generation
  - Quality assessment and recommendations
  - See AI-Powered Features section above

- **🗂️ File Management** - Complete lifecycle control
  - List all local WARC files with metadata
  - File info display (name, size in MB, modified date)
  - Individual file sync to Internet Archive
  - Download button integration
  - Delete with confirmation and auto-refresh

</details>

### 🔍 **Archive Retrieval System**
<details>
<summary><strong>Comprehensive Search Across 9 Archive Services</strong> - Find historical versions anywhere</summary>

Supported services:
- **Wayback Machine** - `https://web.archive.org/web/*/{url}`
- **Archive.today** - `https://archive.today/{url}`
- **Archive.is** - `https://archive.is/{url}`
- **Google Cache** - `https://webcache.googleusercontent.com/search?q=cache:{url}`
- **WebCite** - `http://www.webcitation.org/query?url={url}`
- **Megalodon** - `http://megalodon.jp/?url={url}`
- **TimeTravel Memento** - `https://timetravel.mementoweb.org/list/{url}`
- **Perma.cc** - `https://perma.cc/search?q={url}`
- **Memento API** - JSON API with error handling

Features:
- **All Services or Single Service** - Radio button selection
- **Progress bar with real-time status** - Visual feedback during search
- **Result display with expandable sections** - Organized presentation
- **Direct archive links** - One-click access to archived versions
- **Summary statistics** - Count of found vs not found
- **Timestamp of search completion** - Record keeping

</details>

### 🛡️ **Security & Privacy**
<details>
<summary><strong>Enterprise-Grade Protection</strong> - Your data, your control</summary>

- **🔒 Secure Credential Management** - Streamlit Secrets integration
  - No hardcoded API keys
  - `.env.example` template for safe configuration
  - Internet Archive credentials (ia_access_key, ia_secret_key)
  - Graceful degradation when credentials unavailable

- **🛡️ XSS Protection** - HTML escaping for iframe URLs
  - `html.escape(url, quote=True)` for all embedded content
  - Prevents code injection attacks

- **🔐 Iframe Sandboxing** - Restricted iframe capabilities
  - `sandbox="allow-same-origin allow-scripts allow-forms"`
  - Limits potential malicious behavior
  - Border styling for visual clarity

- **✅ URL Validation** - Robust input checking
  - `urlparse()` for proper URL structure validation
  - Protocol checking (http/https only)
  - Network location verification
  - Malformed URL rejection with clear errors

- **🔒 Privacy-First Design** - No tracking, no analytics
  - All processing happens locally or via user-controlled services
  - No third-party tracking scripts
  - User data never leaves your control

</details>

---

## 🏗️ **System Architecture**

<details open>
<summary><strong>Core Architecture Overview</strong> - Scalable and maintainable design</summary>

### 🔧 **Application Flow**
```mermaid
graph TD
    A[Streamlit UI] --> B{User Action}
    B -->|Archive URL| C[Multi-Service Archiver]
    B -->|Retrieve Archives| D[Archive Search Engine]
    B -->|Compare Archives| E[Comparison Tools]
    B -->|WARC Management| F[WARC Handler]

    C --> G[Wayback Machine API]
    C --> H[Archive.today API]
    C --> I[Local WARC Creator]

    D --> J[9 Archive Services]

    E --> K[Screenshot Module]
    E --> L[Text Diff Module]
    E --> M[Iframe Viewer]

    F --> N[Internet Archive Uploader]
    F --> O[WARC Parser]
    F --> P[File Management]

    style A fill:#e1f5fe
    style E fill:#f3e5f5
    style F fill:#e8f5e8
```
</details>


### 🔄 **Comparison Workflow**
```mermaid
sequenceDiagram
    participant U as User
    participant UI as Streamlit UI
    participant SS as Screenshot Service
    participant TD as Text Diff
    participant SE as Selenium Driver

    U->>UI: Enter two archive URLs
    UI->>UI: Validate URLs (urlparse)
    UI->>UI: Clean URLs (remove duplicates)
    UI->>UI: Store in session state
    U->>UI: Click "Screenshot Comparison"
    UI->>SS: take_screenshot(url1, "screenshot1.png")
    SS->>SE: Initialize Chrome driver (headless)
    SE->>SE: Navigate to URL + wait 3s
    SE->>SS: Save 1920x1080 screenshot
    SS-->>UI: Return screenshot path
    UI->>SS: take_screenshot(url2, "screenshot2.png")
    SS-->>UI: Return screenshot path
    UI->>U: Display side-by-side + full-size expanders

    U->>UI: Click "Text Diff Analysis"
    UI->>TD: extract_text_from_url(url1)
    TD->>TD: Fetch with requests + BeautifulSoup
    TD->>TD: Remove scripts/styles, normalize whitespace
    TD-->>UI: Return cleaned text
    UI->>TD: extract_text_from_url(url2)
    TD-->>UI: Return cleaned text
    UI->>UI: Generate unified diff with difflib
    UI->>U: Display metrics + diff + expandable previews
```

</details>

---

## 🚀 **Quick Start Guide**

### 📦 **Installation Options**

#### Option 1: Clone and Run Locally
```bash
# Clone the repository
git clone https://github.com/shadowdevnotreal/WWWScope.git

# Navigate to project directory
cd WWWScope/wwwscope-project

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional - for Internet Archive sync)
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your Internet Archive credentials

# Run the application
streamlit run app/app.py
```

#### Option 2: Deploy to Streamlit Cloud
1. Fork this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Click "New app"
4. Select your forked repository
5. Set main file path: `wwwscope-project/app/app.py`
6. (Optional) Add secrets in Streamlit Cloud dashboard:
   ```toml
   ia_access_key = "your_internet_archive_access_key"
   ia_secret_key = "your_internet_archive_secret_key"
   ```
7. Click "Deploy"

#### Option 3: Cloud Development Environment
[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/shadowdevnotreal/WWWScope)

```bash
# In Cloud Shell
git clone https://github.com/shadowdevnotreal/WWWScope.git
cd WWWScope/wwwscope-project

# Install dependencies
pip install -r requirements.txt --break-system-packages

# Note: Screenshot feature requires Chrome (not available in Cloud Shell)
# All other features work normally

# Run in cloud mode
streamlit run app/app.py --server.headless true
```

#### Option 4: Docker Deployment
```bash
# Coming soon - Docker support planned for Q1 2025
```

### 🎮 **Usage Workflow**

1. **📥 Archive a URL**
   - Choose "Archive URL" tab
   - Select "Online Services" or "Local WARC"
   - Enter URL and select services (Wayback Machine, Archive.today, etc.)
   - Click "Archive Now" and monitor progress

2. **🔍 Retrieve Archives**
   - Choose "Retrieve Archives" tab
   - Enter URL to search
   - Select "All Services" or specific service
   - Click "Search Archives"
   - View results with direct links

3. **🔄 Compare Archives**
   - Choose "Compare Archives" tab
   - Enter two archive URLs (e.g., Wayback Machine snapshots from different dates)
   - Click "Start Comparison"
   - Use tools:
     - **📸 Screenshot Comparison** - Visual side-by-side
     - **📊 Text Diff Analysis** - Line-by-line changes
     - **🤖 AI Explain Changes** - Get plain English summary of what changed (NEW!)
     - **👁️ Iframe Preview** - Live embedded view

4. **📦 Manage WARC Files**
   - Choose "WARC Management" tab
   - Upload local WARC files or view existing
   - Click "View Content" to inspect archives
     - **ReplayWeb.page** - Download and view in professional WARC viewer (NEW!)
     - **Basic Viewer** - Quick in-app preview with HTTP headers
   - Use AI features (if enabled):
     - **📝 Summarize** - AI-generated content summary (NEW!)
     - **🏷️ Generate Metadata** - Auto-create tags and descriptions (NEW!)
   - Click "Sync" to upload to Internet Archive
   - Download or delete files as needed

### ⚙️ **Configuration Options**

#### **🤖 Groq AI Configuration** (Recommended - enables AI features) ⚡ NEW!

**Option 1: UI Configuration (Easiest)**
1. Start WWWScope: `streamlit run app/app.py`
2. Open sidebar → Expand "🤖 Enable AI Features"
3. Get free API key from [console.groq.com](https://console.groq.com)
4. Enter API key in the input field
5. Click "🧪 Test API Key" to verify connection
6. Click "💾 Save API Key" to persist configuration
7. Select your preferred model from dropdown
8. AI features now available in all tabs!

**Option 2: Configuration File**

Create or edit `.streamlit/secrets.toml`:
```toml
# Groq AI Configuration (for AI-powered features)
groq_api_key = "gsk_your_actual_api_key_here"

# Internet Archive (for cloud sync)
ia_access_key = "your_access_key_here"
ia_secret_key = "your_secret_key_here"
```

**Option 3: Environment Variable**
```bash
# Linux/Mac
export GROQ_API_KEY="gsk_your_actual_api_key_here"

# Windows (PowerShell)
$env:GROQ_API_KEY="gsk_your_actual_api_key_here"

# Windows (CMD)
set GROQ_API_KEY=gsk_your_actual_api_key_here
```

**Get Groq API Key (Free):**
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for free account
3. Navigate to API Keys section
4. Generate new API key (starts with `gsk_...`)
5. Free tier: 30 requests/minute, 6,000 tokens/minute

---

#### **🏛️ Internet Archive Credentials** (Optional - enables cloud sync feature)

Create `.streamlit/secrets.toml`:
```toml
ia_access_key = "your_access_key_here"
ia_secret_key = "your_secret_key_here"
```

**Get your credentials:**
1. Create account at [archive.org](https://archive.org)
2. Visit [archive.org/account/s3.php](https://archive.org/account/s3.php)
3. Copy your access and secret keys

---

## 🛠️ **Tech Stack**

<div align="center">

| Frontend/UI | Backend | Automation | Storage |
|-------------|---------|------------|---------|
| ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white) | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) | ![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white) | ![Internet Archive](https://img.shields.io/badge/Internet%20Archive-666666?style=for-the-badge&logo=internet-archive&logoColor=white) |
| ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) | ![Requests](https://img.shields.io/badge/Requests-FF6B6B?style=for-the-badge) | ![Chrome](https://img.shields.io/badge/Chrome-4285F4?style=for-the-badge&logo=google-chrome&logoColor=white) | ![WARC](https://img.shields.io/badge/WARC-1.0-blue?style=for-the-badge) |

| Parsing | AI/ML ⚡ NEW! | DevOps | Analytics |
|---------|--------------|---------|-----------|
| ![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup4-59666C?style=for-the-badge) | ![Groq](https://img.shields.io/badge/Groq-FF6B35?style=for-the-badge&logo=ai&logoColor=white) | ![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white) | ![Streamlit](https://img.shields.io/badge/Analytics-Built--in-FF4B4B?style=for-the-badge) |
| ![warcio](https://img.shields.io/badge/warcio-1.7.4-green?style=for-the-badge) | ![Llama](https://img.shields.io/badge/Llama%203.3-70B-blueviolet?style=for-the-badge) | ![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white) | ![Session State](https://img.shields.io/badge/Session%20State-Persistent-blueviolet?style=for-the-badge) |
| ![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white) | ![Speed](https://img.shields.io/badge/Speed-280%20tok%2Fs-success?style=for-the-badge) | | |

</div>

### 🔧 **Key Dependencies**

```python
# Core dependencies
streamlit >= 1.28.0          # Modern web UI framework
requests >= 2.31.0           # HTTP library for API calls
internetarchive >= 3.5.0     # Internet Archive uploader
warcio >= 1.7.4              # WARC file parser
beautifulsoup4 >= 4.12.0     # HTML parsing

# AI/ML Enhancement (NEW!)
groq >= 0.4.0                # Groq AI for ultra-fast inference (~280 tok/s)

# Browser Automation (Optional)
selenium >= 4.15.0           # Browser automation for screenshots
webdriver-manager >= 4.0.0   # ChromeDriver management

# Cloud Storage (Optional)
boto3 >= 1.28.0              # AWS S3 integration

# Testing
pytest >= 7.4.0              # Testing framework
```

### 🏗️ **Architecture Features**

- **🎨 Modern UI** - Streamlit's reactive framework for instant updates
- **🔒 Secure by Design** - No hardcoded credentials, XSS protection, sandboxed iframes
- **⚡ High Performance** - Concurrent request handling, efficient caching
- **🌐 Cloud Ready** - Deploy to Streamlit Cloud, AWS, GCP, or Azure
- **♿ Accessible** - Keyboard navigation, screen reader support
- **📱 Responsive** - Works on desktop, tablet, and mobile

---

## 🎯 **Use Cases**

### 📰 **Journalism & Media**
- Archive source material before publication
- Track changes to official statements and press releases
- Document evidence of content modification or deletion
- Maintain reproducible citations

### 🔬 **Research & Academia**
- Preserve web-based research sources
- Create reproducible web citations for papers
- Track evolution of online datasets
- Maintain digital research collections

### ⚖️ **Legal & Compliance**
- Preserve web-based evidence for legal proceedings
- Document compliance with web disclosure requirements
- Track changes to terms of service and privacy policies
- Maintain tamper-evident records

### 🛡️ **Digital Preservation**
- Build institutional web archives
- Preserve cultural heritage websites
- Document internet history
- Create disaster recovery backups

---

## 📸 **Screenshots & Live Demo**

<div align="center">

### 🎯 **Try It Live - Comparison Demo**

**Real-World Example:** Tracking changes to a scammer bootcamp page

🔗 **Demo URLs for Testing:**
- **Version 1**: [https://archive.ph/d97Mw](https://archive.ph/d97Mw)
- **Version 2**: [https://archive.ph/8I1iK](https://archive.ph/8I1iK)

**How to test:**
1. Navigate to the **"Compare Archives"** tab
2. Paste Version 1 URL in first field: `https://archive.ph/d97Mw`
3. Paste Version 2 URL in second field: `https://archive.ph/8I1iK`
4. Click **"Start Comparison"**
5. Try all three tools:
   - 📸 **Screenshot Comparison** - Visual diff
   - 📊 **Text Diff Analysis** - Line-by-line changes
   - 👁️ **Iframe Preview** - Side-by-side view

---

### ✨ **Feature Highlights**

**🏠 Tab 1: Archive URL**
- Multi-service archiving with Wayback Machine, Archive.today, and Memento
- Local WARC creation with industry-standard WARC 1.0 format
- Progress tracking and status updates

**🔍 Tab 2: Retrieve Archives**
- Search across 9 different archive services
- Expandable results with direct links
- Summary statistics and timestamps

**🔄 Tab 3: Compare Archives**
- Screenshot comparison with 1920x1080 resolution
- Full-size expandable views for detail examination
- Text diff with color-coded syntax highlighting
- **🤖 AI-powered diff explanation** - Plain English change summary (NEW!)
- **Significance detection** - SIGNIFICANT/MINOR/NEGLIGIBLE ratings (NEW!)
- Live iframe preview (side-by-side)
- Smart error handling (rate limits, CAPTCHA, access denied)

**📦 Tab 4: WARC Management**
- Upload and storage for `.warc` and `.warc.gz` files
- **ReplayWeb.page integration** - Professional WARC viewer (NEW!)
- Basic in-app viewer with HTTP headers
- **🤖 AI content summarization** - Instant archive summaries (NEW!)
- **🏷️ AI metadata generation** - Auto-create tags and descriptions (NEW!)
- Internet Archive sync with comprehensive metadata
- Enhanced retry logic with progressive backoff
- Download and delete capabilities

---

**🎥 Demo Video Coming Soon**

</div>

---

## 🤝 **Contributing**

We welcome contributions from the community! Here's how you can help:

### 🎯 **Ways to Contribute**

- **🐛 Bug Reports** - Found an issue? [Open an issue](https://github.com/shadowdevnotreal/WWWScope/issues)
- **💡 Feature Requests** - Have an idea? [Start a discussion](https://github.com/shadowdevnotreal/WWWScope/discussions)
- **🔧 Code Contributions** - Submit pull requests for improvements
- **📚 Documentation** - Help improve guides and examples
- **🧪 Testing** - Help with quality assurance and bug testing

### 📋 **Development Setup**

```bash
# Fork the repository
git clone https://github.com/YOUR_USERNAME/WWWScope.git
cd WWWScope/wwwscope-project

# Create feature branch
git checkout -b feature/amazing-feature

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# Make your changes with proper testing
pytest tests/

# Format code
black app/

# Commit with conventional commits
git commit -m "feat: add amazing new feature"

# Push and create pull request
git push origin feature/amazing-feature
```

### 🧪 **Quality Assurance Checklist**

- [ ] ✅ All existing tests pass (`pytest`)
- [ ] 🧪 New features have test coverage
- [ ] 📚 Documentation updated (README, docstrings)
- [ ] 🔒 Security review (no hardcoded credentials, XSS prevention)
- [ ] ⚡ Performance check (no blocking operations in UI)
- [ ] 🐍 Code formatted with Black
- [ ] 📝 Conventional commit messages

---

## 📚 **Documentation**

<div align="center">

| Resource | Description | Link |
|----------|-------------|------|
| 📖 **User Guide** | Complete usage instructions | [View Guide](https://github.com/shadowdevnotreal/WWWScope/wiki) |
| 🔧 **Deployment Guide** | Production deployment instructions | [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) |

</div>

---

## 🌍 **Community & Support**

<div align="center">

### 💬 **Join Our Community**

[![GitHub Discussions](https://img.shields.io/badge/GitHub-Discussions-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/shadowdevnotreal/WWWScope/discussions)
[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@CatzHat)

### 📧 **Get Support**

- **📚 Documentation**: [Complete Guide](https://github.com/shadowdevnotreal/WWWScope/wiki)
- **💬 Community**: [Join Discussions](https://github.com/shadowdevnotreal/WWWScope/discussions)
- **🐛 Issues**: [Report Problems](https://github.com/shadowdevnotreal/WWWScope/issues)
- **📧 Email**: [Direct Support](mailto:43219706+shadowdevnotreal@users.noreply.github.com)

</div>

---

## 🔮 **Roadmap**

<details>
<summary><strong>🚀 Upcoming Features</strong> - What's coming next</summary>

### ✅ **Recently Completed (v2.1.0)**
- [x] **🤖 AI-Powered Change Detection** - Intelligent diff analysis with Groq AI
- [x] **🧠 Smart Summarization** - Archive content summarization
- [x] **🏷️ Auto-Metadata Generation** - AI-generated tags and descriptions
- [x] **📊 Content Classification** - Intelligent content analysis and categorization
- [x] **🎯 ReplayWeb.page Integration** - Professional WARC viewer support
- [x] **⚡ Enhanced Archive Services** - Improved retry logic and error handling

### Q1 2025
- [ ] **🐳 Docker Support** - Containerized deployment with Docker Compose
- [ ] **📱 Mobile App** - Progressive Web App (PWA) for mobile devices
- [ ] **🔌 Browser Extension** - One-click archiving from Chrome/Firefox
- [ ] **📊 Enhanced Analytics** - Archive statistics and usage metrics dashboard
- [ ] **🔍 Semantic Search** - Search archives by meaning, not just keywords

### Q2 2025
- [ ] **📈 Interactive Diff Visualization** - Visual diff with highlight modes and change tracking
- [ ] **🔄 Scheduled Archiving** - Automated periodic archiving with cron jobs
- [ ] **☁️ Multi-Cloud Storage** - AWS S3, Google Cloud Storage, Azure Blob
- [ ] **📈 Archive Clustering** - Automatically group similar archives

### Q3 2025
- [ ] **🏢 Enterprise Features** - Team collaboration, role-based access control
- [ ] **📈 Advanced Reporting** - Export-ready reports (PDF, CSV, JSON)
- [ ] **🔗 API Integration** - RESTful API for programmatic access
- [ ] **🌐 Multi-language Support** - Internationalization (i18n)
- [ ] **🔄 Change Trend Analysis** - Detect patterns across multiple versions

</details>

---

## ⚠️ **Important Information**

<div align="center">

### 🚨 **Responsible Use Policy**

This project is provided for **legitimate archiving, research, and preservation purposes**. Please ensure compliance with:

✅ **Applicable laws and regulations** (copyright, privacy, data protection)
✅ **Terms of service** of archived websites and archiving platforms
✅ **Robots.txt** and ethical web scraping practices
✅ **Rate limiting** to avoid overwhelming servers

### 🆘 **Support Resources**

- **📞 Technical Support**: [GitHub Issues](https://github.com/shadowdevnotreal/WWWScope/issues)
- **🔒 Security Issues**: Report to [security email](mailto:43219706+shadowdevnotreal@users.noreply.github.com)
- **📋 Feature Requests**: Use [GitHub Discussions](https://github.com/shadowdevnotreal/WWWScope/discussions)
- **🐛 Bug Reports**: Create detailed [GitHub issues](https://github.com/shadowdevnotreal/WWWScope/issues)

</div>

---

## 📄 **License & Intellectual Property Protection**

> **⚠️ INTELLECTUAL PROPERTY NOTICE**
> This project contains proprietary methodologies and intellectual property owned by **Diatasso LLC**.
> While the source code is GPL v3.0 Licensed, the underlying methodologies, frameworks, and proprietary techniques are protected intellectual property.

---

### 🛡️ Dual Protection Structure

This project operates under a **Dual Protection Model**:

1. **Open Source Code** → GPL v3.0 License (software implementation)
2. **Proprietary IP** → Service Marks and Copyrights (methodologies, frameworks, business processes)

---

### 📋 What's Protected

#### ✅ **GPL v3.0 Licensed (Free to Use)**
- **Source code implementation** - All code files, scripts, and technical implementations
- **Technical architecture** - File structure, organization patterns, deployment configurations
- **Installation and setup procedures** - Installation scripts and deployment methods
- **Basic usage examples** - Command demonstrations and sample workflows

#### 🔒 **Proprietary & Protected (Restricted Use)**
- **"WWWScope™"** product name and branding
- **"PRCM™"** methodology and all derivatives
- **Web archiving methodologies and workflows** developed by Diatasso
- **Business processes and consulting methodologies**
- **Training materials and educational content**
- **All methodologies mentioned in Diatasso pitch decks and business documentation**

---

### ™️ **Service Mark & Brand Protection**

#### **Protected Marks**
**"Diatasso"** is a registered service mark (Reg. Date: 04/18/2022, TN SOS)
- **Scope**: Business consulting, business management, business administration, communications services
- **Class 35**: Advertising, business management, business administration, office functions
- **Protected Services**: Business consultant services, communication services

#### **Protected Branding**
- **Diatasso™** (registered service mark)
- **PRCM™** (proprietary methodology)
- **WWWScope™** (product name)
- All derivative methodology names and frameworks
- All branding, logos, and trade dress associated with Diatasso LLC

---

### ⚖️ **License Terms**

#### **Software License (GPL v3.0)**
```
Copyright (C) 2025 Diatasso LLC

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```

#### **Intellectual Property Restrictions**

**PROPRIETARY METHODOLOGIES - ALL RIGHTS RESERVED**

The methodologies, frameworks, and analytical systems contained in this software are proprietary intellectual property of Diatasso LLC.

**These proprietary elements are NOT covered by the GPL v3.0 License:**

1. **No Methodology Reproduction** - The frameworks and methodologies may not be reproduced, extracted, or implemented independently without authorization.

2. **No Commercial Methodology Use** - The proprietary frameworks may not be used in commercial consulting, training, or service offerings without a licensing agreement.

3. **No Derivative Methodology Creation** - Creating derivative frameworks based on these methodologies requires authorization.

4. **No Brand Usage** - The Diatasso service mark and PRCM/WWWScope trademarks may not be used to brand derivative works or services.

---

### ✅ **Permitted Uses**

#### **You MAY (Under GPL v3.0):**
✔️ Use the source code in personal projects
✔️ Use the code in commercial applications
✔️ Modify and fork the code
✔️ Distribute modified versions (with GPL v3.0 license)
✔️ Include in your portfolio (with proper attribution)
✔️ Reference as "Based on open source code from Diatasso portfolio"
✔️ Use technical architecture patterns

#### **You MAY (With Proper Attribution):**
✔️ Cite frameworks in academic research (with citation)
✔️ Reference methodologies in educational contexts (with attribution)
✔️ Discuss concepts in professional development (with acknowledgment)

---

### ❌ **Prohibited Uses**

#### **You MAY NOT:**
❌ Extract and implement the proprietary frameworks independently
❌ Use "Diatasso™", "PRCM™", or "WWWScope™" to brand your products/services
❌ Offer consulting services based on these methodologies without licensing
❌ Create training programs using the proprietary frameworks
❌ Claim affiliation, partnership, or endorsement by Diatasso
❌ Use in competing business consulting or communications services
❌ Remove or obscure intellectual property notices

---

### 🎯 **Summary of Protection Layers**

**Layer 1: Open Source Code (GPL v3.0)**
✅ Free to use, modify, distribute - Software implementation only

**Layer 2: Service Mark Protection (Diatasso™)**
🔒 Brand identity protected - No unauthorized use of marks

**Layer 3: Proprietary Methodologies (All Rights Reserved)**
🔒 Frameworks and processes protected - Licensing required for commercial use

**Layer 4: Copyrighted Materials (All Rights Reserved)**
🔒 Documentation and training materials - No reproduction without authorization

---

### 📝 **Attribution Requirements**

#### **Proper Attribution Examples:**

**✅ CORRECT:**
- "Based on open source code from the Diatasso portfolio"
- "Powered by technology inspired by Diatasso frameworks"
- "Built using open source implementations"

**❌ INCORRECT:**
- "Powered by Diatasso™" (implies official partnership)
- "Using PRCM™ methodology" (without license)
- "Certified Diatasso consultant" (without authorization)
- "Official Diatasso implementation" (false affiliation)

---

### 🤝 **Licensing & Partnerships**

#### **Commercial Licensing Available**

For legitimate business uses, Diatasso offers:
- **Methodology Licensing** - Authorized use of PRCM™ and proprietary frameworks
- **Training & Certification** - Official training programs for consultants
- **Partnership Programs** - Strategic partnerships for complementary services
- **Custom Development** - Tailored implementations for enterprise clients
- **White-Label Solutions** - Licensed implementations for service providers

#### **Contact Information:**
📧 **Email**: [43219706+shadowdevnotreal@users.noreply.github.com](mailto:43219706+shadowdevnotreal@users.noreply.github.com)

**For:**
- Licensing inquiries → Subject: "Licensing Inquiry - WWWScope"
- Consulting services → Subject: "Consulting Request - Web Archiving"
- Partnership opportunities → Subject: "Partnership Inquiry - WWWScope"
- IP questions → Subject: "IP Question - WWWScope"

---

### 🔍 **Why This Protection Structure?**

This dual-license approach enables:
- ✅ **Community Contribution** - Open source code benefits developers
- ✅ **Business Protection** - Methodologies protected for consulting revenue
- ✅ **Clear Boundaries** - Explicit rules prevent confusion
- ✅ **Growth Opportunities** - Licensing enables legitimate commercial use
- ✅ **Quality Control** - Diatasso maintains methodology integrity

**Similar to:**
- Linux® kernel (GPL) + Red Hat® services (trademark protection)
- Firefox® browser (MPL) + Mozilla® brand (trademark protection)
- WordPress® software (GPL) + WordPress® mark (trademark protection)

---

**© 2025 Diatasso LLC. All Rights Reserved.**
**Diatasso™ is a registered service mark of Diatasso LLC (TN SOS Reg. Date: 04/18/2022)**
**PRCM™ and WWWScope™ are trademarks of Diatasso LLC**

*This project is part of the Diatasso portfolio showcasing our business consulting and technology capabilities while contributing to the open source community under a clear dual-protection structure.*

---

## 🙏 **Acknowledgments**

Special thanks to the open source community and contributors who made this project possible:

- **🔧 Streamlit Team** - For the amazing reactive web framework
- **🏛️ Internet Archive** - For providing free web archiving services
- **🌐 Archive.today** - For additional archiving infrastructure
- **🤖 Groq** - For ultra-fast AI inference and free API access (NEW!)
- **🦙 Meta AI** - For the powerful Llama 3.3 70B model
- **🎯 ReplayWeb.page** - For the professional WARC viewer tool
- **📦 Open Source Libraries** - Beautiful Soup, Selenium, warcio, requests, groq
- **🧪 Beta Testers** - Community members who provided valuable feedback
- **📚 Documentation Contributors** - Writers who helped improve guides

### 🌟 **Built With**

- **Technology Stack** - Modern Python ecosystem (Streamlit, Requests, Selenium, Groq AI)
- **AI/ML Integration** - Groq's ultra-fast inference with Llama 3.3 70B Versatile
- **Design Principles** - User-centered design for researchers and archivists
- **Development Practices** - Test-driven development and continuous integration
- **Community Feedback** - User-driven feature development

---

<div align="center">

![Diatasso Logo](https://github.com/user-attachments/assets/0bdb61c2-fc8c-422a-a991-ef42454f2b1c)

**🚀 A Diatasso PRCM™ Product**

*Empowering digital preservation through intelligent archiving solutions*

---

### ⭐ **Star this repository if it helped you!**

**Made with ❤️ by the Diatasso Team**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/shadowdevnotreal)
[![Website](https://img.shields.io/badge/Website-4285F4?style=for-the-badge&logo=google-chrome&logoColor=white)](https://shadowdevnotreal.github.io)
[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@CatzHat)

<a href="https://www.buymeacoffee.com/diatasso" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-violet.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

**Last Updated**: January 2025 | **Version**: 2.1.0 | **Status**: Production Ready

</div>
