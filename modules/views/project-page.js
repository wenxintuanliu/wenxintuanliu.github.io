const LOCAL_SITE_ROOT = "/home/chunfengfusu/web/research-showcase/";

export function renderPage(page, context) {
  const renderers = {
    home: renderHomePage,
    projects: renderProjectsPage,
    "project-detail": renderProjectDetailPage,
    methods: renderMethodsPage,
    knowledge: renderKnowledgePage,
    article: renderArticlePage,
    about: renderAboutPage,
  };
  const inferredPage = inferPage(page);
  return (renderers[inferredPage] ?? renderers.home)(context);
}

export function renderHomePage({ registry, projects, articles, featuredProject }) {
  const media = mediaIndex(featuredProject.media);
  const featuredMedia = pickFeaturedMedia(media.items);
  const visibleArticles = articles.filter((entry) => !entry.hidden && !entry.data?.hidden);
  const main = pageMain("research-home");
  main.innerHTML = `
    <section class="intro portfolio-intro">
      <div class="section-wrap intro-layout">
        <div class="intro-copy animate-in">
          <span class="eyebrow">Research Portfolio</span>
          <h1>${esc(registry.author?.name ?? "CFD Research")}</h1>
          <p class="lead">${esc(registry.profile?.direction ?? "高保真流体计算与科学可视化")}</p>
          <p class="intro-note">${esc(registry.profile?.summary ?? "")}</p>
          <div class="hero-metrics" aria-label="科研能力摘要">
            ${metric("Projects", projects.length)}
            ${metric("Methods", visibleArticles.length)}
            ${metric("Focus", "Research")}
          </div>
          <div class="intro-actions">
            <a class="btn btn-primary" href="${sitePath("pages/projects.html")}">查看项目</a>
            <a class="btn btn-ghost" href="${sitePath("pages/methods.html")}">查看方法</a>
          </div>
        </div>
        ${featuredMedia ? homeMediaVisual(featuredMedia, featuredProject) : ""}
      </div>
      <footer class="hero-footer section-wrap">
        <span class="footer-left">All rights reserved.<a class="secret-entry" href="${sitePath("pages/method.html?id=markdown-style-gallery")}" aria-label="Markdown 样式示例隐藏入口"><img src="${sitePath("assets/secret-entry.png")}" alt=""></a></span>
        <span>Created by <a href="${esc(registry.author?.github ?? "https://github.com/wenxintuanliu/")}" target="_blank" rel="noreferrer">Chunfeng Fusu ${githubIcon()}</a></span>
      </footer>
    </section>
  `;
  return main;
}

export function renderProjectsPage({ projects }) {
  const main = pageMain("project-page");
  main.innerHTML = `
    <section class="page-hero section-wrap animate-in">
      <span class="eyebrow">Projects</span>
      <h1>项目</h1>
      <p>每个项目对应一篇 Markdown 文章,用于展示各个工况的结果。</p>
    </section>
    <section class="project-section section-wrap">
      <div class="project-grid compact-list">
        ${projects.map((entry, i) => projectListCard(entry.data, i)).join("")}
      </div>
    </section>
  `;
  return main;
}

export function renderProjectDetailPage({ project, projects, articles, registry }) {
  const toc = project.markdown?.headings ?? [];
  const body = renderMarkdownContent(project, { project });
  const main = pageMain("project-detail-page");
  main.innerHTML = `
    <section class="article-hero section-wrap animate-in">
      <div class="article-kicker">
        <span class="eyebrow">${esc(project.subtitle ?? "Research Project")}</span>
        ${statusBadge(project.metadata?.status)}
      </div>
      <h1>${esc(project.title)}</h1>
      <p>${esc(project.claim?.question ?? project.story?.question ?? summaryText(project))}</p>
      ${byline(project.metadata)}
    </section>
    <section class="content-section section-wrap">
      <div class="content-layout">
        <article class="article-body content-card">
          ${body}
        </article>
        <aside class="content-sidebar">
          ${tocCard(toc)}
        </aside>
      </div>
    </section>
    <section class="content-section section-wrap">
      ${appendix(project, projects, articles, registry)}
    </section>
  `;
  return main;
}

export function renderKnowledgePage({ registry, content, projects, articles }) {
  const visibleArticles = articles.filter((entry) => !entry.hidden && !entry.data?.hidden);
  const main = pageMain("knowledge-page");
  main.innerHTML = `
    <section class="page-hero section-wrap animate-in">
      <span class="eyebrow">Index</span>
      <h1>内容索引</h1>
      <p>项目文章与方法文章分组展示，每组内部按首次发布时间排序,可快速检索。</p>
    </section>
    <section class="content-section section-wrap">
      <div class="archive-search">
        <label for="archive-search">Search</label>
        <input id="archive-search" type="search" placeholder="搜索标题、摘要、类型或状态" data-archive-search>
      </div>
      <div class="index-stack">
        ${indexGroup("项目", projects.map((entry) => ({ type: "项目", href: `pages/project.html?id=${encodeURIComponent(entry.id)}`, data: entry.data })))}
        ${indexGroup("方法", visibleArticles.map((entry) => ({ type: "方法", href: `pages/method.html?id=${encodeURIComponent(entry.id)}`, data: entry.data })))}
      </div>
    </section>
  `;
  return main;
}

export function renderArticlePage({ article, projects, articles, registry }) {
  const body = article.markdown?.html ? renderMarkdownContent(article, { article }) : (article.blocks ?? []).map(articleBlock).join("");
  const main = pageMain("article-page");
  main.innerHTML = `
    <article>
      <header class="article-hero section-wrap animate-in">
        <div class="article-kicker">
          <span class="eyebrow">${esc(article.category ?? "Article")}</span>
          ${statusBadge(article.metadata?.status)}
        </div>
        <h1>${esc(article.title)}</h1>
        <p>${esc(article.summary ?? article.subtitle ?? "")}</p>
        ${byline(article.metadata)}
      </header>
      <section class="content-section section-wrap">
        <div class="content-layout">
          <div class="article-body content-card">
            ${body}
          </div>
          <aside class="content-sidebar">
            ${tocCard(article.markdown?.headings ?? [])}
          </aside>
        </div>
      </section>
    </article>
    <section class="content-section section-wrap">
      ${referencesDetails(article.references)}
    </section>
  `;
  return main;
}

export function renderMethodsPage({ registry, projects }) {
  const main = pageMain("methods-page");
  const methods = registry.methods ?? [];
  main.innerHTML = `
    <section class="page-hero section-wrap animate-in">
      <span class="eyebrow">Methods</span>
      <h1>方法</h1>
      <p>解释项目正文中出现的数值方法、分析方法与个人见解</p>
    </section>
    <section class="content-section section-wrap">
      <div class="method-list">
        ${methods.map((method) => methodArticleCard(method, projects)).join("")}
      </div>
    </section>
  `;
  return main;
}

export function renderAboutPage({ registry }) {
  const main = pageMain("about-page");
  main.innerHTML = `
    <section class="page-hero section-wrap animate-in">
      <span class="eyebrow">About</span>
      <h1>关于</h1>
      <p>这里记录个人方向、项目整理方式与联系方式。</p>
    </section>
    <section class="about-section section-wrap">
      <div class="about-profile">
        <img src="${sitePath("assets/profile.png")}" alt="个人头像" loading="lazy">
        <div>
          <span class="eyebrow">About Me</span>
          <h2>${esc(registry.profile?.direction ?? "高保真流体计算与科学可视化")}</h2>
          <p>${esc(registry.profile?.summary ?? "这个网站用于把模拟结果、后处理流程和项目材料整理成可持续扩展的科研作品集。")}</p>
          <div class="contact-actions" aria-label="联系方式">
            <a href="${esc(registry.author?.github ?? "https://github.com/wenxintuanliu/")}" target="_blank" rel="noreferrer" aria-label="GitHub">${githubIcon()}</a>
            <a href="mailto:${esc(registry.author?.email ?? "3403208087@qq.com")}" aria-label="Email">${mailIcon()}</a>
          </div>
        </div>
      </div>
      <div class="about-grid">
        ${(registry.profile?.strengths ?? []).map((item) => `<article><span>Capability</span><strong>${esc(item)}</strong><p>围绕真实计算结果、结构化数据和网页化证据持续沉淀。</p></article>`).join("")}
      </div>
    </section>
  `;
  return main;
}

function inferPage(page) {
  const path = window.location.pathname;
  if (path.endsWith("/pages/project.html")) return "project-detail";
  if (path.endsWith("/pages/method.html")) return "article";
  if (path.endsWith("/pages/knowledge.html")) return "knowledge";
  return page;
}

function pageMain(className) {
  const main = document.createElement("main");
  main.id = "top";
  main.className = className;
  return main;
}

function mediaIndex(media) {
  const items = media?.items ?? [];
  return { items, byRole: Object.fromEntries(items.map((item) => [item.role, item])) };
}

function projectFacts(project) {
  if (Array.isArray(project.facts) && project.facts.length) return project.facts;
  const facts = [];
  const nu = Number(project.parameters?.viscosity);
  if (Number.isFinite(nu) && nu > 0) facts.push({ label: "Re", value: Math.round(1 / nu) });
  if (project.run?.mesh?.elements) facts.push({ label: "谱元网格", value: `${project.run.mesh.elements} elements` });
  if (project.parameters?.polynomialOrder) facts.push({ label: "阶数", value: `p = ${project.parameters.polynomialOrder}` });
  if (project.run?.final?.time) facts.push({ label: "时间范围", value: `0.5 - ${project.run.final.time}` });
  return facts.slice(0, 4);
}

function renderProjectMarkdown(project) {
  return renderMarkdownContent(project, { project });
}

function renderMarkdownContent(entry, context = {}) {
  const html = entry.markdown?.html ?? fallbackProjectBody(entry);
  return withSitePaths(html).replace(/<div data-shortcode="([^"]+)" data-shortcode-value="([^"]+)"><\/div>/g, (_, type, value) => {
    if (type === "figure") return inlineFigure(value, context.project?.media ?? entry.media, context.project?.evidence ?? entry.figures);
    if (type === "compare") return inlineCompare(value, context.project?.media ?? entry.media);
    if (type === "explorer") return context.project ? inlineExplorer(value, context.project) : "";
    return "";
  });
}

function projectListCard(project, index) {
  const media = mediaIndex(project.media);
  const featuredMedia = pickFeaturedMedia(media.items);
  return `
    <article class="project-list-card">
      ${featuredMedia ? projectPreview(featuredMedia) : ""}
      <div class="project-list-copy">
        <span class="project-index">${String(index + 1).padStart(2, "0")} / ${esc(project.category ?? "Research Project")}</span>
        <h2>${esc(project.title)}</h2>
        <p>${esc(project.claim?.contribution ?? summaryText(project) ?? project.story?.question ?? "")}</p>
        ${metaLine(project.metadata)}
        <dl class="project-facts compact-facts">
          ${projectFacts(project).slice(0, 4).map((f) => fact(f.label, f.value)).join("")}
        </dl>
        <a class="read-link" href="${sitePath(`pages/project.html?id=${encodeURIComponent(project.id)}`)}">阅读文章</a>
      </div>
    </article>
  `;
}

function summaryText(entry) {
  if (Array.isArray(entry.summary)) return entry.summary[0] ?? "";
  return entry.summary ?? entry.claim?.contribution ?? entry.story?.question ?? "";
}

function pickFeaturedMedia(items) {
  for (const role of ["hero", "featured", "feature", "speed-evolution"]) {
    const item = items.find((e) => e.role === role);
    if (item) return item;
  }
  return items.find((e) => e.src) ?? null;
}

function homeMediaVisual(item, project) {
  return `
    <figure class="intro-visual animate-in-delayed">
      <a href="${sitePath(`pages/project.html?id=${encodeURIComponent(project.id)}`)}" aria-label="查看项目 ${esc(project.title)}">
        <img src="${esc(sitePath(item.src))}" alt="${esc(item.title)}" loading="eager" decoding="async" fetchpriority="high">
      </a>
      <figcaption>
        <strong>代表项目</strong>
        <span>${esc(project.title)}</span>
      </figcaption>
    </figure>
  `;
}

function projectPreview(item) {
  return `<figure class="project-preview"><img data-lazy-src="${esc(sitePath(item.src))}" alt="${esc(item.title)}" loading="lazy" decoding="async" fetchpriority="low"></figure>`;
}

function inlineFigure(role, media, figures = []) {
  const items = media?.items ?? [];
  const item =
    items.find((entry) => entry.role === role || entry.id === role) ??
    figures.find((entry) => entry.id === role || entry.role === role) ??
    items.find((entry) => entry.src);
  if (!item) return "";
  const figure = figures.find((entry) => entry.mediaRole === item.role || entry.mediaRole === role || entry.id === role || entry.role === role);
  const caption = figure?.caption ?? item.caption ?? item.title;
  return `
    <figure class="md-figure evidence-figure" tabindex="0">
      <img src="${esc(sitePath(item.src))}" alt="${esc(item.title)}" loading="lazy" decoding="async">
      <figcaption>${esc(caption)}${item.sourceLabel ? ` — ${esc(item.sourceLabel)}` : ""}</figcaption>
    </figure>
  `;
}

function inlineCompare(value, media) {
  const [leftKey, rightKey] = value.split(",").map((item) => item.trim()).filter(Boolean);
  const left = mediaItem(leftKey, media);
  const right = mediaItem(rightKey, media);
  if (!left || !right) return "";
  return `
    <div class="compare-panel" data-compare-panel>
      <figure>
        <div class="compare-stage">
          <img src="${esc(sitePath(left.src))}" alt="${esc(left.title)}" loading="lazy" decoding="async">
          <img class="compare-top" src="${esc(sitePath(right.src))}" alt="${esc(right.title)}" loading="lazy" decoding="async">
        </div>
        <figcaption>${esc(left.title)} / ${esc(right.title)}</figcaption>
      </figure>
      <label>
        <span>Compare</span>
        <input type="range" min="0" max="100" value="50" aria-label="调整图像对比比例">
      </label>
    </div>
  `;
}

function mediaItem(key, media) {
  if (!key) return null;
  const items = media?.items ?? [];
  return items.find((entry) => entry.role === key || entry.id === key || entry.src === key) ?? { src: key, title: key };
}

function inlineExplorer(kind, project) {
  if (kind === "time") {
    const timed = (project.media?.items ?? []).filter((item) => item.type === "image" && Number.isFinite(Number(item.time)));
    return timed.length >= 2 ? timeScrubber(timed) : "";
  }
  if (kind === "condition") {
    const meanStreamlines = (project.media?.items ?? []).filter((item) => item.role === "mean-streamline");
    return meanStreamlines.length >= 2 ? switcher(meanStreamlines) : "";
  }
  return "";
}

function timeScrubber(items) {
  return `
    <div class="explorable-panel" data-time-scrubber>
      <div class="explorable-copy">
        <span class="project-index">Time Scrubber</span>
        <h3>时间点切换</h3>
        <p>拖动滑块比较同一采样设置下不同时间点的流场图像。</p>
        <input type="range" min="0" max="${items.length - 1}" value="0" step="1" aria-label="选择时间点">
        <output>${esc(items[0].title)}</output>
      </div>
      <figure>
        <img src="${esc(sitePath(items[0].src))}" alt="${esc(items[0].title)}" loading="lazy" decoding="async">
        <figcaption>${esc(items[0].sourceLabel ?? items[0].method ?? "")}</figcaption>
      </figure>
      <script type="application/json">${jsonData(items.map((item) => ({ src: sitePath(item.src), title: item.title, label: item.sourceLabel ?? item.method ?? "" })))}</script>
    </div>
  `;
}

function switcher(items) {
  return `
    <div class="explorable-panel" data-image-switcher>
      <div class="explorable-copy">
        <span class="project-index">Condition Switcher</span>
        <h3>工况对照</h3>
        <p>选择 Reynolds 数和障碍物条件，快速检查平均流线差异。</p>
        <div class="switcher-buttons">
          ${items.map((item, i) => `<button type="button" class="${i === 0 ? "is-active" : ""}" data-index="${i}">${esc(item.title)}</button>`).join("")}
        </div>
      </div>
      <figure>
        <img src="${esc(sitePath(items[0].src))}" alt="${esc(items[0].title)}" loading="lazy" decoding="async">
        <figcaption>${esc(items[0].sourceLabel ?? items[0].method ?? "")}</figcaption>
      </figure>
      <script type="application/json">${jsonData(items.map((item) => ({ src: sitePath(item.src), title: item.title, label: item.sourceLabel ?? item.method ?? "" })))}</script>
    </div>
  `;
}

function tocCard(headings = []) {
  if (!headings.length) {
    return `
      <section class="sidebar-card">
        <h2>目录</h2>
        <p>这篇内容还没有二级标题。</p>
      </section>
    `;
  }
  return `
    <nav class="sidebar-card toc-card" aria-label="正文目录">
      <h2>目录</h2>
      ${headings.map((heading) => `<a class="toc-level-${heading.level}" href="#${esc(heading.id)}">${esc(heading.text)}</a>`).join("")}
    </nav>
  `;
}

function appendix(project, projects, articles, registry) {
  return `
    <div class="appendix">
      <details open>
        <summary>可复现与数据来源</summary>
        ${reproCard(project)}
      </details>
      <details>
        <summary>引用</summary>
        ${referencesList(project.references)}
      </details>
      <details>
        <summary>相关内容</summary>
        ${relatedList(project.related, projects, articles, registry)}
      </details>
    </div>
  `;
}

function referencesDetails(references = []) {
  return `
    <div class="appendix">
      <details open>
        <summary>引用</summary>
        ${referencesList(references)}
      </details>
    </div>
  `;
}

function referencesList(references = []) {
  return references.length
    ? `<ol class="reference-list">${references.map((ref) => `<li id="ref-${slugify(ref.key)}"><a href="${esc(ref.url)}" target="_blank" rel="noreferrer">${esc(ref.title)}</a><span>${esc(ref.key)}</span></li>`).join("")}</ol>`
    : "<p>暂无引用记录。</p>";
}

function relatedList(related = {}, projects = [], articles = [], registry = {}) {
  const methodMap = new Map((registry.methods ?? []).map((method) => [method.id, method]));
  const links = [
    ...(related.projects ?? []).map((id) => {
      const item = projects.find((entry) => entry.id === id)?.data;
      return item ? `<li><a href="${sitePath(`pages/project.html?id=${encodeURIComponent(id)}`)}">${esc(item.titleShort ?? item.title)}</a><span>Project Article</span></li>` : "";
    }),
    ...(related.articles ?? []).map((id) => {
      const item = articles.find((entry) => entry.id === id)?.data;
      return item ? `<li><a href="${sitePath(`pages/method.html?id=${encodeURIComponent(id)}`)}">${esc(item.title)}</a><span>Method Article</span></li>` : "";
    }),
    ...(related.methods ?? []).map((id) => {
      const item = methodMap.get(id);
      if (!item) return "";
      const href = item.article ? `pages/method.html?id=${encodeURIComponent(item.article)}` : `pages/methods.html#${encodeURIComponent(id)}`;
      return `<li><a href="${sitePath(href)}">${esc(item.title)}</a><span>Method</span></li>`;
    }),
  ].filter(Boolean);
  return links.length ? `<ol class="reference-list">${links.join("")}</ol>` : "<p>暂无相关内容。</p>";
}

function sortedItems(items) {
  return [...items].sort((a, b) => {
    const ap = Boolean(a.data.pinned ?? a.data.metadata?.pinned);
    const bp = Boolean(b.data.pinned ?? b.data.metadata?.pinned);
    if (ap !== bp) return ap ? -1 : 1;
    const ad = a.data.metadata?.publishedAt ?? "";
    const bd = b.data.metadata?.publishedAt ?? "";
    return ad.localeCompare(bd) || a.data.title.localeCompare(b.data.title);
  });
}

function indexGroup(title, items) {
  const sorted = sortedItems(items);
  return `
    <section class="index-group">
      <div class="index-group-heading">
        <h2>${esc(title)}</h2>
        <span>${sorted.length} entries</span>
      </div>
      <div class="archive-list">
        ${sorted.map(archiveCard).join("")}
      </div>
    </section>
  `;
}

function archiveCard(item) {
  const data = item.data;
  const searchText = [item.type, data.titleShort, data.title, summaryText(data), data.metadata?.status, ...(data.metadata?.tags ?? [])].filter(Boolean).join(" ");
  return `
    <article class="archive-card" data-search-text="${esc(searchText.toLowerCase())}">
      <time datetime="${esc(data.metadata?.publishedAt ?? "")}">${esc(data.metadata?.publishedAt ?? "未注明日期")}</time>
      <div>
        <span class="project-index">${esc(item.type)}</span>
        ${data.pinned || data.metadata?.pinned ? `<span class="pinned-badge">Pinned</span>` : ""}
        <h2><a href="${esc(sitePath(item.href))}">${esc(data.titleShort ?? data.title)}</a></h2>
        <p>${esc(summaryText(data))}</p>
        ${metaLine(data.metadata)}
      </div>
    </article>
  `;
}

function methodArticleCard(method, projects) {
  const linkedProjects = projects
    .filter((entry) => entry.data.related?.methods?.includes(method.id))
    .map((entry) => `<a href="${sitePath(`pages/project.html?id=${encodeURIComponent(entry.id)}`)}">${esc(entry.data.titleShort ?? entry.data.title)}</a>`)
    .join("");
  const href = method.article ? sitePath(`pages/method.html?id=${encodeURIComponent(method.article)}`) : "#";
  return `
    <article class="method-article-card">
      <div>
        ${statusBadge(method.status)}
        <h2><a href="${href}">${esc(method.title)}</a></h2>
        <p>${esc(method.summary)}</p>
      </div>
      <div class="method-card-links">
        <a class="read-link" href="${href}">阅读方法</a>
        ${linkedProjects ? `<div><span>相关项目</span>${linkedProjects}</div>` : ""}
      </div>
    </article>
  `;
}

function fallbackProjectBody(project) {
  return `
    <h2 id="research-question">研究问题</h2>
    <p>${esc(project.claim?.question ?? project.story?.question ?? "")}</p>
    <h2 id="method">方法</h2>
    <p>${esc(project.story?.method ?? project.media?.method ?? "")}</p>
    <h2 id="findings">主要发现</h2>
    <ul>${(project.claim?.findings ?? project.summary ?? []).map((item) => `<li>${esc(item)}</li>`).join("")}</ul>
  `;
}

function reproCard(project) {
  const repro = project.reproducibility ?? {};
  return `
    <div class="appendix-body">
      <p>${esc(project.dataAvailability ?? "当前项目尚未补充数据可用性说明。")}</p>
      ${repro.environment ? `<p><strong>Environment:</strong> ${esc(repro.environment)}</p>` : ""}
      ${repro.commands?.length ? `<pre><code>${esc(repro.commands.join("\n"))}</code></pre>` : ""}
      ${repro.generatedAssets ? `<p><strong>Generated assets:</strong> ${esc(repro.generatedAssets)}</p>` : ""}
    </div>
  `;
}

function articleBlock(block) {
  if (block.type === "list") {
    return `<ul>${(block.items ?? []).map((item) => `<li>${esc(item)}</li>`).join("")}</ul>`;
  }
  if (block.type === "heading") {
    return `<h2>${esc(block.text)}</h2>`;
  }
  return `<p>${esc(block.text ?? "")}</p>`;
}

function byline(metadata = {}) {
  const authors = metadata.authors?.join(", ") ?? "Chunfeng Fusu";
  return `
    <div class="byline">
      <span>${esc(authors)}</span>
      <span>Published ${esc(metadata.publishedAt ?? "n/a")}</span>
      <span>Updated ${esc(metadata.updatedAt ?? "n/a")}</span>
      <span>${esc(metadata.readingMinutes ?? "5")} min read</span>
    </div>
  `;
}

function metaLine(metadata = {}) {
  return `
    <div class="meta-line">
      ${statusBadge(metadata.status)}
      <span>Updated ${esc(metadata.updatedAt ?? "n/a")}</span>
      <span>${esc(metadata.readingMinutes ?? "5")} min</span>
    </div>
  `;
}

function statusBadge(status = "working") {
  return `<span class="status-badge status-${esc(status)}">${esc(status)}</span>`;
}

function uniqueTags(items) {
  return [...new Set(items.flatMap((item) => item.metadata?.tags ?? item.tags ?? []))].sort();
}

function tagPill(tag) {
  return `<span class="tag-pill">${esc(tag)}</span>`;
}

function metric(label, value) {
  return `<div><strong>${esc(value)}</strong><span>${esc(label)}</span></div>`;
}

function fact(label, value) {
  return `<div><dt>${esc(String(label))}</dt><dd>${esc(String(value ?? "n/a"))}</dd></div>`;
}

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function jsonData(value) {
  return JSON.stringify(value).replaceAll("</", "<\\/");
}

function withSitePaths(html) {
  return String(html ?? "").replace(/\b(href|src)="([^"]+)"/g, (_, attr, path) => `${attr}="${esc(normalizeSiteAssetPath(path))}"`);
}

function normalizeSiteAssetPath(path) {
  if (!path) return path;
  if (path.startsWith(LOCAL_SITE_ROOT)) {
    return sitePath(path.slice(LOCAL_SITE_ROOT.length));
  }
  if (/^(?:assets|content|data|meta|pages)\//.test(path)) {
    return sitePath(path);
  }
  return path;
}

function slugify(value) {
  return String(value ?? "")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80);
}

function sitePath(path) {
  if (!path || /^(?:[a-z]+:|#|\/)/i.test(path)) return path;
  return `${siteRoot()}${path}`;
}

function siteRoot() {
  return window.location.pathname.includes("/pages/") ? "../" : "";
}

function githubIcon() {
  return `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12 2C6.48 2 2 6.59 2 12.25c0 4.53 2.87 8.37 6.84 9.73.5.1.68-.22.68-.49v-1.9c-2.78.62-3.37-1.22-3.37-1.22-.45-1.19-1.11-1.5-1.11-1.5-.91-.64.07-.63.07-.63 1 .07 1.53 1.06 1.53 1.06.9 1.57 2.35 1.12 2.92.86.09-.67.35-1.12.63-1.38-2.22-.26-4.56-1.14-4.56-5.07 0-1.12.39-2.04 1.03-2.76-.1-.26-.45-1.31.1-2.72 0 0 .84-.28 2.75 1.05A9.27 9.27 0 0 1 12 6.93c.85 0 1.7.12 2.5.35 1.9-1.33 2.74-1.05 2.74-1.05.55 1.41.2 2.46.1 2.72.64.72 1.03 1.64 1.03 2.76 0 3.94-2.34 4.81-4.57 5.07.36.32.68.95.68 1.92v2.79c0 .27.18.59.69.49A10.08 10.08 0 0 0 22 12.25C22 6.59 17.52 2 12 2Z"/></svg>`;
}

function mailIcon() {
  return `<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M4.5 5.5h15A2.5 2.5 0 0 1 22 8v8a2.5 2.5 0 0 1-2.5 2.5h-15A2.5 2.5 0 0 1 2 16V8a2.5 2.5 0 0 1 2.5-2.5Zm0 2a.5.5 0 0 0-.5.5v.35l8 4.8 8-4.8V8a.5.5 0 0 0-.5-.5h-15Zm15 9a.5.5 0 0 0 .5-.5v-5.32l-7.49 4.49a1 1 0 0 1-1.02 0L4 10.68V16a.5.5 0 0 0 .5.5h15Z"/></svg>`;
}
