(function () {
  const STORAGE_KEY = "preferredLanguage";
  const DEFAULT_LANG = "en";
  const zhCharRegex = /[\p{Script=Han}\u{3000}-\u{303F}\u{FF00}-\u{FFEF}]/u;
  const enCharRegex = /[A-Za-z]/;
  const SKIP_TAGS = new Set([
    "SCRIPT",
    "STYLE",
    "NOSCRIPT",
    "CODE",
    "PRE",
    "TEXTAREA",
    "OPTION",
    "SVG",
    "MATH",
  ]);

  function injectStyles() {
    if (document.getElementById("language-toggle-style")) return;

    const style = document.createElement("style");
    style.id = "language-toggle-style";
    style.textContent = `
:root[data-lang="en"] .lang-zh { display: none !important; }
:root[data-lang="zh"] .lang-en { display: none !important; }
.lang-fragment { display: inline; }
.language-switcher {
  position: fixed;
  top: 16px;
  right: 24px;
  display: inline-flex;
  gap: 0.5rem;
  padding: 0.4rem 0.6rem;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(6px);
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.18);
  z-index: 1000;
  font-size: 0.9rem;
}
.language-switcher button {
  border: none;
  background: transparent;
  color: #f8fafc;
  cursor: pointer;
  padding: 0.25rem 0.8rem;
  border-radius: 999px;
  transition: background 0.2s ease, color 0.2s ease, transform 0.2s ease;
  font-weight: 600;
}
.language-switcher button:hover {
  transform: translateY(-1px);
}
.language-switcher button.active {
  background: rgba(248, 250, 252, 0.92);
  color: #0f172a;
}
.language-switcher button:focus-visible {
  outline: 2px solid rgba(248, 250, 252, 0.85);
  outline-offset: 2px;
}
@media (prefers-color-scheme: light) {
  .language-switcher {
    background: rgba(248, 250, 252, 0.85);
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.12);
  }
  .language-switcher button {
    color: #1f2937;
  }
  .language-switcher button.active {
    background: #2563eb;
    color: #ffffff;
  }
  .language-switcher button:focus-visible {
    outline: 2px solid rgba(37, 99, 235, 0.8);
  }
}
`;
    document.head.appendChild(style);
  }

  function shouldIgnore(textNode) {
    const parent = textNode.parentElement;
    if (!parent) return false;
    if (parent.closest("[data-i18n-ignore]")) return true;
    if (SKIP_TAGS.has(parent.tagName)) return true;
    return false;
  }

  function createSpan(content, lang) {
    const span = document.createElement("span");
    span.className = `lang-fragment ${lang}`;
    span.textContent = content;
    return span;
  }

  function splitMixedText(textNode) {
    const text = textNode.textContent;
    const parts = text.split(/([\p{Script=Han}\u{3000}-\u{303F}\u{FF00}-\u{FFEF}]+)/u);
    const fragment = document.createDocumentFragment();

    for (const part of parts) {
      if (!part) continue;
      const hasZh = zhCharRegex.test(part);
      const hasEn = enCharRegex.test(part);

      if (!hasZh && !hasEn) {
        fragment.appendChild(document.createTextNode(part));
        continue;
      }

      if (hasZh && !hasEn) {
        fragment.appendChild(createSpan(part, "lang-zh"));
      } else if (hasEn && !hasZh) {
        fragment.appendChild(createSpan(part, "lang-en"));
      } else {
        fragment.appendChild(createSpan(part, "lang-neutral"));
      }
    }

    textNode.replaceWith(fragment);
  }

  function wrapSingleLanguage(textNode, lang) {
    const span = createSpan(textNode.textContent, lang);
    textNode.replaceWith(span);
  }

  function prepareLanguageFragments(root) {
    if (root.dataset.i18nPrepared === "true") return;

    const walker = document.createTreeWalker(
      root,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode(textNode) {
          if (!textNode.textContent || !textNode.textContent.trim()) {
            return NodeFilter.FILTER_REJECT;
          }
          if (shouldIgnore(textNode)) return NodeFilter.FILTER_REJECT;
          return NodeFilter.FILTER_ACCEPT;
        },
      },
    );

    const nodes = [];
    while (walker.nextNode()) {
      nodes.push(walker.currentNode);
    }

    nodes.forEach((textNode) => {
      const text = textNode.textContent;
      const hasZh = zhCharRegex.test(text);
      const hasEn = enCharRegex.test(text);

      if (hasZh && hasEn) {
        splitMixedText(textNode);
      } else if (hasZh) {
        wrapSingleLanguage(textNode, "lang-zh");
      } else if (hasEn) {
        wrapSingleLanguage(textNode, "lang-en");
      }
    });

    root.dataset.i18nPrepared = "true";
  }

  function updateToggleButtons(lang) {
    document.querySelectorAll(".language-switcher [data-lang]").forEach((btn) => {
      const isActive = btn.dataset.lang === lang;
      btn.classList.toggle("active", isActive);
      btn.setAttribute("aria-pressed", String(isActive));
    });
  }

  function applyLanguage(lang, persist = true) {
    const normalised = lang === "zh" ? "zh" : "en";
    document.documentElement.dataset.lang = normalised;
    document.documentElement.setAttribute("lang", normalised);

    if (persist) {
      try {
        localStorage.setItem(STORAGE_KEY, normalised);
      } catch (error) {
        console.warn("Language preference could not be stored:", error);
      }
    }

    updateToggleButtons(normalised);
  }

  function setupToggle() {
    let switcher = document.querySelector(".language-switcher");

    if (!switcher) {
      switcher = document.createElement("div");
      switcher.className = "language-switcher";
      switcher.setAttribute("data-i18n-ignore", "true");
      switcher.innerHTML = `
        <button type="button" data-lang="en">English</button>
        <button type="button" data-lang="zh">中文</button>
      `;
      document.body.appendChild(switcher);
    }

    switcher.addEventListener("click", (event) => {
      const button = event.target.closest("[data-lang]");
      if (!button) return;
      applyLanguage(button.dataset.lang);
    });
  }

  function init() {
    injectStyles();
    prepareLanguageFragments(document.body);
    setupToggle();

    let stored = null;
    try {
      stored = localStorage.getItem(STORAGE_KEY);
    } catch (error) {
      console.warn("Language preference could not be read:", error);
    }

    applyLanguage(stored === "zh" ? "zh" : DEFAULT_LANG, false);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
