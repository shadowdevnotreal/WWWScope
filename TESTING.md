# WWWScope Testing Guide

## Test Date: January 2025
## Version: 2.1.0

---

## 🧪 **Comprehensive Feature Testing**

### 1. **AI Model Testing** (8 Models)

Test each Groq model to ensure API functionality:

#### Models to Test:
- [ ] **llama-3.3-70b-versatile** (8K context, Recommended)
- [ ] **llama-3.3-70b-specdec** (8K context, Speculative Decoding)
- [ ] **llama-3.1-70b-versatile** (128K context, Long documents)
- [ ] **llama-3.1-8b-instant** (128K context, Fastest)
- [ ] **llama3-groq-70b-8192-tool-use-preview** (8K context, Function calling)
- [ ] **llama3-groq-8b-8192-tool-use-preview** (8K context, Fast tool use)
- [ ] **mixtral-8x7b-32768** (32K context, Balanced)
- [ ] **gemma2-9b-it** (8K context, Lightweight)

#### Test Procedure:
1. Open sidebar → AI Configuration
2. Enter valid Groq API key
3. Select model from dropdown
4. Click "🧪 Test" button
5. Verify success message: "✅ API key is valid and working!"
6. Repeat for each model

#### Expected Results:
- All models should respond within 5 seconds
- Test response should contain "API key works"
- No 400/401/429 errors

---

### 2. **Archive Comparison Features**

#### 2.1 Side-by-Side Screenshot Comparison
**Test URLs:**
- Version 1: `https://archive.ph/d97Mw`
- Version 2: `https://archive.ph/8I1iK`

**Steps:**
1. Go to "Compare Archives" tab
2. Enter both URLs
3. Click "Start Comparison"
4. Click "📸 Screenshot Comparison"
5. Wait for screenshots to load
6. Click expandable image viewers

**Expected:**
- ✅ Two screenshots side-by-side (1920x1080)
- ✅ Full-size expandable views
- ✅ No Selenium errors
- ✅ Images render clearly

**Fallback:** If Selenium unavailable, should show info message

---

#### 2.2 Text Diff Analysis
**Steps:**
1. Use same comparison URLs
2. Click "📊 Text Diff Analysis"
3. Review diff output

**Expected:**
- ✅ Line-by-line diff with +/- indicators
- ✅ Color-coded changes (green for additions, red for removals)
- ✅ Accurate change count
- ✅ Side-by-side text preview in expander

---

#### 2.3 AI-Powered Diff Explanation
**Prerequisites:** AI enabled with valid API key

**Steps:**
1. After running text diff
2. Click "🤖 Explain Changes (AI)"
3. Wait for AI analysis

**Expected:**
- ✅ Plain English explanation of changes
- ✅ Significance rating (SIGNIFICANT/MINOR/NEGLIGIBLE)
- ✅ Context-aware insights
- ✅ Response within 10 seconds

**Test with different models:**
- Llama 3.3 70B (default)
- Llama 3.1 70B (128K context for large diffs)
- Llama 3.1 8B (fastest)

---

#### 2.4 Iframe Preview
**Steps:**
1. Use comparison URLs
2. Click "👁️ Iframe Preview"

**Expected:**
- ✅ Two iframes side-by-side
- ✅ Both archives load
- ✅ Proper sandboxing (no security warnings)
- ✅ Scroll functionality works

---

### 3. **Archive Submission (Push to Archive)**

#### 3.1 Wayback Machine
**Test URL:** `https://example.com`

**Steps:**
1. Go to "Archive URL" tab
2. Select "Online Services"
3. Check "Wayback Machine"
4. Enter test URL
5. Click "Archive Now"

**Expected:**
- ✅ Submission accepted (or "already archived" message)
- ✅ No rate limit errors (429)
- ✅ Link to archived version provided
- ✅ Retry logic works if initial failure

**Known Issues:**
- Rate limiting may occur (max 1 request per 5 seconds)
- Should show retry countdown

---

#### 3.2 Archive.today
**Test URL:** `https://example.com`

**Steps:**
1. Select "Archive.today"
2. Click "Archive Now"

**Expected:**
- ✅ CAPTCHA notice displayed
- ✅ Mirror rotation attempts (archive.ph, archive.is, archive.fo)
- ✅ Progressive retry with backoff (5s, 10s, 15s, 20s, 30s)
- ✅ Success message with archive URL OR helpful error message

**Manual Verification:**
- May require manual CAPTCHA solving
- Should handle all mirrors gracefully

---

#### 3.3 Local WARC Creation
**Steps:**
1. Select "Local WARC"
2. Enter URL
3. Click "Create Local Archive"

**Expected:**
- ✅ WARC file created in `local_archives/` directory
- ✅ Gzip compression applied
- ✅ File appears in WARC Management tab
- ✅ Proper WARC 1.0 format with headers

---

### 4. **WARC Viewer Testing**

#### 4.1 ReplayWeb.page CDN Viewer (Embedded)
**Prerequisites:** WARC file uploaded

**Steps:**
1. Go to "WARC Management" tab
2. Expand a WARC file
3. Click "👀 View Content"
4. Select "ReplayWeb.page (Recommended)"
5. Click "🚀 Launch Embedded ReplayWeb.page Viewer"

**Expected:**
- ✅ ReplayWeb.page loads from CDN (https://cdn.jsdelivr.net/npm/replaywebpage/)
- ✅ Full JavaScript and CSS rendering
- ✅ Interactive navigation works
- ✅ No external dependencies or paid services
- ✅ Timeline view of captures

**CDN Verification:**
- Open browser dev tools → Network tab
- Verify requests to `cdn.jsdelivr.net` (free CDN)
- NO requests to paid services

---

#### 4.2 ReplayWeb.page Download Method
**Steps:**
1. Click "📥 Download WARC File"
2. Click "Open in ReplayWeb.page" link
3. Drag/drop downloaded WARC to replayweb.page

**Expected:**
- ✅ Download works
- ✅ Link opens https://replayweb.page/
- ✅ Drag-and-drop functionality works
- ✅ Full archive playback

---

#### 4.3 Basic Viewer
**Steps:**
1. Select "Basic Viewer"
2. Review extracted content

**Expected:**
- ✅ HTTP headers displayed per record
- ✅ HTML content rendered in iframe
- ✅ Download button for each page
- ✅ Expandable sections per URL
- ✅ Record count displayed

---

### 5. **AI-Enhanced WARC Analysis**

#### 5.1 Archive Summarization
**Steps:**
1. In WARC Management tab
2. Expand a WARC file
3. Click "📝 Summarize"

**Expected:**
- ✅ AI generates 150-word summary
- ✅ Identifies main topic
- ✅ Notes content type
- ✅ Explains archival value
- ✅ Response within 10 seconds

**Test with:**
- Different content types (news, blog, documentation)
- Different models (fast vs accurate)

---

#### 5.2 Metadata Generation
**Steps:**
1. Click "🏷️ Generate Metadata"

**Expected:**
- ✅ JSON output with:
  - Title (concise, descriptive)
  - Description (1-2 sentences)
  - Tags (5 relevant keywords)
  - Category (main classification)
- ✅ Proper JSON formatting
- ✅ Relevant and accurate metadata

---

### 6. **Internet Archive Sync**

**Prerequisites:**
- Internet Archive credentials in `.streamlit/secrets.toml`
- Valid `ia_access_key` and `ia_secret_key`

**Steps:**
1. In WARC Management tab
2. Click "🔄 Sync" on a WARC file
3. Monitor progress

**Expected:**
- ✅ Upload initiates
- ✅ Progress indication
- ✅ Success message with Archive.org URL
- ✅ Enhanced retry logic on failures
- ✅ Metadata included in upload

**Without Credentials:**
- ✅ Should show clear error message
- ✅ Instructions to configure credentials

---

### 7. **Archive Retrieval Across Services**

**Test URL:** `https://example.com`

**Steps:**
1. Go to "Retrieve Archives" tab
2. Enter URL
3. Select "All Services"
4. Click "Search Archives"

**Expected:**
- ✅ Searches 9 services simultaneously
- ✅ Progress bar updates in real-time
- ✅ Results categorized by service
- ✅ Direct archive links provided
- ✅ Summary statistics (found vs not found)
- ✅ Timestamp of search

**Services to verify:**
- Wayback Machine
- Archive.today
- Archive.is
- Google Cache
- WebCite
- Megalodon
- TimeTravel
- Perma.cc
- Memento API

---

### 8. **Rate Limiting & Performance**

#### 8.1 Advanced Rate Limiter
**Status Check:** Sidebar → System Status → "✅ Advanced Rate Limiting"

**Test:**
1. Make multiple rapid archive requests
2. Verify backoff behavior

**Expected:**
- ✅ Per-service rate limiting
- ✅ Token bucket algorithm
- ✅ Smart request handling
- ✅ No 429 errors from excessive requests

---

#### 8.2 Groq AI Rate Limits
**Free Tier Limits:**
- 30 requests/minute
- 6,000 tokens/minute

**Test:**
1. Make 35 AI requests rapidly
2. Observe behavior

**Expected:**
- ✅ First 30 succeed
- ✅ Clear error after limit
- ✅ Retry suggestion displayed

---

### 9. **UI/UX Features**

#### 9.1 API Key Management
**Test Flow:**
1. Enter API key
2. Click "🧪 Test" → Success
3. Click "💾 Save" → Saved to secrets.toml
4. Restart app → Key persists
5. Click "🗑️ Clear" → Key removed

**Expected:**
- ✅ All buttons work
- ✅ Session state preserved
- ✅ Disk persistence works
- ✅ Clear removes from session only (not disk)

---

#### 9.2 Model Selection
**Steps:**
1. Select different models from dropdown
2. Verify model changes reflected in AI calls

**Expected:**
- ✅ Dropdown shows all 4 models
- ✅ Model descriptions accurate
- ✅ Selection persists during session
- ✅ Different models produce different response styles

---

### 10. **Error Handling & Edge Cases**

#### 10.1 Invalid URLs
**Test:** Enter `not-a-url`

**Expected:**
- ✅ Validation error
- ✅ Clear message to user
- ✅ No crashes

---

#### 10.2 Invalid API Key
**Test:** Enter `gsk_invalid_key_123`

**Expected:**
- ✅ Test fails gracefully
- ✅ Error message: "API key test failed"
- ✅ Suggestion to check key

---

#### 10.3 Network Failures
**Test:** Disconnect internet, attempt archive

**Expected:**
- ✅ Timeout after 30 seconds
- ✅ Helpful error message
- ✅ Retry suggestions

---

#### 10.4 Large WARC Files
**Test:** Upload >100MB WARC

**Expected:**
- ✅ Upload succeeds (may be slow)
- ✅ Progress indication
- ✅ Viewer handles large files
- ✅ Memory doesn't spike excessively

---

## 🔧 **System Status Checks**

### Sidebar Status Indicators

Must show:
- ✅ Enhanced Archive Services (if available)
- ✅ Advanced Rate Limiting (if available)
- ✅ Screenshot Comparison (if Selenium available)
- 🤖 AI Features Enabled (if API key valid)

---

## 📊 **Performance Benchmarks**

| Feature | Expected Time | Acceptable Range |
|---------|--------------|------------------|
| AI Summarization | 3-5s | < 10s |
| AI Diff Explanation | 5-8s | < 15s |
| Screenshot Capture | 5-10s | < 20s |
| Text Diff | Instant | < 2s |
| WARC Upload | Varies | Depends on size |
| Archive Submission | 5-30s | < 60s |

---

## 🐛 **Known Issues & Limitations**

1. **Selenium Headless Mode:** May fail in some cloud environments
2. **Archive.today CAPTCHA:** Manual solving may be required
3. **Groq Rate Limits:** Free tier has 30 req/min limit
4. **ReplayWeb.page Embedded:** Experimental, download method preferred
5. **Large WARC Files:** May timeout on slow connections

---

## ✅ **Acceptance Criteria**

**For v2.1.0 to be considered production-ready:**

- [ ] All 4 Groq models working
- [ ] Side-by-side comparison functional
- [ ] At least one archive service (Wayback) working
- [ ] WARC viewer (basic mode) working
- [ ] AI diff explanation working with at least 1 model
- [ ] API key test/save/clear all functional
- [ ] No critical errors in normal usage
- [ ] ReplayWeb.page using free CDN (no paid dependencies)

---

## 📝 **Test Results Log**

### Test Run 1: [Date]

**Tester:** [Name]

**Results:**
- Models Tested: [ ] / 8
- Features Tested: [ ] / 10
- Bugs Found: [List]
- Performance: [Notes]

---

**End of Testing Guide**
