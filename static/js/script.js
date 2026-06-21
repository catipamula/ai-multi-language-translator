const $ = (selector) => document.querySelector(selector);

const state = {
    lastHistory: null,
    debounceTimer: null,
    conversationMode: false,
    typingToken: 0,
};

document.addEventListener("DOMContentLoaded", () => {
    hydrateTheme();
    bindTranslator();
});

function bindTranslator() {
    const input = $("#inputText");
    if (!input) {
        return;
    }

    $("#translateButton")?.addEventListener("click", () => translateNow());
    $("#swapLanguages")?.addEventListener("click", swapLanguages);
    $("#copyButton")?.addEventListener("click", copyTranslation);
    $("#clearButton")?.addEventListener("click", clearTranslator);
    $("#speakButton")?.addEventListener("click", speakOutput);
    $("#micButton")?.addEventListener("click", speechToText);
    $("#conversationButton")?.addEventListener("click", toggleConversation);

    input.addEventListener("input", () => {
        $("#charCount").textContent = `${input.value.length} / 5000`;
        window.clearTimeout(state.debounceTimer);
        if (input.value.trim().length < 2) {
            return;
        }
        state.debounceTimer = window.setTimeout(() => translateNow(true), 500);
    });

    $("#sourceLanguage")?.addEventListener("change", () => translateNow(true));
    $("#targetLanguage")?.addEventListener("change", () => translateNow(true));
}

function hydrateTheme() {
    const theme = localStorage.getItem("translator-theme");
    if (theme === "dark") {
        document.body.classList.add("dark");
        $("#themeToggle i")?.classList.replace("fa-moon", "fa-sun");
    }
    $("#themeToggle")?.addEventListener("click", toggleTheme);
}

function toggleTheme() {
    document.body.classList.toggle("dark");
    const isDark = document.body.classList.contains("dark");
    localStorage.setItem("translator-theme", isDark ? "dark" : "light");
    const icon = $("#themeToggle i");
    if (icon) {
        icon.className = isDark ? "fa-solid fa-sun" : "fa-solid fa-moon";
    }
}

async function translateNow(isRealtime = false) {
    const input = $("#inputText");
    const sourceLanguage = $("#sourceLanguage");
    const targetLanguage = $("#targetLanguage");
    const output = $("#outputText");

    if (!input || !sourceLanguage || !targetLanguage || !output) {
        console.error("Translator UI is missing required elements.");
        showToast("Translator UI is not fully loaded.", "danger");
        return;
    }

    const text = input.value.trim();
    if (!text) {
        if (!isRealtime) {
            showToast("Enter text to translate.", "warning");
        }
        return;
    }

    setLoading(true);
    try {
        console.info("Sending translation request", {
            source_language: sourceLanguage.value,
            target_language: targetLanguage.value,
            text_length: text.length,
        });
        const data = await postJson("/translate", {
            text,
            source_language: sourceLanguage.value,
            target_language: targetLanguage.value,
        });
        if (!data.success) {
            throw new Error(data.error || "Translation failed.");
        }
        if (!data.translation) {
            throw new Error("Translation response did not include output text.");
        }
        state.lastHistory = data.history;
        $("#detectedLabel").innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> Detected ${data.detected_label}`;
        await typeInto(output, data.translation);
        $("#translationEngine").textContent = "Translated";
        await refreshHistory();
        if (!isRealtime) {
            showToast("Translation successful.");
        }
    } catch (error) {
        console.error("Translation failed", error);
        showToast(error.message, "danger");
    } finally {
        setLoading(false);
    }
}

function setLoading(isLoading) {
    $("#loadingLayer")?.classList.toggle("show", isLoading);
    const button = $("#translateButton");
    if (button) {
        button.disabled = isLoading;
    }
}

async function typeInto(element, text) {
    const token = ++state.typingToken;
    element.value = "";
    const step = Math.max(1, Math.ceil(text.length / 90));
    for (let index = 0; index < text.length; index += step) {
        if (token !== state.typingToken) {
            return;
        }
        element.value = text.slice(0, index + step);
        await wait(9);
    }
    element.value = text;
}

function wait(ms) {
    return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function swapLanguages() {
    const source = $("#sourceLanguage");
    const target = $("#targetLanguage");
    if (source.value === "auto") {
        source.value = target.value;
        target.value = "en";
    } else {
        [source.value, target.value] = [target.value, source.value];
    }
    [$("#inputText").value, $("#outputText").value] = [$("#outputText").value, $("#inputText").value];
    $("#charCount").textContent = `${$("#inputText").value.length} / 5000`;
}

async function copyTranslation() {
    const text = $("#outputText")?.value.trim();
    if (!text) {
        showToast("Nothing to copy.", "warning");
        return;
    }
    await navigator.clipboard.writeText(text);
    showToast("Copied to clipboard.");
}

function clearTranslator() {
    $("#inputText").value = "";
    $("#outputText").value = "";
    $("#charCount").textContent = "0 / 5000";
    $("#detectedLabel").innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Auto detection ready';
    state.lastHistory = null;
}

async function speechToText() {
    showToast("Listening from your microphone...");
    try {
        const data = await postJson("/speech-to-text", {
            language: $("#sourceLanguage").value,
        });
        if (!data.success) {
            throw new Error(data.error || "Speech recognition failed.");
        }
        $("#inputText").value = data.text;
        $("#charCount").textContent = `${data.text.length} / 5000`;
        await translateNow();
        if (state.conversationMode) {
            await speakOutput();
            window.setTimeout(() => speechToText(), 600);
        }
    } catch (error) {
        showToast(error.message, "danger");
        state.conversationMode = false;
        $("#conversationStrip")?.classList.remove("active");
    }
}

function toggleConversation() {
    state.conversationMode = !state.conversationMode;
    $("#conversationStrip")?.classList.toggle("active", state.conversationMode);
    showToast(state.conversationMode ? "Conversation mode started." : "Conversation mode stopped.");
    if (state.conversationMode) {
        speechToText();
    }
}

async function speakOutput() {
    const text = $("#outputText")?.value.trim();
    if (!text) {
        showToast("Nothing to speak.", "warning");
        return;
    }
    try {
        const data = await postJson("/text-to-speech", {
            text,
            language: $("#targetLanguage").value,
            voice: $("#voiceSelect").value,
        });
        if (!data.success) {
            throw new Error(data.error || "Speech output failed.");
        }
        const audio = new Audio(`data:${data.mime_type};base64,${data.audio}`);
        await audio.play();
        showToast(`Speaking with ${data.engine}.`);
    } catch (error) {
        showToast(error.message, "danger");
    }
}

async function refreshHistory() {
    const container = $("#historyList");
    if (!container) {
        return;
    }
    try {
        const data = await fetchJson("/history-data");
        container.innerHTML = data.history.slice(0, 8).map((item) => `
            <article class="mini-card">
                <strong>${escapeHtml(item.original_text)}</strong>
                <span>${escapeHtml(item.translated_text)}</span>
                <small>${escapeHtml(item.created_at)}</small>
            </article>
        `).join("") || '<p class="empty-state">No translations yet.</p>';
    } catch (error) {
        showToast(error.message, "danger");
    }
}

async function postJson(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });
    const data = await parseJsonResponse(response);
    if (!response.ok) {
        throw new Error(data.error || "Request failed.");
    }
    return data;
}

async function fetchJson(url) {
    const response = await fetch(url);
    const data = await parseJsonResponse(response);
    if (!response.ok) {
        throw new Error(data.error || "Request failed.");
    }
    return data;
}

async function parseJsonResponse(response) {
    try {
        return await response.json();
    } catch (error) {
        console.error("Expected JSON response but received something else.", error);
        return {
            success: false,
            error: `Server returned ${response.status} without valid JSON.`,
        };
    }
}

function showToast(message, type = "success") {
    const container = $("#toastContainer");
    if (!container) {
        return;
    }
    const icon = type === "danger" ? "triangle-exclamation" : type === "warning" ? "circle-info" : "circle-check";
    const toast = document.createElement("div");
    toast.className = "toast align-items-center border-0 show";
    toast.role = "alert";
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fa-solid fa-${icon} me-2"></i>${escapeHtml(message)}
            </div>
            <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    container.appendChild(toast);
    window.setTimeout(() => toast.remove(), 3600);
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
