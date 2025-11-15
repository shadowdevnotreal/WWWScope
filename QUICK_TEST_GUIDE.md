# 🚀 Quick Test Guide - WWWScope v2.1.0

**Last Updated:** January 2025
**Purpose:** Verify all features work and use free services

---

## ✅ Pre-Flight Checklist

Before testing, ensure you have:
- [ ] WWWScope running: `streamlit run app/app.py`
- [ ] Groq API key (free from https://console.groq.com)
- [ ] Internet connection

---

## 🧪 5-Minute Feature Test

### 1. **Test AI Features** (2 minutes)

**Setup:**
1. Open sidebar → "🤖 AI Configuration"
2. Paste your Groq API key
3. Click "🧪 Test"
4. Wait for "✅ API key is valid and working!"

**Quick Model Test:**
- Select "llama-3.3-70b-versatile" (default, fastest)
- Select "llama-3.1-70b-versatile" (128K context)
- Both should show as working in dropdown

**Verify:**
- ✅ Test button works
- ✅ Success message appears
- ✅ Model dropdown shows 4 models
- ✅ All models have context window info

---

### 2. **Test Side-by-Side Comparison** (1 minute)

**Test URLs:**
- Version 1: `https://archive.ph/d97Mw`
- Version 2: `https://archive.ph/8I1iK`

**Steps:**
1. Go to "Compare Archives" tab
2. Paste URLs
3. Click "Start Comparison"
4. Click "📊 Text Diff Analysis"
5. Click "🤖 Explain Changes (AI)"

**Verify:**
- ✅ Diff shows color-coded changes
- ✅ Change count is accurate
- ✅ AI explanation in plain English
- ✅ Significance rating (SIGNIFICANT/MINOR/NEGLIGIBLE)

---

### 3. **Test ReplayWeb.page (Free CDN)** (1 minute)

**Steps:**
1. Go to "WARC Management" tab
2. Upload any .warc file (or create one first)
3. Click "👀 View Content"
4. Select "ReplayWeb.page (Recommended)"
5. Click "🚀 Launch Embedded ReplayWeb.page Viewer"

**Verify CDN Usage:**
- ✅ Info message shows "Using Free CDN: jsDelivr"
- ✅ Viewer loads without errors
- ✅ Drag-and-drop zone appears
- ✅ No payment or account prompts

**Open Browser DevTools → Network Tab:**
- ✅ Requests to `cdn.jsdelivr.net`
- ✅ NO requests to paid services
- ✅ File loads from: `https://cdn.jsdelivr.net/npm/replaywebpage@1.8.11/ui.js`

---

### 4. **Test Archive Push** (1 minute)

**Test URL:** `https://example.com`

**Steps:**
1. Go to "Archive URL" tab
2. Select "Online Services"
3. Check "Wayback Machine"
4. Enter URL
5. Click "Archive Now"

**Verify:**
- ✅ Submission accepted (or "already archived")
- ✅ No payment prompts
- ✅ Link to archived version
- ✅ Retry logic if rate limited

**Note:** Archive.today may require CAPTCHA (normal, still free)

---

## 🔍 Detailed Feature Verification

### **AI Models - Test All 4**

Run each model individually:

```bash
# In sidebar, select each model:
1. llama-3.3-70b-versatile (8K context) - DEFAULT ✓
2. llama-3.3-70b-specdec (8K context) - FAST ✓
3. llama-3.1-70b-versatile (128K context) - LONG DOCS ✓
4. llama-3.1-8b-instant (128K context) - FASTEST ✓
5. llama3-groq-70b-8192-tool-use-preview (8K) - TOOLS ✓
6. llama3-groq-8b-8192-tool-use-preview (8K) - FAST TOOLS ✓
7. mixtral-8x7b-32768 (32K context) - BALANCED ✓
8. gemma2-9b-it (8K context) - LIGHTWEIGHT ✓
```

**Expected:** All models respond within 10 seconds

---

### **Screenshot Comparison**

**Prerequisites:** Selenium + ChromeDriver installed

**Test:**
1. Use comparison URLs from above
2. Click "📸 Screenshot Comparison"
3. Wait 10-15 seconds

**Verify:**
- ✅ Two screenshots side-by-side
- ✅ 1920x1080 resolution
- ✅ Expandable full-size views
- ✅ No Selenium errors

**If Disabled:**
- Shows info message: "ℹ️ Screenshot Feature Disabled"
- This is normal if Selenium not installed

---

### **WARC Viewer - Both Modes**

#### Mode 1: ReplayWeb.page (CDN)

**Verify Free CDN:**
```
✅ Loads from: https://cdn.jsdelivr.net/npm/replaywebpage@1.8.11/ui.js
✅ No account required
✅ No payment required
✅ Works offline after initial load
```

**Test:**
- Drag WARC file to viewer
- File loads and renders
- Navigation works
- JavaScript/CSS renders

#### Mode 2: Basic Viewer

**Test:**
- Select "Basic Viewer"
- HTTP headers display
- Content shows in iframe
- Download button works

---

### **AI WARC Analysis**

**Test Summarization:**
1. Expand WARC file
2. Click "📝 Summarize"
3. Wait 5-10 seconds

**Verify:**
- ✅ 150-word summary
- ✅ Main topic identified
- ✅ Content type noted
- ✅ Archival value explained

**Test Metadata Generation:**
1. Click "🏷️ Generate Metadata"
2. Wait 5-10 seconds

**Verify:**
- ✅ JSON output with:
  - Title (descriptive)
  - Description (1-2 sentences)
  - Tags (5 keywords)
  - Category

---

## 🆓 Free Services Verification

### **All Services We Use Are FREE:**

| Service | Free? | URL | Purpose |
|---------|-------|-----|---------|
| **jsDelivr CDN** | ✅ Yes | cdn.jsdelivr.net | ReplayWeb.page hosting |
| **Groq AI** | ✅ Free tier | console.groq.com | AI inference (30 req/min) |
| **Wayback Machine** | ✅ Yes | archive.org | Web archiving |
| **Archive.today** | ✅ Yes | archive.ph | Web archiving |
| **ReplayWeb.page** | ✅ Open source | replayweb.page | WARC viewer |
| **Internet Archive** | ✅ Yes | archive.org | WARC storage |

### **Verify No Paid Services:**

**Check Browser Network Tab:**
```
✅ ALLOWED: cdn.jsdelivr.net (free CDN)
✅ ALLOWED: archive.org (free archiving)
✅ ALLOWED: api.groq.com (free AI tier)
✅ ALLOWED: archive.ph (free archiving)

❌ BLOCK: Any payment processors
❌ BLOCK: Subscription services
❌ BLOCK: Paid CDNs (Cloudflare is OK, it's free)
```

---

## 🛠️ Automated Testing

**Run test script:**
```bash
# From project root
python3 test_features.py
```

**Expected Output:**
```
Testing: Streamlit Framework
✓ PASS: Streamlit imported successfully

Testing: BeautifulSoup (Text Diff)
✓ PASS: BeautifulSoup HTML parsing works

Testing: Free CDN (ReplayWeb.page)
✓ PASS: jsDelivr CDN accessible (free, no account needed)

...

Test Summary
============================================================
Total Tests: 10
Passed: 10
✅ WWWScope v2.1.0 is PRODUCTION READY
```

---

## 🐛 Troubleshooting

### **"AI Features Disabled"**
1. Check API key is correct (starts with `gsk_`)
2. Visit https://console.groq.com to verify key
3. Click "🧪 Test" button
4. Restart app if needed

### **"CDN returned status 403"**
1. Check internet connection
2. Try different network (some corporate networks block CDNs)
3. Verify: `curl -I https://cdn.jsdelivr.net/npm/replaywebpage@1.8.11/ui.js`

### **"Screenshot Feature Disabled"**
1. Install Selenium: `pip install selenium webdriver-manager`
2. Requires Chrome/Chromium browser
3. Restart app

### **"Archive.today CAPTCHA"**
1. This is normal (anti-bot protection)
2. Service is still free
3. Manual solving may be required
4. Try Wayback Machine instead

---

## ✅ Success Criteria

**Your installation is working correctly if:**

- [ ] All 4 AI models respond successfully
- [ ] Text diff shows color-coded changes
- [ ] AI explains changes in plain English
- [ ] ReplayWeb.page loads from free CDN (jsDelivr)
- [ ] At least one archive service works (Wayback or Archive.today)
- [ ] WARC files can be viewed (either mode)
- [ ] No payment or subscription prompts anywhere
- [ ] Browser Network tab shows only free services

---

## 📊 Performance Expectations

| Feature | Expected Time |
|---------|--------------|
| AI Response | 3-10 seconds |
| Text Diff | < 2 seconds |
| Screenshot | 10-20 seconds |
| WARC Upload | Varies by size |
| Archive Push | 5-60 seconds |
| CDN Load | < 3 seconds |

---

## 🎯 Quick Commands

```bash
# Start app
streamlit run app/app.py

# Run automated tests
python3 test_features.py

# Check dependencies
pip list | grep -E "(streamlit|groq|warcio|selenium|beautifulsoup4)"

# View test documentation
cat TESTING.md
```

---

## 📞 Support

**If you encounter issues:**

1. Check TESTING.md for detailed procedures
2. Verify all dependencies: `pip install -r requirements.txt`
3. Check browser console for errors (F12)
4. Verify Network tab shows only free services

**Common Issues:**
- Rate limiting → Wait 60 seconds, try again
- CAPTCHA → Normal for Archive.today
- Selenium errors → Check ChromeDriver installation
- AI errors → Verify Groq API key

---

**Last Updated:** January 2025
**Version:** 2.1.0
**Status:** ✅ Production Ready

All features tested and verified to use **100% free services**!
