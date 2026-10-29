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
  link.textContent = "Consulter l'article original";
  sourceBox.append(byline, link);
  sourceBox.hidden = false;
}

async function loadNews() {
  const response = await fetch("./news.json", {cache:"no-store"});
  if (!response.ok) throw Error("Les informations récentes ne sont pas disponibles.");
  const feed = await response.json();
  if (feed.schema !== 1 || !Array.isArray(feed.items)) throw Error("Format des actualités incorrect.");
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
  message("Vérification des actualités récentes…");
  try {
    const pool = await loadNews();
    if (!pool.length) throw Error("Aucun article récent n'est disponible : lance le mode random_news depuis GitHub Actions.");
    showArticle(pickImportant(pool));
    message("Actualité sélectionnée. Le lien source et la date figurent ci-dessus.");
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
  if (text.length < 3 || text.length > 500) throw Error("Le sujet doit contenir entre 3 et 500 caractères.");
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
    ? "Dans GitHub Actions, sélectionne mode = article_url et colle l'adresse copiée dans article_url."
    : "Dans GitHub Actions, sélectionne mode = custom et colle le sujet copié dans custom_topic.";
  manual.hidden = false;
  launched.hidden = true;
}

$("#copy").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(valueToCopy);
    message("Valeur copiée. Ouvre GitHub Actions et lance le workflow.");
  } catch {
    message("Copie manuellement le sujet ou l'URL dans le champ GitHub Actions.", true);
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
      message("Le rendu est prêt à être lancé depuis GitHub Actions, sans jeton.");
      return;
    }
    message("Envoi sécurisé directement à GitHub…");
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
      if (code === 401 || code === 403) throw Error("Le jeton n'a pas les permissions GitHub Actions nécessaires. Vérifie les droits ou lance le workflow manuellement.");
      throw Error("Déclenchement refusé par GitHub (HTTP " + code + "). Lance le workflow manuellement.");
    }
    token.value = "";
    launched.hidden = false;
    message("La demande a été acceptée par GitHub. Ouvre les exécutions pour suivre le rendu.");
  } catch (error) {
    message(error.message + " Aucune vidéo n'est confirmée.", true);
    try { showManual(inputs()); } catch {}
  } finally {
    createButton.disabled = false;
  }
});

loadNews().then(pool => {
  if (pool.length) message(pool.length + " actualités récentes sourcées disponibles.");
  else message("Aucune actualité récente préchargée. Le mode random_news reste disponible depuis GitHub Actions.");
}).catch(() => {
  message("Actualités momentanément indisponibles. Tu peux créer une vidéo sur un sujet libre.");
});
