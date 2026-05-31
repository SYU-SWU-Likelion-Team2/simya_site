/*
 * tonight.js
 * Description : 오늘의 밤 프론트 상호작용 및 정적 프로토타입 저장소
 * Author       : 배서현
 * Contributors : Codex
 * Created      : 2026-05-23
 * Last Update  : 2026-05-30
 */

const POSTS_KEY = "simyaCommunityPosts";
const LEGACY_POSTS_KEY = "simyaMyPosts";
const LEGACY_POST_KEY = "simyaMyPost";
const DRAFT_KEY = "simyaPostDraft";
const REACTION_KEY = "simyaPostReactions";
const COMMENT_KEY = "simyaPostComments";
const CURRENT_USER_KEY = "simyaCurrentUserId";
const AUTHOR_LABEL_KEY = "simyaAuthorLabel";
const reactionTypes = ["fire", "stay"];
const SIMYA_ROUTE_FALLBACKS = {
  tonightIndex: "index.html",
  tonightWrite: "write.html",
  tonightFirewood: "firewood.html",
  tonightDetail: "detail.html",
  tonightEdit: "edit.html",
  tonightComments: "comments.html",
  tonightReaction: "reaction.html",
};

function syncSimyaViewportScale() {
  const viewport = window.visualViewport || window;
  const width = viewport.width || window.innerWidth;
  const height = viewport.height || window.innerHeight;
  const isPhoneViewport = Math.min(width, height) <= 540;
  const scaleX = isPhoneViewport ? width / 390 : 1;
  const scaleY = isPhoneViewport ? height / 844 : 1;
  document.documentElement.style.setProperty("--simya-scale-x", scaleX);
  document.documentElement.style.setProperty("--simya-scale-y", scaleY);
}

syncSimyaViewportScale();
window.addEventListener("resize", syncSimyaViewportScale);
if (window.visualViewport) {
  window.visualViewport.addEventListener("resize", syncSimyaViewportScale);
}

function getSimyaRoute(name) {
  return (
    (window.SIMYA_ROUTES && window.SIMYA_ROUTES[name]) ||
    SIMYA_ROUTE_FALLBACKS[name] ||
    "#"
  );
}

function appendQuery(url, params) {
  const query = Object.keys(params)
    .filter(function (key) {
      return params[key] !== undefined && params[key] !== null;
    })
    .map(function (key) {
      return encodeURIComponent(key) + "=" + encodeURIComponent(params[key]);
    })
    .join("&");
  if (!query) return url;
  return url + (url.indexOf("?") === -1 ? "?" : "&") + query;
}

function getPostRoute(name, id) {
  return appendQuery(getSimyaRoute(name), { id: id });
}

const durationMeta = {
  short: {
    title: "짧게 머무는 조용한 불씨",
    label: "작성 시간으로부터 5시간까지",
    fixedMinutes: 300,
  },
  dawn: {
    title: "오늘 새벽 동안 함께 타오름",
    label: "커뮤니티 닫히는 새벽 5시까지",
  },
  day: {
    title: "하루 동안 가장 오래 머무름",
    label: "다음 날 작성 시간부터 24시간 동안",
    fixedMinutes: 1440,
  },
};

const defaultPosts = [
  {
    id: "night-14",
    author: "익명의 밤 14",
    title: "퍼질러졌어요 고민이에요",
    copy: "오늘은 아무것도 못 한 것 같은데 마음만 너무 시끄러워요.",
    detailCopy: "오늘은 아무것도 못 한 것 같은데 마음만 너무 시끄러워요. 누군가에게 설명하기엔 사소하고, 혼자 두기엔 자꾸 커지는 밤이에요.",
    duration: "dawn",
    reactions: { fire: 3, stay: 1 },
  },
  {
    id: "night-23",
    author: "익명의 밤 23",
    title: "퍼질러졌어요 고민이에요",
    copy: "괜찮은 척했는데 밤이 되니까 다시 떠올라요.",
    detailCopy: "괜찮은 척했는데 밤이 되니까 다시 떠올라요. 누군가에게 말하기 애매한 감정이 계속 남아 있어요.",
    duration: "dawn",
    reactions: { fire: 12, stay: 4 },
  },
  {
    id: "night-31",
    author: "익명의 밤 31",
    title: "퍼질러졌어요 고민이에요",
    copy: "오늘은 아무것도 못 한 것 같은데 마음만 너무 시끄러워요.",
    detailCopy: "오늘은 아무것도 못 한 것 같은데 마음만 너무 시끄러워요. 누군가에게 설명하기엔 사소하고, 혼자 두기엔 자꾸 커지는 밤이에요.",
    duration: "dawn",
    reactions: { fire: 0, stay: 0 },
  },
];

const defaultComments = [];

function readJson(key, fallback) {
  try {
    return JSON.parse(window.localStorage.getItem(key)) || fallback;
  } catch (error) {
    return fallback;
  }
}

function writeJson(key, value) {
  window.localStorage.setItem(key, JSON.stringify(value));
}

function getCurrentUserId() {
  const params = new URLSearchParams(window.location.search);
  const urlUser = params.get("userId") || params.get("viewer");
  if (urlUser) {
    window.localStorage.setItem(CURRENT_USER_KEY, urlUser);
    return urlUser;
  }
  let userId = window.localStorage.getItem(CURRENT_USER_KEY);
  if (!userId) {
    userId = "local-user";
    window.localStorage.setItem(CURRENT_USER_KEY, userId);
  }
  return userId;
}

function getCurrentAuthorLabel() {
  const labelKey = AUTHOR_LABEL_KEY + ":" + getCurrentUserId();
  let label = window.localStorage.getItem(labelKey);
  if (!label) {
    label = "익명의 밤 " + String(Math.floor(Math.random() * 90) + 10);
    window.localStorage.setItem(labelKey, label);
  }
  return label;
}

function padTime(value) {
  return String(value).padStart(2, "0");
}

function getNextDawnDeadline(from) {
  const date = from ? new Date(from) : new Date();
  const deadline = new Date(date);
  deadline.setHours(5, 0, 0, 0);
  if (deadline <= date) {
    deadline.setDate(deadline.getDate() + 1);
  }
  return deadline;
}

function getDeadlineForDuration(duration, from) {
  const date = from ? new Date(from) : new Date();
  const durationKey = durationMeta[duration] ? duration : "dawn";
  const meta = durationMeta[durationKey];
  if (durationKey === "dawn") return getNextDawnDeadline(date);
  return new Date(date.getTime() + meta.fixedMinutes * 60000);
}

function getPostExpiresAt(post) {
  const savedExpiresAt = Date.parse((post && post.expiresAt) || "");
  if (Number.isFinite(savedExpiresAt)) return savedExpiresAt;
  const createdAt = Date.parse((post && post.createdAt) || "");
  if (Number.isFinite(createdAt)) {
    return getDeadlineForDuration(post.duration || "dawn", new Date(createdAt)).getTime();
  }
  return getDeadlineForDuration(post && post.duration).getTime();
}

function getRemainingMinutes(post) {
  return Math.max(0, Math.ceil((getPostExpiresAt(post) - Date.now()) / 60000));
}

function formatRemaining(totalMinutes, short) {
  const minutes = Math.max(0, totalMinutes);
  const hours = Math.floor(minutes / 60);
  const restMinutes = minutes % 60;
  if (short && hours === 0) return restMinutes + "분";
  if (hours === 0) return restMinutes + "분 남음";
  return hours + "시간 " + padTime(restMinutes) + "분 남음";
}

function formatHubDawnText() {
  const minutes = Math.max(0, Math.ceil((getNextDawnDeadline() - Date.now()) / 60000));
  const hours = Math.floor(minutes / 60);
  const restMinutes = minutes % 60;
  if (hours === 0) return "새벽까지 " + restMinutes + "분 남았어요";
  if (restMinutes === 0) return "새벽까지 " + hours + "시간 남았어요";
  return "새벽까지 " + hours + "시간 " + restMinutes + "분 남았어요";
}

function formatClockRemaining(totalMinutes) {
  const minutes = Math.max(0, totalMinutes);
  const hours = Math.floor(minutes / 60);
  const restMinutes = minutes % 60;
  return padTime(hours) + ":" + padTime(restMinutes) + " 남음";
}

function formatPostTime(post) {
  const createdAt = new Date(post.createdAt || Date.now());
  return padTime(createdAt.getHours()) + ":" + padTime(createdAt.getMinutes());
}

function getPreview(copy, length) {
  const clean = String(copy || "").replace(/\s+/g, " ").trim();
  return clean.slice(0, length) + (clean.length > length ? "..." : "");
}

function savePosts(posts) {
  writeJson(POSTS_KEY, posts);
}

function normalizeCommunityPost(post, mineFallback) {
  const currentUserId = getCurrentUserId();
  const shouldTreatAsMine =
    post.isMine === true ||
    mineFallback ||
    (post.isMine !== false && /^post-/.test(String(post.id || "")));
  const authorId = post.authorId || (shouldTreatAsMine ? currentUserId : "");
  return Object.assign(
    { author: authorId === currentUserId ? getCurrentAuthorLabel() : "익명의 밤", duration: "dawn", reactions: { fire: 0, stay: 0 } },
    post,
    { authorId: authorId, isMine: authorId === currentUserId }
  );
}

function getSavedPosts() {
  let posts = readJson(POSTS_KEY, []);
  const legacyPosts = readJson(LEGACY_POSTS_KEY, []);
  const legacyPost = readJson(LEGACY_POST_KEY, null);
  let shouldSave = false;
  if (!Array.isArray(posts)) posts = [];
  if (!posts.length && Array.isArray(legacyPosts) && legacyPosts.length) {
    posts = legacyPosts.map(function (post) { return normalizeCommunityPost(post, true); });
    shouldSave = true;
  }
  if (!posts.length && legacyPost && legacyPost.copy) {
    posts = [normalizeCommunityPost(Object.assign({ id: legacyPost.id || "post-" + Date.now(), author: getCurrentAuthorLabel(), title: "내가 남긴 밤", duration: legacyPost.duration || "dawn", createdAt: legacyPost.createdAt || new Date().toISOString(), updatedAt: legacyPost.updatedAt || legacyPost.createdAt || new Date().toISOString() }, legacyPost), true)];
    window.localStorage.removeItem(LEGACY_POST_KEY);
    shouldSave = true;
  }
  const normalizedPosts = posts.map(function (post) { return normalizeCommunityPost(post, false); });
  const activePosts = normalizedPosts.filter(function (post) { return getPostExpiresAt(post) > Date.now(); });
  if (shouldSave || activePosts.length !== posts.length || JSON.stringify(activePosts) !== JSON.stringify(posts)) {
    savePosts(activePosts);
  }
  return activePosts;
}

function updatePost(id, patch) {
  const posts = getSavedPosts().map(function (post) {
    if (post.id !== id) return post;
    return Object.assign({}, post, patch, { updatedAt: new Date().toISOString() });
  });
  savePosts(posts);
}

function deletePost(id) {
  savePosts(getSavedPosts().filter(function (post) { return post.id !== id; }));
  const reactionStore = getReactionStore();
  const commentStore = getCommentStore();
  delete reactionStore[id];
  delete commentStore[id];
  saveReactionStore(reactionStore);
  saveCommentStore(commentStore);
}

function getCurrentPostId() {
  const params = new URLSearchParams(window.location.search);
  return params.get("id") || document.body.dataset.postId || null;
}

function isPostMine(post) {
  return Boolean(post && post.authorId && post.authorId === getCurrentUserId());
}

function getCommunityPost(id) {
  return getSavedPosts().find(function (post) { return post.id === id; });
}

function getOwnedPost(id) {
  return getSavedPosts().find(function (post) { return post.id === id && isPostMine(post); });
}

function getDefaultPost(id) {
  return defaultPosts.find(function (post) { return post.id === id; });
}

function withDynamicDefaultPost(post) {
  const createdAt = new Date(Date.now() - 44 * 60000);
  return Object.assign({}, post, { createdAt: createdAt.toISOString(), expiresAt: getNextDawnDeadline().toISOString() });
}

function getPostById(id) {
  const communityPost = getCommunityPost(id);
  const defaultPost = getDefaultPost(id);
  if (communityPost) return communityPost;
  if (defaultPost) return withDynamicDefaultPost(defaultPost);
  return null;
}

function isOwnedId(id) {
  return isPostMine(getCommunityPost(id));
}

function getReactionStore() { return readJson(REACTION_KEY, {}); }
function saveReactionStore(store) { writeJson(REACTION_KEY, store); }
function getCommentStore() { return readJson(COMMENT_KEY, {}); }
function saveCommentStore(store) { writeJson(COMMENT_KEY, store); }

function normalizeCounts(baseCounts, savedCounts) {
  const counts = {};
  reactionTypes.forEach(function (type, index) {
    const base = baseCounts && typeof baseCounts === "object" ? baseCounts[type] : baseCounts && baseCounts[index];
    counts[type] = Number(savedCounts && savedCounts[type] != null ? savedCounts[type] : base || 0);
  });
  return counts;
}

function normalizeSelected(selected) {
  if (!selected) return {};
  if (typeof selected === "string") return selected ? { [selected]: true } : {};
  const normalized = {};
  reactionTypes.forEach(function (type) { if (selected[type]) normalized[type] = true; });
  return normalized;
}

function getPostReactions(id) {
  const post = getPostById(id);
  const store = getReactionStore();
  const saved = store[id] || {};
  return { counts: normalizeCounts(post && post.reactions, saved.counts), selected: normalizeSelected(saved.selected) };
}

function savePostReaction(id, type) {
  const store = getReactionStore();
  const current = getPostReactions(id);
  if (!reactionTypes.includes(type)) return;
  if (current.selected[type]) {
    current.counts[type] = Math.max(0, Number(current.counts[type] || 0) - 1);
    delete current.selected[type];
  } else {
    current.counts[type] = Number(current.counts[type] || 0) + 1;
    current.selected[type] = true;
  }
  store[id] = current;
  saveReactionStore(store);
}

function getPostComments(id) {
  const store = getCommentStore();
  if (store[id]) return store[id];
  return isOwnedId(id) ? [] : defaultComments.slice();
}

function addPostComment(id, body) {
  const store = getCommentStore();
  const comments = getPostComments(id);
  comments.push({ author: "익명의 곁 나 · 방금", body: body, createdAt: new Date().toISOString() });
  store[id] = comments;
  saveCommentStore(store);
}

function applyCountdownSource(item, post) {
  item.dataset.minutesLeft = String(getRemainingMinutes(post));
  item.dataset.expiresAt = new Date(getPostExpiresAt(post)).toISOString();
}

function setupCountdowns() {
  const countdownItems = document.querySelectorAll("[data-countdown]");
  if (!countdownItems.length) return;
  countdownItems.forEach(function (item) {
    const savedExpiresAt = Date.parse(item.dataset.expiresAt || "");
    const minutesLeft = Number(item.dataset.minutesLeft || "0");
    const deadline = Number.isFinite(savedExpiresAt) ? new Date(savedExpiresAt) : new Date(Date.now() + minutesLeft * 60000);
    item.dataset.deadline = String(deadline.getTime());
  });
  function updateCountdowns() {
    countdownItems.forEach(function (item) {
      const deadline = Number(item.dataset.deadline || "0");
      const minutesLeft = Math.max(0, Math.ceil((deadline - Date.now()) / 60000));
      const prefix = item.dataset.countdownPrefix || "";
      const suffix = item.dataset.countdownSuffix || "";
      let remaining = formatRemaining(minutesLeft, item.hasAttribute("data-countdown-short"));
      if (item.dataset.countdownFormat === "clock") remaining = formatClockRemaining(minutesLeft);
      item.textContent = prefix + remaining + suffix;
    });
  }
  updateCountdowns();
  window.setInterval(updateCountdowns, 60000);
}

function setupEmotionInput() {
  const emotionInput = document.querySelector("[data-emotion-input]");
  const emotionCount = document.querySelector("[data-emotion-count]");
  const composeNext = document.querySelector(".compose-next");
  if (emotionInput && emotionCount) {
    emotionInput.value = "";
    emotionCount.textContent = "0";
    emotionInput.addEventListener("input", function () {
      emotionCount.textContent = String(emotionInput.value.length);
    });
  }
  if (composeNext && emotionInput) {
    composeNext.addEventListener("click", function (event) {
      const copy = emotionInput.value.trim();
      if (!copy) { event.preventDefault(); emotionInput.focus(); return; }
      writeJson(DRAFT_KEY, { copy: copy, updatedAt: new Date().toISOString() });
    });
  }
}

function setupFirewoodOptions() {
  const options = document.querySelectorAll("[data-firewood-option]");
  const caption = document.querySelector(".campfire figcaption");

  if (!options.length) return;

  options.forEach(function (option) {
    option.addEventListener("click", function (event) {
      event.preventDefault();
      const duration = option.dataset.duration || "dawn";

      options.forEach(function (o) {
        o.classList.remove("is-selected");
        o.removeAttribute("aria-current");
      });
      option.classList.add("is-selected");
      option.setAttribute("aria-current", "true");

      if (caption) {
        caption.textContent = (durationMeta[duration] || durationMeta.dawn).title;
      }

      const durationInput = document.getElementById("selected-duration");
      if (durationInput) durationInput.value = duration;
    });
  });
}

function setupDetailPost() {
  const detailScreen = document.querySelector(".tonight-detail-screen");
  const id = getCurrentPostId();
  const post = getPostById(id);
  if (!detailScreen || !post) {
    if (detailScreen) window.location.replace(getSimyaRoute("tonightIndex"));
    return;
  }
  const isMine = isOwnedId(id);
  const topTitle = document.querySelector(".tonight-detail-topbar h1");
  const topSubtitle = document.querySelector(".tonight-detail-topbar p");
  const author = document.querySelector("[data-detail-author], .td-post-meta");
  const burn = document.querySelector(".td-post-burn");
  const copy = document.querySelector("[data-detail-copy], .td-post-copy");
  const note = document.querySelector(".td-post-note");
  const left = document.querySelector("[data-countdown]");
  const more = document.querySelector("[data-owner-menu-toggle]");
  const reactionState = getPostReactions(id);
  detailScreen.classList.toggle("is-mine-detail", isMine);
  if (topTitle && !document.querySelector(".tonight-edit-screen")) topTitle.textContent = isMine ? "내가 남긴 밤" : "밤의 기록";
  if (topSubtitle && !document.querySelector(".tonight-edit-screen")) topSubtitle.textContent = isMine ? "아직 머무는 중" : "곁에 머무는 글";
  if (author) author.textContent = (isMine ? "내가 남긴 밤" : post.author) + " · " + formatPostTime(post);
  if (burn) burn.textContent = (durationMeta[post.duration] || durationMeta.dawn).label;
  if (copy) copy.textContent = post.detailCopy || post.copy;
  if (note) note.textContent = isMine ? "아직 커뮤니티에 머무는 중이에요" : "말없이 곁에 머무를 수 있어요";
  if (left) applyCountdownSource(left, post);
  if (more) more.hidden = !isMine;
  document.querySelectorAll("[data-reaction-count]").forEach(function (count) {
    count.textContent = String(reactionState.counts[count.dataset.reactionCount] || 0);
  });
  document.querySelectorAll("[data-reaction-chip-view]").forEach(function (chip) {
    chip.href = getPostRoute("tonightReaction", id);
    chip.classList.toggle("is-selected", Boolean(reactionState.selected[chip.dataset.reactionType]));
  });
  document.querySelectorAll(".td-comments-more").forEach(function (item) { item.href = getPostRoute("tonightComments", id); });
  document.querySelectorAll(".tonight-detail-back").forEach(function (link) {
    if (link.getAttribute("href") === "detail.html" || link.getAttribute("href") === getSimyaRoute("tonightDetail")) {
      link.href = getPostRoute("tonightDetail", id);
    }
  });
}

function setupOwnerMenu() {
  const id = getCurrentPostId();
  const toggle = document.querySelector("[data-owner-menu-toggle]");
  const menu = document.querySelector("[data-owner-menu]");
  const edit = document.querySelector("[data-owner-edit]");
  const deleteButton = document.querySelector("[data-owner-delete]");
  const modal = document.querySelector("[data-delete-modal]");
  const cancel = document.querySelector("[data-delete-cancel]");
  const confirm = document.querySelector("[data-delete-confirm]");
  if (edit) edit.href = getPostRoute("tonightEdit", id);
  if (toggle && menu) toggle.addEventListener("click", function () { menu.hidden = !menu.hidden; });
  if (deleteButton && modal) deleteButton.addEventListener("click", function () { menu.hidden = true; modal.hidden = false; });
  if (cancel && modal) cancel.addEventListener("click", function () { modal.hidden = true; });
  if (confirm) {
    confirm.addEventListener("click", function () {
      deletePost(id);
      if (!modal) { window.location.href = getSimyaRoute("tonightIndex"); return; }
      const modalPanel = modal.querySelector(".td-delete-modal");
      const title = modal.querySelector("#delete-title");
      if (modalPanel) modalPanel.classList.add("is-complete");
      if (title) title.textContent = "글이 삭제 되었습니다";
      modal.hidden = false;
      window.setTimeout(function () { window.location.href = getSimyaRoute("tonightIndex"); }, 1200);
    });
  }
}

function setupComments() {
  const id = getCurrentPostId();
  const comments = getPostComments(id);
  const commentSection = document.querySelector(".td-comments");
  const form = document.querySelector(".td-comment-input");
  const input = form ? form.querySelector("input") : null;
  const submit = form ? form.querySelector("button") : null;
  const isMine = isOwnedId(id);
  if (commentSection) {
    const title = commentSection.querySelector("h2");
    const more = commentSection.querySelector(".td-comments-more");
    commentSection.querySelectorAll(".td-comment").forEach(function (comment) { comment.remove(); });
    if (title) title.textContent = "곁에 남긴 말 " + comments.length;
    if (more) { more.href = getPostRoute("tonightComments", id); more.hidden = comments.length < 3; }
    comments.forEach(function (comment, index) {
      const article = document.createElement("article");
      article.className = "td-comment";
      article.style.top = 34 + index * 74 + "px";
      article.innerHTML = '<div class="tonight-detail-avatar td-avatar-small" aria-hidden="true"></div><h3></h3><p></p>';
      article.querySelector("h3").textContent = comment.author;
      article.querySelector("p").textContent = comment.body;
      commentSection.appendChild(article);
    });
  }
  if (form && input) {
    form.action = getPostRoute("tonightDetail", id);
    input.value = "";
    if (isMine) {
      form.classList.add("is-disabled");
      input.placeholder = "내 글에는 답장을 남길 수 없어요";
      input.disabled = true;
      if (submit) submit.disabled = true;
      return;
    }
    input.placeholder = input.getAttribute("placeholder") || "조용히 한마디 남기기";
    form.addEventListener("submit", function (event) {
      const body = input.value.trim();
      event.preventDefault();
      if (!body) { input.focus(); return; }
      addPostComment(id, body);
      window.location.href = getPostRoute("tonightDetail", id);
    });
  }
}

function setupReactionSelection() {
  const id = getCurrentPostId();
  const reactionState = getPostReactions(id);
  document.querySelectorAll("[data-reaction-option]").forEach(function (option) {
    const type = option.dataset.reactionOption;
    const selected = Boolean(reactionState.selected[type]);
    let selectedLabel = option.querySelector("em");
    option.href = getPostRoute("tonightDetail", id);
    option.classList.toggle("is-selected", selected);
    if (selected && !selectedLabel) { selectedLabel = document.createElement("em"); selectedLabel.textContent = "선택됨"; option.appendChild(selectedLabel); }
    if (!selected && selectedLabel) selectedLabel.remove();
    option.addEventListener("click", function (event) {
      event.preventDefault();
      savePostReaction(id, type);
      window.location.href = getPostRoute("tonightDetail", id);
    });
  });
}

function setupEditPage() {
  const form = document.querySelector(".td-edit-form");
  const id = getCurrentPostId();
  if (!form || !id) return;
  const textarea = document.querySelector("[data-edit-textarea]");
  const count = document.querySelector("[data-edit-count]");
  const cancel = document.querySelector("[data-edit-cancel]");
  const duration = document.querySelector("[data-edit-duration]");
  const post = getOwnedPost(id);
  if (!form) return;
  if (!post) { window.location.replace(getSimyaRoute("tonightIndex")); return; }
  const countdown = document.querySelector("[data-countdown]");
  if (countdown) applyCountdownSource(countdown, post);
  if (textarea) textarea.value = post.copy || "";
  if (duration) duration.textContent = (durationMeta[post.duration] || durationMeta.dawn).label;
  if (cancel) cancel.href = getPostRoute("tonightDetail", id);
  function updateCount() { if (count && textarea) count.textContent = String(textarea.value.length); }
  updateCount();
  if (textarea) textarea.addEventListener("input", updateCount);
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    updatePost(id, { copy: textarea.value.trim() || textarea.value });
    window.location.href = getPostRoute("tonightDetail", id);
  });
}

document.addEventListener("DOMContentLoaded", function () {
  const cards = document.querySelectorAll(".hub-feed-card");
  cards.forEach(function (card, index) {
  });
});

getSavedPosts();
// setupHub();
setupEmotionInput();
setupFirewoodOptions();
// setupDetailPost();
// setupOwnerMenu();
// setupComments();
// setupReactionSelection();
// setupEditPage();
setupCountdowns();