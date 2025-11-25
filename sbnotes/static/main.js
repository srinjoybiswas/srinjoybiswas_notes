/* ==========================================================
   SB NOTES – MAIN JS
   Common frontend logic for the entire website
   ========================================================== */


/* ----------------------------------------------------------
   1. Disable Right Click Everywhere
-----------------------------------------------------------*/
document.addEventListener("contextmenu", function (e) {
    e.preventDefault();
    console.warn("Right-click disabled on SB Notes.");
});


/* ----------------------------------------------------------
   2. Disable Text Copy / Cut / Paste
-----------------------------------------------------------*/
document.addEventListener("copy", function (e) {
    e.preventDefault();
    alert("Copying is disabled on SB Notes.");
});

document.addEventListener("cut", function (e) {
    e.preventDefault();
    alert("Cut operation is disabled.");
});

document.addEventListener("paste", function (e) {
    e.preventDefault();
    alert("Pasting is disabled.");
});


/* ----------------------------------------------------------
   3. Disable Print / Save / Screenshot Shortcuts
-----------------------------------------------------------*/
document.addEventListener("keydown", function (e) {

    // PrintScreen
    if (e.key === "PrintScreen") {
        alert("Screenshots are disabled.");
        return false;
    }

    // Ctrl+P = Print
    if (e.ctrlKey && (e.key === 'p' || e.key === 'P')) {
        alert("Printing is disabled.");
        e.preventDefault();
        return false;
    }

    // Ctrl+S = Save page
    if (e.ctrlKey && (e.key === 's' || e.key === 'S')) {
        alert("Saving this page is disabled.");
        e.preventDefault();
        return false;
    }

    // Ctrl+C = Copy
    if (e.ctrlKey && (e.key === 'c' || e.key === 'C')) {
        alert("Copying is disabled.");
        e.preventDefault();
        return false;
    }

    // Ctrl+Shift+I = Inspect Element
    if (e.ctrlKey && e.shiftKey && e.key === 'I') {
        alert("Developer tools disabled.");
        e.preventDefault();
        return false;
    }

    // Ctrl+Shift+J = Console
    if (e.ctrlKey && e.shiftKey && e.key === 'J') {
        alert("Console access disabled.");
        e.preventDefault();
        return false;
    }
});


/* ----------------------------------------------------------
   4. LIVE CLOCK (Will be used if element exists)
-----------------------------------------------------------*/
function updateLiveClock() {
    const timeBox = document.getElementById("currentTime");
    if (timeBox) {
        const now = new Date();
        timeBox.innerText = now.toLocaleTimeString();
    }
}

setInterval(updateLiveClock, 1000);
updateLiveClock();


/* ----------------------------------------------------------
   5. Scroll Progress Bar (auto detects if element exists)
-----------------------------------------------------------*/
const readerContainer = document.getElementById("readerContainer");
const progressBar = document.getElementById("scrollProgress");

if (readerContainer && progressBar) {
    readerContainer.addEventListener("scroll", () => {
        let scrollTop = readerContainer.scrollTop;
        let scrollHeight = readerContainer.scrollHeight - readerContainer.clientHeight;
        let progress = (scrollTop / scrollHeight) * 100;
        progressBar.style.width = progress + "%";
    });
}


/* ----------------------------------------------------------
   6. Block Dragging of Images/PDF
-----------------------------------------------------------*/
document.addEventListener("dragstart", function (e) {
    e.preventDefault();
});


/* ----------------------------------------------------------
   7. Block selecting text globally
-----------------------------------------------------------*/
document.addEventListener("selectstart", function (e) {
    e.preventDefault();
});


/* ----------------------------------------------------------
   8. Hide Content if DevTools Is Open (Hardening)
-----------------------------------------------------------
(function detectDevTools() {
    let threshold = 160;

    setInterval(() => {
        let widthDiff = window.outerWidth - window.innerWidth;
        let heightDiff = window.outerHeight - window.innerHeight;

        if (widthDiff > threshold || heightDiff > threshold) {
            document.body.innerHTML = `
              <div style="display:flex;justify-content:center;align-items:center;
                          height:100vh;font-size:24px;font-weight:bold;">
                Developer tools are blocked on SB Notes.
              </div>`;
        }
    }, 1000);
})();
*/