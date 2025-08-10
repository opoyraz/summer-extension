document.addEventListener("DOMContentLoaded", () => {
  const historyContainer = document.getElementById("historyContainer");
  const clearHistoryBtn = document.getElementById("clearHistoryBtn");
  const backBtn = document.getElementById("backBtn");

  // Load and display history
  function loadHistory() {
    chrome.storage.local.get(["summer_summaries"], (result) => {
      const summaries = result.summer_summaries || [];
      
      if (summaries.length === 0) {
        historyContainer.innerHTML = '<p style="text-align: center; color: #666;">No summaries yet!</p>';
        return;
      }

      historyContainer.innerHTML = "";
      
      summaries.forEach((item, index) => {
        const card = document.createElement("div");
        card.className = "summary-card";
        
        // Format timestamp
        const date = new Date(item.timestamp);
        const formattedDate = date.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
        
        // Handle old summaries that might not have provider/model info
        const provider = item.provider || "Unknown";
        const model = item.model || "Unknown";
        
        // Create model info display with color coding
        const modelInfoColor = {
          'openai': '#10a37f',
          'groq': '#f97316',
          'ollama': '#2563eb',
          'watsonx': '#1f2937',
          'unknown': '#6b7280'
        };
        
        const color = modelInfoColor[provider.toLowerCase()] || modelInfoColor['unknown'];
        
        card.innerHTML = `
          <pre>${item.summary}</pre>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
            <small>${formattedDate}</small>
            <span style="
              background: ${color}; 
              color: white; 
              padding: 2px 8px; 
              border-radius: 12px; 
              font-size: 11px;
              font-weight: bold;
            ">
              ${provider.toUpperCase()} - ${model}
            </span>
          </div>
          <button class="copy-btn" data-index="${index}" style="
            background-color: #4CAF50;
            color: white;
            margin-top: 8px;
            padding: 6px;
            font-size: 14px;
          ">
            📋 Copy Summary
          </button>
        `;
        
        historyContainer.appendChild(card);
      });
      
      // Add copy functionality to all copy buttons
      document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', function() {
          const index = this.getAttribute('data-index');
          const summaryText = summaries[index].summary;
          
          navigator.clipboard.writeText(summaryText).then(() => {
            const originalText = this.innerText;
            this.innerText = "✅ Copied!";
            this.style.backgroundColor = "#27ae60";
            
            setTimeout(() => {
              this.innerText = originalText;
              this.style.backgroundColor = "#4CAF50";
            }, 2000);
          }).catch(err => {
            console.error("Failed to copy:", err);
            // Fallback for older browsers
            const textArea = document.createElement("textarea");
            textArea.value = summaryText;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            this.innerText = "✅ Copied!";
            this.style.backgroundColor = "#27ae60";
            setTimeout(() => {
              this.innerText = "📋 Copy Summary";
              this.style.backgroundColor = "#4CAF50";
            }, 2000);
          });
        });
      });
    });
  }

  // Clear history
  clearHistoryBtn.addEventListener("click", () => {
    if (confirm("Are you sure you want to clear all summary history?")) {
      chrome.storage.local.set({ "summer_summaries": [] }, () => {
        historyContainer.innerHTML = '<p style="text-align: center; color: #666;">History cleared!</p>';
        setTimeout(loadHistory, 1500);
      });
    }
  });

  // Back button
  backBtn.addEventListener("click", () => {
    window.close();
  });

  // Load history on page load
  loadHistory();
});