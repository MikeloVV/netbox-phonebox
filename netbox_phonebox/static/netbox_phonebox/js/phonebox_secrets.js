(function () {
    "use strict";

    const API_BASE = "/api/plugins/secrets/secrets/";

    /**
     * Fetch decrypted secret value via API
     */
    async function fetchSecretPlaintext(secretId) {
        const response = await fetch(`${API_BASE}${secretId}/`, {
            method: "GET",
            headers: {
                "Accept": "application/json",
                "X-CSRFToken": getCSRFToken(),
            },
            credentials: "same-origin",
        });

        if (!response.ok) {
            if (response.status === 403) {
                throw new Error("Permission denied. Check your session key.");
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        return data.plaintext || null;
    }

    /**
     * Get CSRF token from cookie
     */
    function getCSRFToken() {
        const name = "csrftoken";
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                return cookie.substring(name.length + 1);
            }
        }
        return "";
    }

    /**
     * Toggle single secret visibility
     */
    async function toggleSecret(row) {
        const secretId = row.dataset.secretId;
        const placeholder = row.querySelector(".phonebox-secret-placeholder");
        const plaintext = row.querySelector(".phonebox-secret-plaintext");
        const textEl = row.querySelector(".phonebox-secret-text");
        const toggleBtn = row.querySelector(".phonebox-toggle-secret");
        const icon = toggleBtn.querySelector("i");

        // If already visible — hide
        if (plaintext.style.display !== "none") {
            plaintext.style.display = "none";
            placeholder.style.display = "";
            icon.className = "mdi mdi-lock-open-variant";
            toggleBtn.title = "Unlock";
            toggleBtn.classList.remove("btn-ghost-danger");
            toggleBtn.classList.add("btn-ghost-success");
            return;
        }

        // Fetch and show
        try {
            toggleBtn.disabled = true;
            icon.className = "mdi mdi-loading mdi-spin";

            const value = await fetchSecretPlaintext(secretId);

            if (value !== null) {
                textEl.textContent = value;
                placeholder.style.display = "none";
                plaintext.style.display = "";
                icon.className = "mdi mdi-lock";
                toggleBtn.title = "Lock";
                toggleBtn.classList.remove("btn-ghost-success");
                toggleBtn.classList.add("btn-ghost-danger");
            } else {
                textEl.textContent = "(empty)";
                placeholder.style.display = "none";
                plaintext.style.display = "";
                icon.className = "mdi mdi-lock";
                toggleBtn.title = "Lock";
            }
        } catch (err) {
            console.error("Failed to fetch secret:", err);
            alert(err.message || "Failed to decrypt secret. Is your session key active?");
            icon.className = "mdi mdi-lock-open-variant";
        } finally {
            toggleBtn.disabled = false;
        }
    }

    /**
     * Copy secret value to clipboard
     */
    async function copySecret(btn) {
        const textEl = btn.closest(".phonebox-secret-plaintext").querySelector(".phonebox-secret-text");
        const value = textEl.textContent;

        try {
            await navigator.clipboard.writeText(value);

            // Visual feedback
            const icon = btn.querySelector("i");
            const origClass = icon.className;
            icon.className = "mdi mdi-check";
            btn.classList.add("btn-ghost-success");

            setTimeout(() => {
                icon.className = origClass;
                btn.classList.remove("btn-ghost-success");
            }, 1500);
        } catch (err) {
            console.error("Failed to copy:", err);
        }
    }

    /**
     * Unlock all secrets
     */
    async function unlockAll() {
        const rows = document.querySelectorAll(".phonebox-secrets-table tr[data-secret-id]");
        for (const row of rows) {
            const plaintext = row.querySelector(".phonebox-secret-plaintext");
            if (plaintext.style.display === "none") {
                await toggleSecret(row);
            }
        }

        // Toggle buttons
        document.querySelectorAll(".phonebox-unlock-all").forEach(b => b.style.display = "none");
        document.querySelectorAll(".phonebox-lock-all").forEach(b => b.style.display = "");
    }

    /**
     * Lock all secrets
     */
    function lockAll() {
        const rows = document.querySelectorAll(".phonebox-secrets-table tr[data-secret-id]");
        for (const row of rows) {
            const plaintext = row.querySelector(".phonebox-secret-plaintext");
            const placeholder = row.querySelector(".phonebox-secret-placeholder");
            const textEl = row.querySelector(".phonebox-secret-text");
            const toggleBtn = row.querySelector(".phonebox-toggle-secret");
            const icon = toggleBtn.querySelector("i");

            plaintext.style.display = "none";
            placeholder.style.display = "";
            textEl.textContent = "";
            icon.className = "mdi mdi-lock-open-variant";
            toggleBtn.title = "Unlock";
            toggleBtn.classList.remove("btn-ghost-danger");
            toggleBtn.classList.add("btn-ghost-success");
        }

        // Toggle buttons
        document.querySelectorAll(".phonebox-unlock-all").forEach(b => b.style.display = "");
        document.querySelectorAll(".phonebox-lock-all").forEach(b => b.style.display = "none");
    }

    /**
     * Initialize event listeners
     */
    function init() {
        // Toggle individual secrets
        document.querySelectorAll(".phonebox-toggle-secret").forEach(btn => {
            btn.addEventListener("click", function (e) {
                e.preventDefault();
                const row = this.closest("tr[data-secret-id]");
                toggleSecret(row);
            });
        });

        // Copy buttons
        document.querySelectorAll(".phonebox-copy-secret").forEach(btn => {
            btn.addEventListener("click", function (e) {
                e.preventDefault();
                copySecret(this);
            });
        });

        // Unlock all
        document.querySelectorAll(".phonebox-unlock-all").forEach(btn => {
            btn.addEventListener("click", function (e) {
                e.preventDefault();
                unlockAll();
            });
        });

        // Lock all
        document.querySelectorAll(".phonebox-lock-all").forEach(btn => {
            btn.addEventListener("click", function (e) {
                e.preventDefault();
                lockAll();
            });
        });
    }

    // Run when DOM ready
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();