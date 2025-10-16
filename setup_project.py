#!/usr/bin/env python3
"""
WWWScope Setup Script - Creates organized project structure
Run: python setup_project.py
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

print("=" * 60)
print("🌍 WWWScope Project Setup")
print("=" * 60)
print()

# Create project directory
project_dir = Path("wwwscope-project")
project_dir.mkdir(exist_ok=True)

# Create folder structure
print("📁 Creating folder structure...")
dirs = [
    "app/core", "app/integrations", "docs/guides", "docs/analysis",
    "tests", ".streamlit", ".github/workflows", "deployment", "assets"
]
for d in dirs:
    (project_dir / d).mkdir(parents=True, exist_ok=True)
    print(f"  ✅ {d}")

# Copy and rename files from src/
print("\n📋 Copying files from src/...")
file_map = {
    "src/rate_limiter.py": "app/core/rate_limiter.py",
    "src/ia_uploader.py": "app/core/ia_uploader.py",
    "src/archive_services.py": "app/core/archive_services.py",
    "src/app.py": "app/app.py",
}

for src, dst in file_map.items():
    src_path = Path(src)
    if src_path.exists():
        dst_path = project_dir / dst
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dst_path)
        print(f"  ✅ {src} → {dst}")
    else:
        print(f"  ⚠️  {src} not found (skipping)")

# Create __init__.py files
print("\n🐍 Creating __init__.py files...")
for init in ["app/__init__.py", "app/core/__init__.py", "app/integrations/__init__.py", "tests/__init__.py"]:
    (project_dir / init).touch()

# Create requirements.txt
print("\n📦 Creating requirements.txt...")
(project_dir / "requirements.txt").write_text("""# Core dependencies
streamlit>=1.28.0
requests>=2.31.0

# Internet Archive
internetarchive>=3.5.0

# WARC handling
warcio>=1.7.4
beautifulsoup4>=4.12.0

# Optional dependencies
boto3>=1.28.0
selenium>=4.15.0

# Testing
pytest>=7.4.0
""")

# Create .gitignore
print("🚫 Creating .gitignore...")
(project_dir / ".gitignore").write_text("""# Python
__pycache__/
*.py[cod]
venv/
env/

# Streamlit
.streamlit/secrets.toml

# Local data
*.warc
*.warc.gz
local_archives/

# IDE
.vscode/
.idea/
.DS_Store

# Logs
*.log
""")

# Create Streamlit config
print("⚙️  Creating Streamlit config...")
(project_dir / ".streamlit/config.toml").write_text("""[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f5f5f5"

[server]
maxUploadSize = 500
enableXsrfProtection = true

[browser]
gatherUsageStats = false
""")

(project_dir / ".streamlit/secrets.toml.example").write_text("""# Copy this file to secrets.toml and add your credentials

# Internet Archive credentials
ia_access_key = "your-access-key-here"
ia_secret_key = "your-secret-key-here"
""")

# Create README
print("📖 Creating README...")
(project_dir / "README.md").write_text("""# 🌍 WWWScope - Web Archive & Retrieval Tool

Archive, compare, and sync web history with ease.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app/app.py
```

## Features

- 📥 Multi-service archiving
- 🔄 Internet Archive sync
- ⚡ Smart rate limiting
- 🐛 All bugs fixed!

## Deploy

See docs/ for deployment instructions.

## License

GPL-3.0
""")

# Create git-init scripts
print("🔧 Creating Git scripts...")
(project_dir / "git-init.sh").write_text("""#!/bin/bash
echo "🚀 Initializing Git repository..."
git init
git add .
git commit -m "Initial commit: WWWScope project structure"
echo ""
echo "✅ Git initialized!"
echo ""
echo "Next steps:"
echo "  1. Create GitHub repo"
echo "  2. git remote add origin https://github.com/yourusername/wwwscope.git"
echo "  3. git push -u origin main"
""")

(project_dir / "git-init.bat").write_text("""@echo off
echo Initializing Git repository...
git init
git add .
git commit -m "Initial commit: WWWScope project structure"
echo.
echo Git initialized!
echo.
echo Next steps:
echo   1. Create GitHub repo
echo   2. git remote add origin https://github.com/yourusername/wwwscope.git
echo   3. git push -u origin main
pause
""")

# Note: app.py is already copied from src/ in the file_map above
print("📝 app.py copied from src/ (full application)")

# Summary
print("\n" + "=" * 60)
print("✅ Setup Complete!")
print("=" * 60)
print(f"\n📁 Project location: {project_dir.absolute()}")
print("\n📋 Next steps:")
print("  1. Test: cd wwwscope-project && streamlit run app/app.py")
print("  2. Git: cd wwwscope-project && ./git-init.sh (or git-init.bat)")
print("  3. Push to GitHub and deploy!")
print("\n🎉 Ready for deployment!")
