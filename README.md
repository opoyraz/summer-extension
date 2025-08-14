# 🌞 Summer App: Complete Installation Guide for Beginners

This guide will help you install and run the **Summer Chrome Extension** - a multi-provider web page summarizer that uses Ollama (local), OpenAI, Groq, and IBM Watsonx. You'll learn how to set up everything from scratch using Python 3.12.

## What You'll Install

- **Python 3.12**: Required runtime for the FastAPI backend
- **Ollama**: Runs large language models locally on your computer  
- **CrewAI**: AI agent framework (installed via Python dependencies)
- **Summer Backend**: FastAPI server that handles summarization requests
- **Chrome Extension**: User interface for webpage summarization

## Prerequisites

- **Computer Requirements**: 8GB RAM minimum (16GB+ recommended for larger models)
- **Storage**: At least 15GB free space for models and dependencies
- **Internet**: Required for initial downloads
- **Chrome Browser**: For the extension

---

## Part 1: Install Python 3.12

The Summer app specifically requires Python 3.12 for optimal compatibility.

### Windows Installation

1. **Download Python 3.12**:
   - Go to [python.org/downloads](https://python.org/downloads)
   - Click "Download Python 3.12.x" (latest 3.12 version)
   
2. **Install Python**:
   - Run the downloaded installer
   - **⚠️ CRITICAL**: Check "Add Python 3.12 to PATH" during installation
   - Click "Install Now"
   
3. **Verify Installation**:
   Open Command Prompt (`Windows + R`, type `cmd`, press Enter):
   ```cmd
   python --version
   # Should show: Python 3.12.x
   
   pip --version
   # Should show pip version
   ```

### Mac Installation

1. **Using Homebrew** (recommended):
   ```bash
   # Install Homebrew if you don't have it
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install Python 3.12
   brew install python@3.12
   
   # Make it accessible as 'python'
   brew link python@3.12
   ```

2. **Alternative: Direct Download**:
   - Go to [python.org/downloads](https://python.org/downloads)
   - Download Python 3.12.x for macOS
   - Run the installer package

3. **Verify Installation**:
   Open Terminal (`Cmd + Space`, type "Terminal"):
   ```bash
   python3.12 --version
   # Should show: Python 3.12.x
   
   pip3.12 --version
   # Should show pip version
   ```

---

## Part 2: Install Ollama

Ollama runs AI models locally on your computer.

### Windows Installation

1. **Download Ollama**:
   - Visit [ollama.ai/download](https://ollama.ai/download)
   - Click "Download for Windows"
   - Run the installer (.exe file)

2. **Verify Installation**:
   Open Command Prompt:
   ```cmd
   ollama --version
   ```
   You should see version information.

3. **Start Ollama Service**:
   ```cmd
   ollama serve
   ```
   Keep this window open - you should see "Ollama is running on localhost:11434"

### Mac Installation

1. **Download and Install**:
   ```bash
   # Method 1: Direct download (recommended)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Method 2: Using Homebrew
   brew install ollama
   ```

2. **Start Ollama Service**:
   ```bash
   ollama serve
   ```
   Keep this terminal open.

3. **Verify Installation**:
   In a new terminal window:
   ```bash
   ollama --version
   ```

---

## Part 3: Download AI Models for Summer

Summer needs specific models to work. Start with these recommendations:

### Essential Models for Beginners

```bash
# Lightweight models (good for testing, 4-8GB RAM)
ollama pull llama3.2:3b       # Fast, basic summaries
ollama pull gemma2:2b         # Very lightweight

# Recommended models (8-16GB RAM)
ollama pull llama3.1:8b       # Best balance of speed and quality
ollama pull granite3.3:8b     # IBM's model, excellent for summaries

# High-quality models (16GB+ RAM)
ollama pull mistral:7b        # Excellent for detailed analysis
```

### Download Process
1. **Keep Ollama running** in one terminal/command prompt
2. **Open a new terminal/command prompt**
3. **Run the pull command**:
   ```bash
   ollama pull llama3.1:8b
   ```
4. **Wait for download** (5-30 minutes depending on model size and internet speed)
5. **Verify models are downloaded**:
   ```bash
   ollama list
   ```

### Model Size Guidelines
- **2B-3B models**: 2-4GB download, needs 4GB+ RAM, 5-15 seconds per summary
- **7B-8B models**: 4-6GB download, needs 8GB+ RAM, 15-45 seconds per summary
- **13B+ models**: 8GB+ download, needs 16GB+ RAM, 45-120 seconds per summary

---

## Part 4: Set Up the Summer App

### Step 1: Download and Prepare Summer Project
1. **Download** the Summer app files to your computer
2. **Create a folder** called `summer-app` on your desktop
3. **Extract all files** into this folder. You should have:
   ```
   summer-app/
   ├── main.py
   ├── agents.py  
   ├── requirements.txt
   ├── popup.html
   ├── popup.js
   ├── manifest.json
   ├── history.html
   ├── history.js
   ├── content.js
   └── styles.css
   ```

### Step 2: Open Terminal/Command Prompt in Summer Folder

**Windows:**
1. Open File Explorer
2. Navigate to your `summer-app` folder
3. Click in the address bar, type `cmd`, press Enter
4. Command Prompt opens in the correct folder

**Mac:**
1. Open Finder
2. Navigate to your `summer-app` folder
3. Right-click the folder, select "New Terminal at Folder"

### Step 3: Create Python Virtual Environment

This keeps Summer's dependencies separate from other Python projects.

**Windows:**
```cmd
python -m venv summer_env
summer_env\Scripts\activate
```

**Mac:**
```bash
python3.12 -m venv summer_env
source summer_env/bin/activate
```

✅ **Success indicator**: You should see `(summer_env)` at the beginning of your command prompt.

### Step 4: Install Summer Dependencies (Including CrewAI)

```bash
pip install -r requirements.txt
```

This installs all required packages:
- **CrewAI** (AI agent framework) 
- **FastAPI** (web server)
- **Uvicorn** (server runner)
- **Ollama integration** (langchain-community)
- **IBM Watsonx AI** (for enterprise models)
- **BeautifulSoup4** (web content extraction)
- **All other dependencies** needed for Summer

### Step 5: Create Configuration File (Optional but Recommended)

Create a file called `.env` in your summer-app folder:

**Windows (using Notepad):**
```cmd
notepad .env
```

**Mac (using TextEdit):**
```bash
touch .env
open -e .env
```

Add this content and save:
```bash
# Local Ollama settings
OLLAMA_HOST=localhost
OLLAMA_MODE=fast

# Optional: Add API keys for cloud providers if you have them
# OPENAI_API_KEY=sk-your-openai-key-here
# GROQ_API_KEY=gsk_your-groq-key-here
# WATSONX_API_KEY=your-watsonx-key-here
# WATSONX_URL=https://us-south.ml.cloud.ibm.com
# WATSONX_PROJECT_ID=your-project-id
```

---

## Part 5: Start and Test Summer

### Step 1: Start Ollama (First Terminal/Command Prompt)
**Keep this running in the background:**

```bash
ollama serve
```

You should see: `Ollama is running on localhost:11434`

### Step 2: Start Summer Backend (Second Terminal/Command Prompt)

Open a **new** terminal/command prompt in your summer-app folder and:

**Windows:**
```cmd
summer_env\Scripts\activate
python main.py
```

**Mac:**
```bash
source summer_env/bin/activate
python main.py
```

✅ **Success indicator**: You should see:
```
INFO: Uvicorn running on http://0.0.0.0:5050
```

### Step 3: Install Summer Chrome Extension

1. **Open Chrome** browser
2. **Go to Extensions**: Type `chrome://extensions/` in the address bar
3. **Enable Developer Mode**: Toggle the switch in the top right corner
4. **Load Extension**: Click "Load unpacked" button
5. **Select Folder**: Choose your `summer-app` folder (the main folder containing all files)
6. **Verify**: You should see "Summer - AI Summarizer" appear in your extensions list

### Step 4: Test Your Complete Setup

#### Test 1: Check Ollama Models
In any terminal/command prompt:
```bash
ollama list
```
Should show your downloaded models.

#### Test 2: Check Summer Backend
Open your browser and go to: `http://localhost:5050/providers`

You should see JSON data showing available providers.

#### Test 3: Test the Complete Summer Extension
1. **Go to any news article** or blog post (try BBC News, CNN, or Medium)
2. **Click the Summer extension icon** in your Chrome toolbar
3. **Select "Ollama (Local)"** as provider
4. **Choose one of your downloaded models** (e.g., `llama3.1:8b`)
5. **Click "Summarize"**
6. **Wait 15-60 seconds** - you should get a summary of the webpage!

---

## Part 6: Daily Usage Guide

### Starting Summer (Every Time You Want to Use It)

1. **Start Ollama** (in one terminal):
   ```bash
   ollama serve
   ```

2. **Start Summer Backend** (in another terminal):
   **Windows:**
   ```cmd
   cd path\to\your\summer-app
   summer_env\Scripts\activate
   python main.py
   ```
   
   **Mac:**
   ```bash
   cd path/to/your/summer-app
   source summer_env/bin/activate
   python main.py
   ```

3. **Use the Chrome extension** - it's always available once loaded!

### Stopping Summer

- **Close terminals** running Ollama and Summer backend
- **Chrome extension stays loaded** until you remove it

---

## Troubleshooting Common Issues

### Python 3.12 Issues

**"Python not found" or "python is not recognized"**
- **Windows**: Restart Command Prompt, ensure "Add to PATH" was checked during installation
- **Mac**: Use `python3.12` instead of `python`
- **Reinstall** Python 3.12 if needed, making sure to check PATH option

**"No module named 'fastapi'" or similar dependency errors**
- **Check virtual environment**: `(summer_env)` should show in your prompt
- **Reactivate environment**: Run the activation command again
- **Reinstall dependencies**: `pip install -r requirements.txt`

### Ollama Issues

**"Ollama not found" or "Command not found"**
- **Restart terminal** after installing Ollama
- **Windows**: Try running Command Prompt as Administrator
- **Mac**: Try `brew install ollama` if direct install failed

**"Connection refused" to localhost:11434**
- **Start Ollama**: Make sure `ollama serve` is running
- **Check port**: Run `ollama ps` to see if Ollama is active
- **Restart Ollama**: Close and restart `ollama serve`

**"Model not found" error in Summer extension**
- **List models**: `ollama list` to see what's downloaded
- **Download model**: `ollama pull llama3.1:8b` (or the model you want)
- **Check exact name**: Model names in Summer must match exactly

### Summer Backend Issues

**"Failed to connect to backend" in Chrome extension**
- **Check backend is running**: Look for "Uvicorn running on http://0.0.0.0:5050"
- **Test manually**: Open `http://localhost:5050/providers` in browser
- **Check virtual environment**: Make sure `(summer_env)` is active
- **Restart backend**: Close and restart `python main.py`

**"Address already in use" error**
- **Close existing backend**: Find and close any running `python main.py` processes
- **Change port**: Edit `main.py` and change `port=5050` to `port=5051`

### Chrome Extension Issues

**Extension doesn't appear after loading**
- **Check all files**: Ensure `manifest.json` is in the summer-app folder
- **Developer mode**: Must be enabled in `chrome://extensions/`
- **Reload extension**: Click the refresh icon on the extension card

**"Failed to access the current tab" error**
- **Refresh the webpage** you're trying to summarize
- **Try a different website**: Some sites block content extraction
- **Check HTTPS**: Some secure sites have restrictions

**Extension loads but summarization fails**
- **Check browser console**: Press F12 → Console tab for error messages
- **Verify backend**: Test `http://localhost:5050/providers` in browser
- **Check model**: Verify your selected model is downloaded with `ollama list`

### Performance Issues

**Models are very slow**
- **Use smaller models**: Try `llama3.2:3b` instead of `llama3.1:8b`
- **Close other applications**: Free up RAM and CPU
- **Check RAM usage**: Use Task Manager (Windows) or Activity Monitor (Mac)

**"Out of memory" errors**
- **Use smaller models**: Stick to 3B or 7B models
- **Close browser tabs**: Free up system memory
- **Restart Ollama**: `ollama serve` fresh

---

## Performance Tips & Model Recommendations

### For Computers with 4-8GB RAM
```bash
ollama pull llama3.2:3b      # Fast, good quality
ollama pull gemma2:2b        # Very fast, basic summaries
```
**Expected speed**: 5-15 seconds per summary

### For Computers with 8-16GB RAM  
```bash
ollama pull llama3.1:8b      # Best balance of speed/quality (recommended)
ollama pull granite3.3:8b    # Excellent for professional content
```
**Expected speed**: 15-45 seconds per summary

### For High-End Systems (16GB+ RAM)
```bash
ollama pull mistral:7b       # Excellent quality
ollama pull codellama:13b    # Great for technical content
```
**Expected speed**: 45-120 seconds per summary

### Managing Disk Space
```bash
# Remove unused models
ollama rm model_name

# Check what's using space
ollama list

# Models stored in:
# Windows: C:\Users\username\.ollama\models
# Mac: ~/.ollama/models
```

---

## Advanced Features

### Using Cloud Providers
Add API keys to your `.env` file to use cloud models alongside local Ollama:

```bash
# OpenAI (for comparison)
OPENAI_API_KEY=sk-your-key-here

# Groq (very fast cloud inference)  
GROQ_API_KEY=gsk_your-key-here
```

### CrewAI Agentic Mode
For more detailed analysis, set in `.env`:
```bash
OLLAMA_MODE=agentic  # Uses multiple AI agents for deeper analysis
# vs
OLLAMA_MODE=fast     # Direct API calls (default, faster)
```

### Custom Instructions
In the Summer extension, try different instruction styles:
- "Create a TL;DR summary"
- "Executive summary for business use"
- "Extract key technical points"
- "Summarize for a 10-year-old"

---

## What's Next?

### Explore Summer Features
1. **Try different models**: Compare `llama3.1:8b` vs `granite3.3:8b`
2. **Use custom instructions**: Experiment with different summary styles
3. **View history**: Click "View History" to see all past summaries
4. **Test different content**: Try news, blogs, research papers, documentation

### Content That Works Best with Summer
- **News Articles**: Excellent results with any 7B+ model
- **Blog Posts**: Great for extracting key insights  
- **Research Papers**: Use larger models or enterprise providers
- **Documentation**: Technical content works well with `granite3.3:8b`
- **Product Reviews**: Good for feature extraction

---

## Need Help?

### Quick Diagnostics
```bash
# Check what's running
# Windows:
tasklist | findstr ollama
tasklist | findstr python

# Mac:
ps aux | grep ollama
ps aux | grep python
```

### Test Connectivity
```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Test Summer backend  
curl http://localhost:5050/providers
```

### Get Support
- **Ollama Issues**: [github.com/ollama/ollama](https://github.com/ollama/ollama)
- **CrewAI Documentation**: [crewai.io/docs](https://crewai.io/docs)
- **Python 3.12 Help**: [python.org/doc](https://python.org/doc)

---

## Quick Start Checklist

✅ Install Python 3.12 with PATH  
✅ Install Ollama  
✅ Download at least one model (`ollama pull llama3.1:8b`)  
✅ Download Summer app files  
✅ Create virtual environment  
✅ Install dependencies (`pip install -r requirements.txt`)  
✅ Start Ollama (`ollama serve`)  
✅ Start Summer backend (`python main.py`)  
✅ Load Chrome extension  
✅ Test on a webpage  

**Congratulations! You now have a complete local AI summarization system running on your computer! 🌞**
