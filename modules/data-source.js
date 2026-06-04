import { parseMarkdownDocument } from "./markdown.js";

const SITE_ROOT = new URL("../", import.meta.url);
const LOCAL_SITE_ROOT = "/home/chunfengfusu/web/research-showcase/";

export async function loadRegistry() {
  return loadJson("data/registry.json");
}

export async function loadContentIndex() {
  return loadJson("data/content.json");
}

export async function loadProject(path) {
  return attachMarkdown(await loadJson(path));
}

export async function loadArticle(path) {
  return attachMarkdown(await loadJson(path));
}

export async function loadProjects(projectEntries) {
  return Promise.all(
    projectEntries.map(async (entry) => {
      const data = entry.data ? await loadProject(entry.data) : await attachMarkdown({ ...entry, metadata: entry.metadata ?? {}, summary: entry.summary ?? "" });
      return { ...entry, data: normalizeProject(data) };
    }),
  );
}

export async function loadArticles(articleEntries = []) {
  return Promise.all(
    articleEntries.map(async (entry) => {
      const data = entry.data ? await loadArticle(entry.data) : await attachMarkdown({ ...entry, metadata: entry.metadata ?? {}, summary: entry.summary ?? "" });
      return { ...entry, data };
    }),
  );
}

async function loadJson(path) {
  const url = new URL(path, SITE_ROOT);
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${path}: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

async function loadText(path) {
  const url = new URL(path, SITE_ROOT);
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${path}: ${response.status} ${response.statusText}`);
  }
  return response.text();
}

async function attachMarkdown(entry) {
  if (!entry.content) return entry;
  const document = parseMarkdownDocument(await loadText(entry.content));
  document.html = resolveMarkdownPaths(document.html, entry.content);
  return {
    ...entry,
    markdown: document,
    metadata: mergeMetadata(entry.metadata, document.frontmatter),
    title: document.frontmatter.title ?? entry.title,
    subtitle: document.frontmatter.subtitle ?? entry.subtitle,
    category: document.frontmatter.category ?? entry.category,
    type: document.frontmatter.type ?? entry.type,
    titleShort: document.frontmatter.titleShort ?? entry.titleShort,
    hero: document.frontmatter.hero ?? entry.hero,
    hidden: document.frontmatter.hidden ?? entry.hidden,
    pinned: document.frontmatter.pinned ?? entry.pinned,
    methods: document.frontmatter.methods ?? entry.methods,
    projects: document.frontmatter.projects ?? entry.projects,
    referenceKeys: document.frontmatter.references ?? entry.referenceKeys,
    references: entry.references ?? parseReferenceItems(document.frontmatter.referenceItems),
    related: mergeRelated(entry.related, document.frontmatter),
    dataAvailability: document.frontmatter.dataAvailability ?? entry.dataAvailability,
    summary: document.frontmatter.summary
      ? (Array.isArray(entry.summary) ? [document.frontmatter.summary] : document.frontmatter.summary)
      : entry.summary,
  };
}

function normalizeProject(entry) {
  if (entry.type !== "project") return entry;
  const summary = Array.isArray(entry.summary) ? entry.summary : [entry.summary].filter(Boolean);
  const cover = coverFromFrontmatter(entry);
  const fallbackMedia = cover
    ? { items: [{ id: "hero", role: "hero", type: "image", title: entry.title, src: cover, method: "Markdown front matter" }] }
    : { items: [] };
  return {
    media: fallbackMedia,
    references: [],
    related: {},
    reproducibility: {},
    ...entry,
    summary,
    claim: {
      question: entry.question ?? summary[0] ?? "",
      contribution: entry.contribution ?? summary[0] ?? "",
      findings: entry.findings ?? summary,
      limitations: entry.limitations ?? [],
      ...(entry.claim ?? {}),
    },
  };
}

function resolveMarkdownPaths(html, contentPath) {
  return String(html ?? "").replace(/\b(href|src)="([^"]+)"/g, (_, attr, target) => {
    return `${attr}="${resolveContentTarget(target, contentPath)}"`;
  });
}

function resolveContentTarget(target, contentPath = "") {
  if (!target) return target;
  if (target.startsWith(LOCAL_SITE_ROOT)) {
    return target.slice(LOCAL_SITE_ROOT.length);
  }
  if (isAbsoluteOrRooted(target)) return target;
  const base = contentPath.split("/").slice(0, -1).join("/");
  return base ? `${base}/${target}` : target;
}

function isAbsoluteOrRooted(target) {
  return /^(?:[a-z]+:|#|\/|assets\/|content\/|data\/|meta\/|pages\/)/i.test(target);
}

function coverFromFrontmatter(entry) {
  const candidate = entry.cover ?? entry.heroImage ?? entry.thumbnail ?? entry.hero;
  if (!looksLikeAssetPath(candidate)) return null;
  return resolveContentTarget(candidate, entry.content);
}

function looksLikeAssetPath(value) {
  return typeof value === "string" && (/^(?:\.?\.?\/|\/|assets\/|content\/)/.test(value) || /\.(?:png|jpe?g|gif|webp|svg|avif)$/i.test(value));
}

function mergeMetadata(metadata = {}, frontmatter = {}) {
  return {
    ...metadata,
    authors: frontmatter.author ? [frontmatter.author] : metadata.authors,
    publishedAt: frontmatter.publishedAt ?? metadata.publishedAt,
    updatedAt: frontmatter.updatedAt ?? metadata.updatedAt,
    status: frontmatter.status ?? metadata.status,
    tags: frontmatter.tags ?? metadata.tags,
    readingMinutes: frontmatter.readingMinutes ?? metadata.readingMinutes,
    pinned: frontmatter.pinned ?? metadata.pinned,
  };
}

function parseReferenceItems(items = []) {
  return asList(items).map((item) => {
    const [key, title, url] = String(item).split("|").map((part) => part.trim());
    return { key, title: title ?? key, url: url ?? "#" };
  }).filter((item) => item.key);
}

function mergeRelated(related = {}, frontmatter = {}) {
  return {
    projects: asList(frontmatter.relatedProjects ?? frontmatter.projects ?? related.projects),
    articles: asList(frontmatter.relatedArticles ?? related.articles),
    methods: asList(frontmatter.relatedMethods ?? frontmatter.methods ?? related.methods),
  };
}

function asList(value) {
  if (value === null || value === undefined || value === "") return [];
  return Array.isArray(value) ? value : [value];
}
