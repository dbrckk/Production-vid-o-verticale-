"use strict";

const REPO = "dbrckk/Production-vid-o-verticale-";
const WORKFLOW = "render.yml";
const WORKFLOW_URL = "https://github.com/" + REPO + "/actions/workflows/" + WORKFLOW;
const API_URL = "https://api.github.com/repos/" + REPO + "/actions/workflows/" + WORKFLOW + "/dispatches";
const MAX_AGE_HOURS = 72;
const $ = selector => document.querySelector(selector);
const topic = $("#topic"), quality = $("#quality"), token = $("#token");
const status = $("#status"), randomButton = $("#random"), createButton = $("#create");
const sourceBox = $("#article"), manual = $("#manual"), launched = $("#launched");
let selectedArticle = null, articles = [], valueToCopy = "";

function message(text, error = false) {
  status.textContent = text;
  status.classList.toggle("error", error);
}

function isFresh(article, now = Date.now()) {
  const published = Date.parse(article.published);
  const ageHours = (now - published) / 3600000;
  return Boolean(article.title && article.source && /^https:\/\//.test(article.url))
    && Number.isFinite(published) && ageHours >= -1 && ageHours <= MAX_AGE_HOURS;
}

function resetArticle() {
  selectedArticle = null;
  sourceBox.replaceChildren();
  sourceBox.hidden = true;
}

function showArticle(article) {
  resetArticle();
  selectedArticle = article;
  topic.value = article.title;
  const byline = document.createElement("span");
  byline.textContent = article.source + " · " + new Date(article.published).toLocaleString("fr-FR") + " · ";
  const link = document.createElement("a");
  link.href = article.url;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.textContent = "Read the original article";
  sourceBox.append(byline, link);
  sourceBox.hidden = false;
}

async function loadNews() {
  const response = await fetch("./news.json", {cache:"no-store"});
  if (!response.ok) throw Error("Fresh news is not currently available.");
  const feed = await response.json();
  if (feed.schema !== 1 || !Array.isArray(feed.items)) throw Error("News feed format is invalid.");
  articles = feed.items.filter(item => isFresh(item));
  return articles;
}

function pickImportant(pool) {
  const french = pool.filter(x => ["franceinfo","France 24","Le Monde"].includes(x.source));
  const shortlist = (french.length ? french : pool).slice(0, 15);
  const weights = shortlist.map(x => Math.max(.1, Number(x.importance) - .75) ** 2);
  let point = Math.random() * weights.reduce((sum, weight) => sum + weight, 0);
  for (let i = 0; i < shortlist.length; i++) {
    point -= weights[i];
    if (point <= 0) return shortlist[i];
  }
  return shortlist.at(-1);
}

randomButton.addEventListener("click", async () => {
  randomButton.disabled = true;
  manual.hidden = true;
  launched.hidden = true;
  message("Checking recent English-language news…");
  try {
    const pool = await loadNews();
    if (!pool.length) throw Error("No recent English news found. Use the random_news mode on GitHub Actions.");
    showArticle(pickImportant(pool));
    message("News selected. The source and date are linked above.");
  } catch (error) {
    message(error.message, true);
  } finally {
    randomButton.disabled = false;
  }
});

topic.addEventListener("input", () => {
  if (selectedArticle && topic.value.trim() !== selectedArticle.title) resetArticle();
});

function inputs() {
  const text = topic.value.trim();
  if (text.length < 3 || text.length > 500) throw Error("Enter an English topic between 3 and 500 characters.");
  const article = selectedArticle && text === selectedArticle.title && isFresh(selectedArticle)
    ? selectedArticle : null;
  if (selectedArticle && !article) resetArticle();
  return {
    mode: article ? "article_url" : "custom",
    custom_topic: article ? "" : text,
    article_url: article ? article.url : "",
    quality: quality.value,
    title: "",
  };
}

function showManual(data) {
  const articleMode = data.mode === "article_url";
  valueToCopy = articleMode ? data.article_url : data.custom_topic;
  $("#manual-help").textContent = articleMode
    ? "In GitHub Actions, choose mode = article_url and paste the news URL."
    : "In GitHub Actions, choose mode = custom and paste your English topic.";
  manual.hidden = false;
  launched.hidden = true;
}

$("#copy").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(valueToCopy);
    message("Copied. Open GitHub Actions and start the workflow.");
  } catch {
    message("Copy the topic or URL manually into GitHub Actions.", true);
  }
});

createButton.addEventListener("click", async () => {
  createButton.disabled = true;
  manual.hidden = true;
  launched.hidden = true;
  try {
    const data = inputs();
    const secret = token.value.trim();
    if (!secret) {
      showManual(data);
      message("Ready to render via GitHub Actions without a browser token.");
      return;
    }
    message("Sending directly to GitHub securely…");
    const response = await fetch(API_URL, {
      method:"POST",
      headers:{
        "Accept":"application/vnd.github+json",
        "Authorization":"Bearer " + secret,
        "X-GitHub-Api-Version":"2022-11-28",
        "Content-Type":"application/json",
      },
      body: JSON.stringify({ref:"main",inputs:data}),
    });
    if (!response.ok) {
      const code = response.status;
      if (code === 401 || code === 403) throw Error("Your token lacks GitHub Actions permissions. Check the scopes or start manually.");
      throw Error("GitHub rejected the workflow request (HTTP " + code + "). Start the workflow manually.");
    }
    token.value = "";
    launched.hidden = false;
    message("GitHub accepted the request. Check workflow runs for your English-narrated MP4.");
  } catch (error) {
    message(error.message + " No video has been confirmed.", true);
    try { showManual(inputs()); } catch {}
  } finally {
    createButton.disabled = false;
  }
});

loadNews().then(pool => {
  if (pool.length) message(pool.length + " recent sourced stories available.");
  else message("No recent stories are cached. The random_news mode is available on GitHub Actions.");
}).catch(() => {
  message("News is temporarily unavailable. You can still create a custom English video.");
});
