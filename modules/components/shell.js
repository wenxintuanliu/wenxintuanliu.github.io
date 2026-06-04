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
  root.append(createScrollTop());

  requestAnimationFrame(() => {
    initThemeToggle();
    initMobileNav();
    initScrollEffects();
    initLightbox();
    initExplorables();
    initComparePanels();
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

function initThemeToggle() {
  const toggle = document.getElementById("theme-toggle");
  if (!toggle) return;

  const saved = localStorage.getItem("theme");
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const theme = saved || (prefersDark ? "dark" : "light");
  applyTheme(theme);

  toggle.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    const next = current === "dark" ? "light" : "dark";
    applyTheme(next);
    localStorage.setItem("theme", next);
  });
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const toggle = document.getElementById("theme-toggle");
  if (toggle) {
    toggle.innerHTML = theme === "dark" ? sunIcon() : moonIcon();
  }
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

function typesetMath(attempt = 0) {
  if (window.MathJax?.typesetPromise) {
    window.MathJax.typesetPromise().catch(() => {});
    return;
  }
  if (attempt < 12) {
    window.setTimeout(() => typesetMath(attempt + 1), 250);
  }
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

function menuIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h18M3 6h18M3 18h18"/></svg>`;
}

function closeIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>`;
}
