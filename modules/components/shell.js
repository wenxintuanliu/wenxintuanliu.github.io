const NAV_ITEMS = [
  ["home", "首页", "index.html"],
  ["projects", "项目", "pages/projects.html"],
  ["methods", "方法", "pages/methods.html"],
  ["knowledge", "索引", "pages/knowledge.html"],
  ["about", "关于", "pages/about.html"],
];

export function renderShell(registry, content, currentPage = "home") {
  const root = document.createElement("div");
  root.className = "site";
  const activePage = inferActivePage(currentPage);
  root.innerHTML = `
    <header class="topbar" id="topbar">
      <a class="brand" href="${sitePath("index.html")}" aria-label="回到首页">
        <img class="brand-icon" src="${sitePath("assets/profile.png")}" alt="" aria-hidden="true">
        <span>${escapeHtml(registry.siteTitle)}</span>
      </a>
      <nav class="nav-links" id="nav-links" aria-label="站点导航">
        ${NAV_ITEMS.map(([page, label, href]) => navLink(page, label, href, activePage)).join("")}
      </nav>
      <div style="display:flex;align-items:center">
        <button class="theme-toggle" id="theme-toggle" aria-label="切换深色模式" type="button">
          ${sunIcon()}
        </button>
        <button class="mobile-toggle" id="mobile-toggle" aria-label="打开导航菜单" type="button">
          ${menuIcon()}
        </button>
      </div>
    </header>
  `;
  root.append(content);
  if (activePage !== "home") {
    root.append(createSiteFooter(registry));
  }
  root.append(createScrollTop());

  requestAnimationFrame(() => {
    initThemeToggle();
    initMobileNav();
    initScrollEffects();
    initLightbox();
    initExplorables();
    initComparePanels();
    initLazyImages();
    initCodeCopy();
    initArchiveSearch();
    typesetMath();
  });

  return root;
}

function createScrollTop() {
  const btn = document.createElement("button");
  btn.className = "scroll-top";
  btn.id = "scroll-top";
  btn.setAttribute("aria-label", "回到顶部");
  btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 15l-6-6-6 6"/></svg>`;
  return btn;
}

function createSiteFooter(registry) {
  const footer = document.createElement("footer");
  footer.className = "site-footer";
  footer.innerHTML = `
    <span class="footer-left">All rights reserved.<a class="secret-entry" href="${sitePath("pages/method.html?id=markdown-style-gallery")}" aria-label="Markdown 样式示例隐藏入口"><img src="${sitePath("assets/secret-entry.png")}" alt=""></a></span>
    <span>Created by <a href="${escapeHtml(registry.author?.github ?? "https://github.com/wenxintuanliu/")}" target="_blank" rel="noreferrer">Chunfeng Fusu ${githubIcon()}</a></span>
  `;
  return footer;
}

function initThemeToggle() {
  const toggle = document.getElementById("theme-toggle");
  if (!toggle) return;

  const saved = localStorage.getItem("theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const theme = ["light", "dark", "vivid"].includes(saved) ? saved : (prefersDark ? "dark" : "light");
  applyTheme(theme);

  toggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    const next = current === "light" ? "dark" : current === "dark" ? "vivid" : "light";
    applyTheme(next);
    localStorage.setItem("theme", next);
  });
}

function applyTheme(theme) {
  document.documentElement.classList.add("theme-changing");
  document.documentElement.setAttribute("data-theme", theme);
  const toggle = document.getElementById("theme-toggle");
  if (toggle) {
    const labels = {
      light: "当前为白天主题，点击切换到黑夜主题",
      dark: "当前为黑夜主题，点击切换到清新主题",
      vivid: "当前为清新主题，点击切换到白天主题",
    };
    toggle.setAttribute("aria-label", labels[theme] ?? labels.light);
    toggle.title = labels[theme] ?? labels.light;
    toggle.innerHTML = theme === "dark" ? paletteIcon() : theme === "vivid" ? sunIcon() : moonIcon();
  }
  window.setTimeout(() => document.documentElement.classList.remove("theme-changing"), 80);
}

function initMobileNav() {
  const toggle = document.getElementById("mobile-toggle");
  const nav = document.getElementById("nav-links");
  if (!toggle || !nav) return;

  toggle.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", String(open));
    toggle.innerHTML = open ? closeIcon() : menuIcon();
  });

  nav.addEventListener("click", (e) => {
    if (e.target.tagName === "A") {
      nav.classList.remove("is-open");
      toggle.innerHTML = menuIcon();
    }
  });
}

function initScrollEffects() {
  const topbar = document.getElementById("topbar");
  const scrollBtn = document.getElementById("scroll-top");

  const onScroll = () => {
    const y = window.scrollY;
    if (topbar) topbar.classList.toggle("scrolled", y > 20);
    if (scrollBtn) scrollBtn.classList.toggle("visible", y > 400);
  };

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  if (scrollBtn) {
    scrollBtn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
}

function initLightbox() {
  document.addEventListener("click", (e) => {
    const figure = e.target.closest(".evidence-figure, .mesh-figure");
    if (!figure) return;

    const img = figure.querySelector("img");
    if (!img) return;

    const caption = figure.querySelector("figcaption")?.textContent || "";
    openLightbox(img.src, img.alt, caption);
  });
}

function initExplorables() {
  document.querySelectorAll("[data-time-scrubber]").forEach((panel) => {
    const data = readPanelData(panel);
    const input = panel.querySelector("input[type='range']");
    const img = panel.querySelector("img");
    const output = panel.querySelector("output");
    const caption = panel.querySelector("figcaption");
    if (!data.length || !input || !img || !output) return;

    input.addEventListener("input", () => {
      const item = data[Number(input.value)] ?? data[0];
      img.src = item.src;
      img.alt = item.title;
      output.textContent = item.title;
      if (caption) caption.textContent = item.label;
    });
  });

  document.querySelectorAll("[data-image-switcher]").forEach((panel) => {
    const data = readPanelData(panel);
    const img = panel.querySelector("img");
    const caption = panel.querySelector("figcaption");
    const buttons = [...panel.querySelectorAll("button[data-index]")];
    if (!data.length || !img || !buttons.length) return;

    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        const item = data[Number(button.dataset.index)] ?? data[0];
        img.src = item.src;
        img.alt = item.title;
        if (caption) caption.textContent = item.label;
        buttons.forEach((entry) => entry.classList.toggle("is-active", entry === button));
      });
    });
  });
}

function initComparePanels() {
  document.querySelectorAll("[data-compare-panel]").forEach((panel) => {
    const range = panel.querySelector("input[type='range']");
    const topImage = panel.querySelector(".compare-top");
    if (!range || !topImage) return;
    const update = () => {
      topImage.style.clipPath = `inset(0 ${100 - Number(range.value)}% 0 0)`;
    };
    range.addEventListener("input", update);
    update();
  });
}

function initLazyImages() {
  const images = [...document.querySelectorAll("img[data-lazy-src]")];
  if (!images.length) return;

  const load = (img) => {
    if (!img.dataset.lazySrc) return;
    img.src = img.dataset.lazySrc;
    img.removeAttribute("data-lazy-src");
  };

  if (!("IntersectionObserver" in window)) {
    images.forEach(load);
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      load(entry.target);
      observer.unobserve(entry.target);
    });
  }, { rootMargin: "180px" });

  images.forEach((img) => observer.observe(img));
}

function initCodeCopy() {
  document.querySelectorAll("[data-copy-code]").forEach((button) => {
    button.addEventListener("click", async () => {
      const block = button.closest(".md-codeblock");
      const text = block?.querySelector("code")?.textContent ?? "";
      if (!text) return;
      try {
        await navigator.clipboard.writeText(text);
        button.textContent = "Copied";
        setTimeout(() => {
          button.textContent = "Copy";
        }, 1200);
      } catch {
        button.textContent = "Select";
      }
    });
  });
}

function initArchiveSearch() {
  const input = document.querySelector("[data-archive-search]");
  if (!input) return;
  const cards = [...document.querySelectorAll("[data-search-text]")];
  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase();
    cards.forEach((card) => {
      card.hidden = query ? !card.dataset.searchText.includes(query) : false;
    });
  });
}

function typesetMath() {
  if (!document.querySelector(".md-math, .md-inline-math")) return;
  loadMathJax().then(() => window.MathJax?.typesetPromise?.()).catch(() => {});
}

let mathJaxPromise = null;

function loadMathJax() {
  if (window.MathJax?.typesetPromise) return Promise.resolve();
  if (mathJaxPromise) return mathJaxPromise;

  window.MathJax = {
    tex: {
      inlineMath: [["\\(", "\\)"]],
      displayMath: [["\\[", "\\]"]],
      processEscapes: true,
    },
    svg: { fontCache: "global" },
    options: { skipHtmlTags: ["script", "noscript", "style", "textarea", "pre", "code"] },
  };

  mathJaxPromise = new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js";
    script.async = true;
    script.onload = resolve;
    script.onerror = reject;
    document.head.append(script);
  });
  return mathJaxPromise;
}

function readPanelData(panel) {
  try {
    return JSON.parse(panel.querySelector('script[type="application/json"]')?.textContent ?? "[]");
  } catch {
    return [];
  }
}

function openLightbox(src, alt, caption) {
  const overlay = document.createElement("div");
  overlay.className = "lightbox";
  overlay.setAttribute("role", "dialog");
  overlay.setAttribute("aria-modal", "true");
  overlay.setAttribute("aria-label", caption || alt || "image preview");
  overlay.innerHTML = `
    <img src="${escapeHtml(src)}" alt="${escapeHtml(alt)}">
    ${caption ? `<div class="lightbox-caption">${escapeHtml(caption)}</div>` : ""}
  `;

  document.body.append(overlay);
  requestAnimationFrame(() => overlay.classList.add("active"));

  const close = () => {
    overlay.classList.remove("active");
    setTimeout(() => overlay.remove(), 250);
  };

  overlay.addEventListener("click", close);
  document.addEventListener("keydown", function handler(e) {
    if (e.key === "Escape") {
      close();
      document.removeEventListener("keydown", handler);
    }
  });
}

function inferActivePage(currentPage) {
  const path = window.location.pathname;
  if (path.endsWith("/pages/project.html")) return "projects";
  if (path.endsWith("/pages/methods.html") || path.endsWith("/pages/method.html")) return "methods";
  if (path.endsWith("/pages/knowledge.html")) return "knowledge";
  return currentPage;
}

function navLink(page, label, href, currentPage) {
  const active = page === currentPage;
  return `<a href="${sitePath(href)}"${active ? ' class="is-active" aria-current="page"' : ""}>${label}</a>`;
}

function sitePath(path) {
  if (!path || /^(?:[a-z]+:|#|\/)/i.test(path)) return path;
  return `${siteRoot()}${path}`;
}

function siteRoot() {
  return window.location.pathname.includes("/pages/") ? "../" : "";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function sunIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>`;
}

function moonIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
}

function paletteIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3a9 9 0 0 0 0 18h1.5a2 2 0 0 0 1.43-3.4 1.1 1.1 0 0 1 .77-1.88H17a4 4 0 0 0 0-8h-1.2A4.8 4.8 0 0 0 12 3Z"/><circle cx="7.5" cy="10" r=".7"/><circle cx="10.5" cy="7.5" r=".7"/><circle cx="14" cy="8" r=".7"/></svg>`;
}

function githubIcon() {
  return `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12 2C6.48 2 2 6.59 2 12.25c0 4.53 2.87 8.37 6.84 9.73.5.1.68-.22.68-.49v-1.9c-2.78.62-3.37-1.22-3.37-1.22-.45-1.19-1.11-1.5-1.11-1.5-.91-.64.07-.63.07-.63 1 .07 1.53 1.06 1.53 1.06.9 1.57 2.35 1.12 2.92.86.09-.67.35-1.12.63-1.38-2.22-.26-4.56-1.14-4.56-5.07 0-1.12.39-2.04 1.03-2.76-.1-.26-.45-1.31.1-2.72 0 0 .84-.28 2.75 1.05A9.27 9.27 0 0 1 12 6.93c.85 0 1.7.12 2.5.35 1.9-1.33 2.74-1.05 2.74-1.05.55 1.41.2 2.46.1 2.72.64.72 1.03 1.64 1.03 2.76 0 3.94-2.34 4.81-4.57 5.07.36.32.68.95.68 1.92v2.79c0 .27.18.59.69.49A10.08 10.08 0 0 0 22 12.25C22 6.59 17.52 2 12 2Z"/></svg>`;
}

function menuIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h18M3 6h18M3 18h18"/></svg>`;
}

function closeIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>`;
}
