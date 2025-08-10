const providerSelect = document.getElementById("provider");
const ollamaOptions = document.getElementById("ollama-options");
const openaiOptions = document.getElementById("openai-options");
const groqOptions = document.getElementById("groq-options");
const watsonxOptions = document.getElementById("watsonx-options");

const progressContainer = document.getElementById("progress-container");
const progressBar = document.getElementById("progress-bar");
const progressLabel = document.getElementById("progress-label");
const output = document.getElementById("output");

// Store provider configuration from backend
let providerConfig = {};

// Chrome Extension error handling
function handleChromeError(operation) {
  if (chrome.runtime.lastError) {
    console.error(`Chrome extension error during ${operation}:`, chrome.runtime.lastError);
    return false;
  }
  return true;
}

// Check if running in Chrome extension context
if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.id) {
  console.log('✅ Running in Chrome extension context');
} else {
  console.warn('⚠️ Not running in Chrome extension context');
}

// Check provider configuration from backend
async function checkProviderConfig() {
  try {
    console.log("🔍 Checking provider configuration...");
    const response = await fetch("http://localhost:5050/providers");
    
    if (response.ok) {
      providerConfig = await response.json();
      console.log("📋 Provider config:", providerConfig);
      updateUIBasedOnConfig();
    } else {
      console.warn("⚠️ Could not fetch provider config");
      providerConfig = {};
    }
  } catch (error) {
    console.warn("⚠️ Backend not available for provider config check:", error);
    providerConfig = {};
  }
}

// Update UI based on provider configuration
function updateUIBasedOnConfig() {
  // OpenAI
  const openaiApikey = document.getElementById("openai-apikey");
  const openaiEnvLabel = document.getElementById("openai-env-label");
  if (providerConfig.openai?.has_apikey) {
    openaiApikey.classList.add("env-configured");
    openaiApikey.placeholder = "API key configured in .env";
    openaiEnvLabel.classList.add("show");
  }

  // Groq
  const groqApikey = document.getElementById("groq-apikey");
  const groqEnvLabel = document.getElementById("groq-env-label");
  if (providerConfig.groq?.has_apikey) {
    groqApikey.classList.add("env-configured");
    groqApikey.placeholder = "API key configured in .env";
    groqEnvLabel.classList.add("show");
  }

  // Watsonx
  const watsonxApikey = document.getElementById("watsonx-apikey");
  const projectId = document.getElementById("project-id");
  const spaceId = document.getElementById("space-id");
  const watsonxUrl = document.getElementById("watsonx-url");
  
  if (providerConfig.watsonx?.has_apikey) {
    watsonxApikey.classList.add("env-configured");
    watsonxApikey.placeholder = "API key configured in .env";
    document.getElementById("watsonx-apikey-env-label").classList.add("show");
  }
  
  if (providerConfig.watsonx?.has_project_id) {
    projectId.classList.add("env-configured");
    projectId.placeholder = "Project ID configured in .env";
    document.getElementById("watsonx-project-env-label").classList.add("show");
  }
  
  if (providerConfig.watsonx?.has_space_id) {
    spaceId.classList.add("env-configured");
    spaceId.placeholder = "Space ID configured in .env";
    document.getElementById("watsonx-space-env-label").classList.add("show");
  }
  
  if (providerConfig.watsonx?.has_url) {
    watsonxUrl.classList.add("env-configured");
    watsonxUrl.placeholder = "URL configured in .env";
    document.getElementById("watsonx-url-env-label").classList.add("show");
  }
}

function showProgress(percent, label = "Processing...") {
  progressContainer.style.display = "block";
  progressBar.style.width = `${percent}%`;
  progressLabel.innerText = label;
}

function hideProgress() {
  progressContainer.style.display = "none";
  progressBar.style.width = "0%";
}

function animatedTyping(text, element) {
  element.innerText = "";
  let i = 0;
  const interval = setInterval(() => {
    if (i < text.length) {
      element.innerText += text.charAt(i);
      i++;
    } else {
      clearInterval(interval);
    }
  }, 20);
}

// Faster animated typing function (3 chars at once, 10ms interval)
function animatedTypingFast(text, element) {
  console.log("Starting fast animation with text length:", text ? text.length : "text is null/undefined");
  
  if (!element) {
    console.error("Element is null/undefined");
    return;
  }
  
  if (!text) {
    console.error("Text is null/undefined");
    element.innerText = "";
    return;
  }
  
  element.innerText = "";
  let i = 0;
  const interval = setInterval(() => {
    try {
      if (i < text.length) {
        // Add multiple characters at once for faster typing
        const charsToAdd = Math.min(3, text.length - i);
        element.innerText += text.substring(i, i + charsToAdd);
        i += charsToAdd;
      } else {
        console.log("Animation complete");
        clearInterval(interval);
      }
    } catch (err) {
      console.error("Error during animation:", err);
      clearInterval(interval);
      element.innerText = text; // Fallback to show full text
    }
  }, 10);
}

// Chrome Extension storage functions
function saveSummary(summary, provider, model) {
  chrome.storage.local.get(["summer_summaries"], (result) => {
    if (!handleChromeError("saveSummary get")) return;
    
    let history = result.summer_summaries || [];
    history.unshift({ 
      summary,                           // The summary text
      timestamp: Date.now(),             // The timestamp
      provider: provider || "unknown",   // The provider (OpenAI, Groq, etc.)
      model: model || "unknown"          // The specific model used
    });
    if (history.length > 10) history = history.slice(0, 10);
    
    chrome.storage.local.set({ "summer_summaries": history }, () => {
      handleChromeError("saveSummary set");
    });
  });
}

// Save model name to provider-specific history
function saveModelToHistory(provider, modelName) {
  if (!modelName || !modelName.trim()) return;
  
  chrome.storage.local.get(["model_history"], (result) => {
    if (!handleChromeError("saveModelToHistory get")) return;
    
    let modelHistory = result.model_history || {};
    
    // Initialize provider array if doesn't exist
    if (!modelHistory[provider]) {
      modelHistory[provider] = [];
    }
    
    // Remove if already exists (to move to top)
    modelHistory[provider] = modelHistory[provider].filter(m => m !== modelName);
    
    // Add to beginning
    modelHistory[provider].unshift(modelName);
    
    // Keep only last 5 models per provider
    if (modelHistory[provider].length > 5) {
      modelHistory[provider] = modelHistory[provider].slice(0, 5);
    }
    
    chrome.storage.local.set({ "model_history": modelHistory }, () => {
      handleChromeError("saveModelToHistory set");
      console.log(`Saved model ${modelName} to ${provider} history`);
    });
  });
}

// Load model history and create datalist
function loadModelHistory() {
  chrome.storage.local.get(["model_history"], (result) => {
    if (!handleChromeError("loadModelHistory get")) return;
    
    const modelHistory = result.model_history || {};
    console.log("Loading model history:", modelHistory);
    
    // Update datalists for each provider
    updateDatalist("openai-models", modelHistory.openai || []);
    updateDatalist("groq-models", modelHistory.groq || []);
    updateDatalist("watsonx-models", modelHistory.watsonx || []);
    updateDatalist("ollama-custom-models", modelHistory.ollama || []);
  });
}

// Update datalist with model names
function updateDatalist(datalistId, models) {
  const datalist = document.getElementById(datalistId);
  if (!datalist) {
    console.log(`Datalist ${datalistId} not found`);
    return;
  }
  
  // Clear existing options
  datalist.innerHTML = "";
  
  // Add new options
  models.forEach(model => {
    const option = document.createElement("option");
    option.value = model;
    datalist.appendChild(option);
  });
  
  console.log(`Updated ${datalistId} with ${models.length} models`);
}

function showCopyButton(text) {
  const btn = document.getElementById("copy-button");
  btn.style.display = "block";
  btn.onclick = () => {
    navigator.clipboard.writeText(text).then(() => {
      btn.innerText = "✅ Copied!";
      setTimeout(() => (btn.innerText = "📋 Copy"), 2000);
    }).catch(err => {
      console.error("Copy failed:", err);
      // Fallback for older browsers
      const textArea = document.createElement("textarea");
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      btn.innerText = "✅ Copied!";
      setTimeout(() => (btn.innerText = "📋 Copy"), 2000);
    });
  };
}

function showBackButton() {
  const backBtn = document.getElementById("back-button");
  backBtn.style.display = "block";
  backBtn.onclick = () => {
    document.getElementById("form").style.display = "block";
    output.style.opacity = 0;
    output.innerText = "";
    backBtn.style.display = "none";
    document.getElementById("copy-button").style.display = "none";
    document.body.classList.remove('expanded');
  };
}

// Handle provider selection
providerSelect.onchange = () => {
  const provider = providerSelect.value;
  
  // Hide all options first
  ollamaOptions.classList.add("hidden");
  openaiOptions.classList.add("hidden");
  groqOptions.classList.add("hidden");
  watsonxOptions.classList.add("hidden");
  
  // Show relevant options
  if (provider === "ollama") {
    ollamaOptions.classList.remove("hidden");
  } else if (provider === "openai") {
    openaiOptions.classList.remove("hidden");
  } else if (provider === "groq") {
    groqOptions.classList.remove("hidden");
  } else if (provider === "watsonx") {
    watsonxOptions.classList.remove("hidden");
  }
  
  // Reload model history to update datalists
  loadModelHistory();
};

// Handle model selection for each provider
document.getElementById("ollama-model").onchange = () => {
  const isOther = document.getElementById("ollama-model").value === "other";
  document.getElementById("custom-ollama-model").classList.toggle("hidden", !isOther);
};

document.getElementById("openai-model").onchange = () => {
  const isOther = document.getElementById("openai-model").value === "other";
  document.getElementById("custom-openai-model").classList.toggle("hidden", !isOther);
};

document.getElementById("groq-model").onchange = () => {
  const isOther = document.getElementById("groq-model").value === "other";
  document.getElementById("custom-groq-model").classList.toggle("hidden", !isOther);
};

document.getElementById("watsonx-model").onchange = () => {
  const isOther = document.getElementById("watsonx-model").value === "other";
  document.getElementById("custom-watsonx-model").classList.toggle("hidden", !isOther);
};

// Initialize with default provider (ollama)
providerSelect.dispatchEvent(new Event('change'));

// Load model history and check provider config on startup
loadModelHistory();
checkProviderConfig();

// Close window button
document.getElementById("closeWindowBtn").onclick = () => {
  window.close();
};

// Main summarization function
document.getElementById("summarize").onclick = async () => {
  const provider = providerSelect.value;
  const instructions = document.getElementById("instructions").value.trim();
  
  console.log("🚀 Starting summarization with provider:", provider);
  
  let model = "";
  let apikey = "";
  let config = { provider, instructions };

  // Get model and API key based on provider
  if (provider === "ollama") {
    const modelSelect = document.getElementById("ollama-model");
    model = modelSelect.value === "other" 
      ? document.getElementById("custom-ollama-model").value.trim()
      : modelSelect.value;
    
    if (!model) {
      alert("❌ Please select or enter an Ollama model.");
      return;
    }
    
    // Save custom Ollama model to history
    if (modelSelect.value === "other" && model) {
      saveModelToHistory("ollama", model);
    }
    
  } else if (provider === "openai") {
    const modelSelect = document.getElementById("openai-model");
    model = modelSelect.value === "other" 
      ? document.getElementById("custom-openai-model").value.trim()
      : modelSelect.value;
    
    apikey = document.getElementById("openai-apikey").value.trim();
    
    if (!model) {
      alert("❌ Please select or enter an OpenAI model.");
      return;
    }
    
    // Only require API key if not configured in .env
    if (!apikey && !providerConfig.openai?.has_apikey) {
      alert("❌ Please enter OpenAI API key.");
      return;
    }
    
    // Save model to history
    if (modelSelect.value === "other" && model) {
      saveModelToHistory("openai", model);
    }
    
  } else if (provider === "groq") {
    const modelSelect = document.getElementById("groq-model");
    model = modelSelect.value === "other" 
      ? document.getElementById("custom-groq-model").value.trim()
      : modelSelect.value;
    
    apikey = document.getElementById("groq-apikey").value.trim();
    
    if (!model) {
      alert("❌ Please select or enter a Groq model.");
      return;
    }
    
    // Only require API key if not configured in .env
    if (!apikey && !providerConfig.groq?.has_apikey) {
      alert("❌ Please enter Groq API key.");
      return;
    }
    
    // Save model to history
    if (modelSelect.value === "other" && model) {
      saveModelToHistory("groq", model);
    }
    
  } else if (provider === "watsonx") {
    const modelSelect = document.getElementById("watsonx-model");
    model = modelSelect.value === "other" 
      ? document.getElementById("custom-watsonx-model").value.trim()
      : modelSelect.value;
    
    apikey = document.getElementById("watsonx-apikey").value.trim();
    config.project_id = document.getElementById("project-id").value.trim();
    config.space_id = document.getElementById("space-id").value.trim();
    config.watsonx_url = document.getElementById("watsonx-url").value.trim();
    
    if (!model) {
      alert("❌ Please select or enter a Watsonx model.");
      return;
    }
    
    // Check required fields (only if not configured in .env)
    const missingFields = [];
    if (!apikey && !providerConfig.watsonx?.has_apikey) missingFields.push("API Key");
    if (!config.watsonx_url && !providerConfig.watsonx?.has_url) missingFields.push("Watsonx URL");
    
    // Require EITHER project_id OR space_id, not both
    const hasProjectId = config.project_id || providerConfig.watsonx?.has_project_id;
    const hasSpaceId = config.space_id || providerConfig.watsonx?.has_space_id;
    
    if (!hasProjectId && !hasSpaceId) {
      missingFields.push("Project ID or Space ID");
    }
    
    if (missingFields.length > 0) {
      alert(`❌ Please fill in: ${missingFields.join(", ")}`);
      return;
    }
    
    // Save model to history
    if (modelSelect.value === "other" && model) {
      saveModelToHistory("watsonx", model);
    }
  }

  config.model = model;
  config.apikey = apikey;

  console.log("📋 Configuration:", { 
    provider, 
    model, 
    hasApiKey: !!apikey,
    hasInstructions: !!instructions 
  });

  // Get active tab
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    // Extract text from the page
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        console.log("🔍 Starting text extraction...");
        
        let extractedText = "";
        
        // Strategy 1: Try main content areas
        const contentSelectors = [
          'article',
          'main', 
          '[role="main"]',
          '.content',
          '.post-content',
          '.entry-content',
          '.article-content',
          '.main-content',
          '#content'
        ];
        
        for (const selector of contentSelectors) {
          const element = document.querySelector(selector);
          if (element) {
            const text = element.innerText || element.textContent || '';
            if (text.trim().length > 200) {
              extractedText = text;
              console.log(`✅ Found content using: ${selector}`);
              break;
            }
          }
        }
        
        // Strategy 2: Extract from paragraphs if main content not found
        if (!extractedText || extractedText.length < 200) {
          console.log("🔄 Trying paragraph extraction...");
          const paragraphs = Array.from(document.querySelectorAll('p'));
          const paraText = paragraphs
            .map(p => (p.innerText || p.textContent || '').trim())
            .filter(text => text.length > 20)
            .join('\n\n');
          
          if (paraText.length > extractedText.length) {
            extractedText = paraText;
          }
        }
        
        // Strategy 3: Fallback to body text with cleanup
        if (!extractedText || extractedText.length < 100) {
          console.log("🔄 Using body fallback...");
          
          // Remove navigation, header, footer elements
          const elementsToRemove = document.querySelectorAll(
            'nav, header, footer, aside, .navigation, .menu, .sidebar, .ads, .advertisement'
          );
          
          // Clone body to avoid modifying the actual page
          const bodyClone = document.body.cloneNode(true);
          
          // Remove unwanted elements from clone
          elementsToRemove.forEach(el => {
            const clonedEl = bodyClone.querySelector(el.tagName.toLowerCase() + 
              (el.className ? '.' + el.className.split(' ').join('.') : ''));
            if (clonedEl) clonedEl.remove();
          });
          
          extractedText = bodyClone.innerText || bodyClone.textContent || '';
        }
        
        // Clean up the text
        extractedText = extractedText
          .replace(/\s+/g, ' ')           // Multiple spaces to single
          .replace(/\n\s*\n/g, '\n\n')   // Multiple newlines to double
          .trim();
        
        console.log(`📊 Extracted ${extractedText.length} characters`);
        console.log(`📄 Preview: ${extractedText.substring(0, 300)}...`);
        
        return extractedText;
      }
    }, async (results) => {
      
      if (!handleChromeError("text extraction")) return;
      
      const extractedText = results[0]?.result || "";
      
      console.log("📥 Received extracted text:", extractedText.length, "characters");
      
      if (!extractedText || extractedText.length < 50) {
        alert("❌ Could not extract meaningful content from this page. Try a different page or check if the content has loaded properly.");
        return;
      }

      // Limit text length to prevent issues
      const maxLength = 6000;
      const finalText = extractedText.length > maxLength 
        ? extractedText.substring(0, maxLength) + "..."
        : extractedText;

      console.log("📤 Sending to backend:", finalText.length, "characters");

      // Show progress
      let percent = 10;
      showProgress(percent, "Connecting...");

      const progressInterval = setInterval(() => {
        percent = Math.min(percent + 8, 85);
        showProgress(percent, "Processing...");
      }, 400);

      try {
        const payload = {
          text: finalText,
          ...config
        };

        console.log("📦 Full payload:", {
          ...payload,
          text: `${payload.text.substring(0, 100)}... (${payload.text.length} chars)`
        });

        const response = await fetch("http://localhost:5050/summarize", {
          method: "POST",
          headers: { 
            "Content-Type": "application/json"
          },
          body: JSON.stringify(payload)
        });

        clearInterval(progressInterval);
        showProgress(100, "Complete!");

        console.log("📨 Response status:", response.status);

        const data = await response.json();
        console.log("📨 Response data:", data);

        if (!response.ok) {
          console.error("❌ Backend error:", data);
          alert(`❌ Error: ${data.error || "Unknown backend error"}`);
          hideProgress();
          return;
        }

        const summaryText = typeof data.summary === "string" 
          ? data.summary 
          : JSON.stringify(data.summary, null, 2);

        if (!summaryText || summaryText.trim().length === 0) {
          alert("❌ Received empty summary from backend.");
          hideProgress();
          return;
        }

        console.log("✅ Summary received:", summaryText.length, "characters");

        // Show results
        document.getElementById("form").style.display = "none";
        output.style.opacity = 1;
        
        // Option 1: Instant display (currently active)
        output.innerText = `Summary:\n\n${summaryText}`;
        document.body.classList.add('expanded');
        
        // Option 2: Original animated typing - 1 char every 20ms (commented out)
        // animatedTyping(`Summary:\n\n${summaryText}`, output);
        
        // Option 3: Faster animated typing - 3 chars every 10ms (commented out)
        // animatedTypingFast(`Summary:\n\n${summaryText}`, output);
        
        showCopyButton(summaryText);
        showBackButton();
        saveSummary(summaryText, provider, model);

        setTimeout(hideProgress, 1000);

      } catch (error) {
        clearInterval(progressInterval);
        hideProgress();
        console.error("🔥 Network error:", error);
        alert("❌ Failed to connect to backend. Make sure the server is running on http://localhost:5050");
      }
    });

  } catch (error) {
    console.error("❌ Chrome API error:", error);
    alert("❌ Failed to access the current tab. Please try refreshing the page.");
  }
};

// View History
document.getElementById("history-button").onclick = () => {
  chrome.tabs.create({ url: chrome.runtime.getURL("history.html") }, () => {
    handleChromeError("history tab creation");
  });
};