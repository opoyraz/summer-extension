// content.js - Chrome Extension
window.addEventListener("message", (event) => {
  if (event.data.type === "INSERT_SUMMARY") {
    // Remove existing summary box if any
    const existingBox = document.getElementById("crew-summary-box");
    if (existingBox) {
      existingBox.remove();
    }

    const box = document.createElement("div");
    box.id = "crew-summary-box";
    box.innerHTML = `<h4>✨ Summer Summary</h4><p>${event.data.summary}</p>`;
    
    // Chrome Extension specific styling
    box.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      max-width: 350px;
      padding: 15px;
      background: linear-gradient(to bottom right, #ffffffdd, #f0f0f0ee);
      border: 1px solid #ccc;
      border-radius: 20px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 9999;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      font-size: 14px;
      backdrop-filter: blur(10px);
      animation: slideIn 0.3s ease-out;
    `;
    
    // Add animation keyframes
    if (!document.getElementById('summer-animation-styles')) {
      const styleSheet = document.createElement('style');
      styleSheet.id = 'summer-animation-styles';
      styleSheet.textContent = `
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(100px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        #crew-summary-box h4 {
          margin-top: 0;
          font-weight: 600;
          color: #333;
          font-size: 16px;
        }
        
        #crew-summary-box p {
          margin: 10px 0 0;
          line-height: 1.4;
          color: #555;
        }
        
        #crew-summary-box:hover {
          box-shadow: 0 6px 20px rgba(0,0,0,0.2);
          transition: box-shadow 0.3s ease;
        }
      `;
      document.head.appendChild(styleSheet);
    }
    
    document.body.appendChild(box);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
      if (box && box.parentNode) {
        box.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => {
          if (box && box.parentNode) {
            box.remove();
          }
        }, 300);
      }
    }, 10000);
    
    // Add slideOut animation
    if (!document.getElementById('summer-slideout-styles')) {
      const slideOutStyle = document.createElement('style');
      slideOutStyle.id = 'summer-slideout-styles';
      slideOutStyle.textContent = `
        @keyframes slideOut {
          from {
            opacity: 1;
            transform: translateX(0);
          }
          to {
            opacity: 0;
            transform: translateX(100px);
          }
        }
      `;
      document.head.appendChild(slideOutStyle);
    }
  }
});

// Listen for messages from the extension
chrome.runtime.onMessage?.addListener((request, sender, sendResponse) => {
  if (request.action === "insertSummary") {
    window.postMessage({
      type: "INSERT_SUMMARY",
      summary: request.summary
    }, "*");
    sendResponse({success: true});
  }
});