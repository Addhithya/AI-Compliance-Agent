console.log("⚙️ Gmail Compliance Checker Active");

function attachListenerToComposer(composer) {
  if (!composer || composer.__complianceAttached) return;

  composer.__complianceAttached = true;
  console.log("✅ Composer detected. Attaching listeners...");

  let lastText = "";

  function debounce(func, delay) {
    let timeout;
    return function(...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), delay);
    };
  }

  const handler = debounce(async () => {
    const text = composer.innerText.trim();

    if (!text || text === lastText) return;
      lastText = text; 
      console.log("📨 User stopped typing. Checking compliance...");

      try {
        const response = await fetch('http://127.0.0.1:8000/assess', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text })
        });

        const result = await response.json();
        console.log("🛡️ API result:", result);

        if (result.compliant === "No") {
          // alert("⚠️ Compliance Alert: " + result.reason);
          showPopup(result.reason || "⚠️ Non-compliant content detected.");
        }
      } catch (err) {
        console.error("❌ Error calling compliance API:", err);
      }
  }, 1000);

  // const handler = () => {
    // const text = composer.innerText.trim();

    // if (!text || text === lastText) return;

    // clearTimeout(debounceTimer);

    // debounceTimer = setTimeout(async () => {
    //   lastText = text;  // Store last sent text
    //   console.log("📨 User stopped typing. Checking compliance...");

    //   try {
    //     const response = await fetch('http://127.0.0.1:8000/assess', {
    //       method: 'POST',
    //       headers: { 'Content-Type': 'application/json' },
    //       body: JSON.stringify({ text })
    //     });

    //     const result = await response.json();
    //     console.log("🛡️ API result:", result);

    //     if (result.compliant === "No") {
    //       // alert("⚠️ Compliance Alert: " + result.reason);
    //       showPopup(result.reason || "⚠️ Non-compliant content detected.");
    //     }
    //   } catch (err) {
    //     console.error("❌ Error calling compliance API:", err);
    //   }
  //   }, 2000); // 2 sec
  // };

  composer.addEventListener("input", handler);
  composer.addEventListener("keyup", handler);
}

let popupVisible = false;

// Tooltip UI
function showPopup(message) {
  if (popupVisible) return; // Prevent multiple popups

  popupVisible = true;

  const popup = document.createElement('div');
  popup.id = 'compliance-popup';
  popup.style.position = 'fixed';
  popup.style.top = '50%';
  popup.style.left = '50%';
  popup.style.transform = 'translate(-50%, -50%)';
  popup.style.background = '#ff4d4d';
  popup.style.color = '#fff';
  popup.style.padding = '20px';
  popup.style.borderRadius = '12px';
  popup.style.zIndex = '99999';
  popup.style.boxShadow = '0 0 10px rgba(0,0,0,0.3)';
  popup.style.fontSize = '16px';
  popup.innerText = message;

  document.body.appendChild(popup);

  setTimeout(() => {
    popup.remove();
    popupVisible = false; // Reset the flag when popup disappears
  }, 5000);
}



// MutationObserver to detect Gmail compose box
const observer = new MutationObserver(mutations => {
  for (const mutation of mutations) {
    for (const node of mutation.addedNodes) {
      if (node.nodeType === 1 && node.querySelectorAll) {
        const editor = node.querySelector('div[contenteditable="true"]');
        if (editor && editor.getAttribute("aria-label") === "Message Body") {
          attachListenerToComposer(editor);
        }
      }
    }
  }
});

observer.observe(document.body, { childList: true, subtree: true });
