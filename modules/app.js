import { loadArticles, loadContentIndex, loadRegistry, loadProjects } from "./data-source.js";
import { renderShell } from "./components/shell.js";
import { renderPage } from "./views/project-page.js";

const app = document.getElementById("app");
const currentPage = document.body.dataset.page ?? "home";

async function boot() {
  try {
    const registry = await loadRegistry();
    const route = pageKind();
    const needsProjects = ["home", "projects", "methods", "knowledge", "project-detail", "article"].includes(route);
    const needsArticles = ["knowledge", "project-detail", "article"].includes(route);
    const needsContent = route === "knowledge";
    const [content, projects, articles] = await Promise.all([
      needsContent ? loadContentIndex() : Promise.resolve({}),
      needsProjects ? loadProjects(registry.projects) : Promise.resolve([]),
      needsArticles ? loadArticles(registry.methodArticles ?? registry.articles ?? []) : Promise.resolve(minimalArticles(registry)),
    ]);
    const featuredProject = projects.find((project) => project.featured) ?? projects[0];
    const requestedProjectId = new URLSearchParams(window.location.search).get("id");
    const requestedArticleId = new URLSearchParams(window.location.search).get("id");
    const activeProject = projects.find((project) => project.id === requestedProjectId) ?? featuredProject;
    const activeArticle = articles.find((article) => article.id === requestedArticleId) ?? articles[0];
    const context = {
      registry,
      content,
      projects,
      articles,
      project: activeProject?.data,
      article: activeArticle?.data,
      featuredProject: featuredProject?.data,
    };
    updateDocumentMeta(currentPage, context);
    app.innerHTML = "";
    app.append(renderShell(registry, renderPage(currentPage, context), currentPage));
  } catch (error) {
    app.innerHTML = `
      <main class="error-state">
        <h1>数据加载失败</h1>
        <p>请通过本地静态服务器打开本站点，而不是直接用 file:// 打开。</p>
        <pre>${String(error)}</pre>
      </main>
    `;
  }
}

function pageKind() {
  const path = window.location.pathname;
  if (path.endsWith("/pages/project.html")) return "project-detail";
  if (path.endsWith("/pages/method.html")) return "article";
  if (path.endsWith("/pages/projects.html")) return "projects";
  if (path.endsWith("/pages/methods.html")) return "methods";
  if (path.endsWith("/pages/knowledge.html")) return "knowledge";
  if (path.endsWith("/pages/about.html")) return "about";
  return currentPage;
}

function minimalArticles(registry) {
  return (registry.methodArticles ?? registry.articles ?? []).map((entry) => ({
    ...entry,
    data: {
      ...entry,
      metadata: entry.metadata ?? {},
      hidden: entry.hidden,
      summary: entry.summary ?? "",
    },
  }));
}

function updateDocumentMeta(page, context) {
  const path = window.location.pathname;
  const titleParts = {
    home: ["CFD Research"],
    projects: ["项目", "CFD Research"],
    methods: ["数值方法", "CFD Research"],
    knowledge: ["知识库", "CFD Research"],
    article: [context.article?.title ?? "文章", "CFD Research"],
    about: ["关于", "CFD Research"],
  };

  if (path.endsWith("/pages/project.html")) {
    document.title = `${context.project.title} | CFD Research`;
  } else if (path.endsWith("/pages/method.html")) {
    document.title = `${context.article?.title ?? "文章"} | CFD Research`;
  } else {
    document.title = (titleParts[page] ?? titleParts.home).join(" | ");
  }

  const description =
    path.endsWith("/pages/project.html")
      ? context.project.summary?.[0]
      : path.endsWith("/pages/method.html")
        ? context.article?.summary
        : context.registry.profile?.summary;
  setMeta("description", description ?? "高保真流体计算、数值方法与科学可视化科研展示站。");
  setMeta("og:title", document.title, "property");
  setMeta("og:description", description ?? "高保真流体计算、数值方法与科学可视化科研展示站。", "property");
  setMeta("og:type", path.endsWith("/pages/project.html") || path.endsWith("/pages/method.html") ? "article" : "website", "property");
}

function setMeta(name, content, attr = "name") {
  let tag = document.head.querySelector(`meta[${attr}="${name}"]`);
  if (!tag) {
    tag = document.createElement("meta");
    tag.setAttribute(attr, name);
    document.head.append(tag);
  }
  tag.setAttribute("content", content);
}

boot();
