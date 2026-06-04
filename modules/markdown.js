export function parseMarkdownDocument(source) {
  const { frontmatter, body } = splitFrontMatter(source);
  const headings = [];
  const footnotes = new Map();
  const bodyWithoutFootnotes = collectFootnotes(body, footnotes);
  const html = renderBlocks(bodyWithoutFootnotes, headings, footnotes);
  return { frontmatter, html, headings, footnotes: Object.fromEntries(footnotes) };
}

function splitFrontMatter(source) {
  const text = String(source ?? "").replace(/\r\n/g, "\n");
  if (!text.startsWith("---\n")) return { frontmatter: {}, body: text };
  const end = text.indexOf("\n---", 4);
  if (end === -1) return { frontmatter: {}, body: text };
  return {
    frontmatter: parseFrontMatter(text.slice(4, end)),
    body: text.slice(end + 4).trim(),
  };
}

function parseFrontMatter(source) {
  const data = {};
  let activeKey = null;
  for (const rawLine of source.split("\n")) {
    const line = rawLine.trimEnd();
    if (!line.trim()) continue;
    const listMatch = line.match(/^\s*-\s+(.+)$/);
    if (activeKey && listMatch) {
      data[activeKey].push(cleanValue(listMatch[1]));
      continue;
    }
    const match = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!match) continue;
    const [, key, value] = match;
    if (value === "") {
      data[key] = [];
      activeKey = key;
    } else {
      data[key] = cleanValue(value);
      activeKey = null;
    }
  }
  return data;
}

function cleanValue(value) {
  const text = value.trim();
  if (text === "true") return true;
  if (text === "false") return false;
  if (text.startsWith("[") && text.endsWith("]")) {
    return text
      .slice(1, -1)
      .split(",")
      .map((entry) => cleanValue(entry))
      .filter((entry) => entry !== "");
  }
  return text.replace(/^["']|["']$/g, "");
}

function collectFootnotes(source, footnotes) {
  const lines = source.split("\n");
  const body = [];
  for (const line of lines) {
    const match = line.match(/^\[\^([^\]]+)\]:\s*(.+)$/);
    if (match) {
      footnotes.set(match[1].trim(), match[2].trim());
    } else {
      body.push(line);
    }
  }
  return body.join("\n").trim();
}

function renderBlocks(source, headings, footnotes, includeFootnotes = true) {
  const lines = source.split("\n");
  const html = [];
  let paragraph = [];
  let list = [];
  let quote = [];
  let code = [];
  let table = [];
  let math = [];
  let codeLang = "";
  let callout = null;
  let inCode = false;
  let inMath = false;

  const flushParagraph = () => {
    if (!paragraph.length) return;
    html.push(`<p>${inline(paragraph.join(" "), footnotes)}</p>`);
    paragraph = [];
  };
  const flushList = () => {
    if (!list.length) return;
    html.push(`<ul>${list.map((item) => `<li>${inline(item, footnotes)}</li>`).join("")}</ul>`);
    list = [];
  };
  const flushQuote = () => {
    if (!quote.length) return;
    html.push(`<blockquote>${quote.map((item) => `<p>${inline(item, footnotes)}</p>`).join("")}</blockquote>`);
    quote = [];
  };
  const flushCode = () => {
    const language = codeLang || "text";
    html.push(`
      <figure class="md-codeblock">
        <figcaption><span>${esc(language)}</span><button type="button" data-copy-code>Copy</button></figcaption>
        <pre><code${codeLang ? ` class="language-${esc(codeLang)}"` : ""}>${esc(code.join("\n"))}</code></pre>
      </figure>
    `);
    code = [];
    codeLang = "";
  };
  const flushTable = () => {
    if (!table.length) return;
    html.push(renderTable(table, footnotes));
    table = [];
  };
  const flushMath = () => {
    if (!math.length) return;
    html.push(`<div class="md-math" role="img" aria-label="mathematical expression">\\[${esc(math.join("\n"))}\\]</div>`);
    math = [];
  };
  const flushOpen = () => {
    flushParagraph();
    flushList();
    flushQuote();
    flushTable();
  };

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();

    if (line.trim() === "$$") {
      if (inMath) {
        flushMath();
        inMath = false;
      } else {
        flushOpen();
        inMath = true;
      }
      continue;
    }
    if (inMath) {
      math.push(rawLine);
      continue;
    }

    if (line.startsWith("```")) {
      if (inCode) {
        flushCode();
        inCode = false;
      } else {
        flushOpen();
        inCode = true;
        codeLang = line.slice(3).trim();
      }
      continue;
    }
    if (inCode) {
      code.push(rawLine);
      continue;
    }

    const calloutStart = line.match(/^:::(note|tip|warning|result|important|danger)\s*(.*)$/);
    if (calloutStart) {
      flushOpen();
      callout = { type: calloutStart[1], title: calloutStart[2] || calloutStart[1], lines: [] };
      continue;
    }
    if (callout && line === ":::") {
      const inner = renderBlocks(callout.lines.join("\n"), [], footnotes, false);
      html.push(`<aside class="md-callout md-callout-${esc(callout.type)}"><strong>${inline(callout.title, footnotes)}</strong>${inner}</aside>`);
      callout = null;
      continue;
    }
    if (callout) {
      callout.lines.push(line);
      continue;
    }

    if (!line.trim()) {
      flushOpen();
      continue;
    }

    if (isTableLine(line)) {
      flushParagraph();
      flushList();
      flushQuote();
      table.push(line);
      continue;
    }
    flushTable();

    const heading = line.match(/^(#{2,4})\s+(.+)$/);
    if (heading) {
      flushOpen();
      const level = heading[1].length;
      const text = heading[2].trim();
      const id = slugify(text);
      headings.push({ id, text, level });
      html.push(`<h${level} id="${esc(id)}">${inline(text, footnotes)}</h${level}>`);
      continue;
    }

    const shortcode = line.match(/^\{\{\s*([a-zA-Z-]+):([^}]+)\s*\}\}$/);
    if (shortcode) {
      flushOpen();
      html.push(`<div data-shortcode="${esc(shortcode[1])}" data-shortcode-value="${esc(shortcode[2].trim())}"></div>`);
      continue;
    }

    const image = line.match(/^!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]+)")?\)$/);
    if (image) {
      flushOpen();
      const [, alt, src, caption] = image;
      html.push(`<figure class="md-figure"><img src="${esc(src)}" alt="${esc(alt)}" loading="lazy" decoding="async">${caption ? `<figcaption>${inline(caption, footnotes)}</figcaption>` : ""}</figure>`);
      continue;
    }

    if (/^---+$/.test(line.trim())) {
      flushOpen();
      html.push("<hr>");
      continue;
    }

    const listItem = line.match(/^[-*]\s+(.+)$/);
    if (listItem) {
      flushParagraph();
      flushQuote();
      list.push(listItem[1]);
      continue;
    }

    const quoteLine = line.match(/^>\s?(.+)$/);
    if (quoteLine) {
      flushParagraph();
      flushList();
      quote.push(quoteLine[1]);
      continue;
    }

    flushList();
    flushQuote();
    paragraph.push(line.trim());
  }

  flushOpen();
  if (inCode) flushCode();
  if (inMath) flushMath();
  if (includeFootnotes && footnotes.size) html.push(renderFootnotes(footnotes));
  return html.join("\n");
}

function isTableLine(line) {
  return /^\|.+\|$/.test(line.trim());
}

function renderTable(rows, footnotes) {
  if (rows.length < 2 || !/^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$/.test(rows[1])) {
    return `<p>${inline(rows.join(" "), footnotes)}</p>`;
  }
  const cells = rows.map((row) => row.trim().replace(/^\||\|$/g, "").split("|").map((cell) => cell.trim()));
  const [head, , ...body] = cells;
  return `
    <div class="md-table-wrap">
      <table class="md-table">
        <thead><tr>${head.map((cell) => `<th>${inline(cell, footnotes)}</th>`).join("")}</tr></thead>
        <tbody>${body.map((row) => `<tr>${row.map((cell) => `<td>${inline(cell, footnotes)}</td>`).join("")}</tr>`).join("")}</tbody>
      </table>
    </div>
  `;
}

function renderFootnotes(footnotes) {
  return `
    <section class="md-footnotes" aria-label="Footnotes">
      <h2 id="footnotes">注释</h2>
      <ol>
        ${[...footnotes].map(([key, text]) => `<li id="fn-${esc(key)}">${inline(text, footnotes)} <a href="#fnref-${esc(key)}" aria-label="返回正文">↩</a></li>`).join("")}
      </ol>
    </section>
  `;
}

function inline(value, footnotes = new Map()) {
  return esc(value)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/==([^=]+)==/g, "<mark>$1</mark>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>")
    .replace(/\$([^$\n]+)\$/g, (_, math) => `<span class="md-inline-math">\\(${esc(math)}\\)</span>`)
    .replace(/\[cite:([^\]]+)\]/g, (_, key) => `<a class="md-cite" href="#ref-${slugify(key)}">[${esc(key)}]</a>`)
    .replace(/\[\^([^\]]+)\]/g, (_, key) => footnotes.has(key) ? `<sup id="fnref-${esc(key)}"><a href="#fn-${esc(key)}">${esc(key)}</a></sup>` : `<sup>${esc(key)}</sup>`)
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
}

function slugify(value) {
  return String(value ?? "")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80);
}

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
