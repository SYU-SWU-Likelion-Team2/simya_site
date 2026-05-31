/*
 * onboarding.js
 * Description : 온보딩/인증 프론트 상호작용
 * Author       : 배서현
 * Contributors : Codex
 * Created      : 2026-05-23
 * Last Update  : 2026-05-30
 * Revision History
 *   v1.0.0 - 정적 프론트 리소스 제작 (2026-05-23 : 배서현)
 *   v1.1.0 - Figma 기준 UI/상호작용 반영 (2026-05-26 : Codex)
 *   v1.2.0 - Django MTV 연결 준비 및 백엔드 인수인계 주석 정리 (2026-05-30 : Codex)
 */

const SIMYA_ROUTE_FALLBACKS = {
  authLogin: "pages/auth/login.html",
  tonightIndex: "../tonight/index.html",
};

function syncSimyaViewportScale() {
  const viewport = window.visualViewport || window;
  const width = viewport.width || window.innerWidth;
  const height = viewport.height || window.innerHeight;

  const scale = Math.min(width / 390, height / 844, 1);

  document.documentElement.style.setProperty("--simya-scale-x", scale);
  document.documentElement.style.setProperty("--simya-scale-y", scale);
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

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    document.cookie.split(";").forEach(function (cookie) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
      }
    });
  }
  return cookieValue;
}

function updateTime() {
  const now = new Date();
  const timeString =
    String(now.getHours()).padStart(2, "0") +
    ":" +
    String(now.getMinutes()).padStart(2, "0");
  document.querySelectorAll(".time").forEach(function (el) {
    el.textContent = timeString;
  });
}

updateTime();
setInterval(updateTime, 60000);

let currentSlide = 1;
const totalSlides = 4;

function nextSlide() {
  const current = document.getElementById("slide-" + currentSlide);
  if (!current) return;
  current.classList.remove("active");
  currentSlide++;
  if (currentSlide > totalSlides) currentSlide = 1;
  document.getElementById("slide-" + currentSlide).classList.add("active");
}

const startButtons = document.querySelectorAll(".btn-google, .btn-auth-switch");
startButtons.forEach(function (button) {
  button.addEventListener("click", function () {
    window.location.href = getSimyaRoute("authLogin");
  });
});

document.querySelectorAll("[data-toggle-password]").forEach(function (button) {
  button.addEventListener("click", function () {
    const input = button.parentElement.querySelector("input");
    const isHidden = input.type === "password";
    input.type = isHidden ? "text" : "password";
    button.textContent = isHidden ? "보기" : "숨김";
  });
});

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("[data-auth-form]").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      const data = new FormData(form);
      const mode = form.dataset.authMode || "login";

      fetch(mode === "signup" ? "/api/accounts/signup/" : "/api/accounts/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
          username: data.get("loginId"),
          password: data.get("password"),
          nickname: data.get("nickname") || "",
          name: data.get("name") || "",
        }),
      })
        .then((res) => res.json())
        .then((json) => {
          if (json.token) {
            localStorage.setItem("accessToken", json.token.access);
            localStorage.setItem("refreshToken", json.token.refresh);
            window.location.href = getSimyaRoute("tonightIndex");
          } else {
            alert(json.error || "오류가 발생했습니다.");
          }
        })
        .catch(() => alert("서버 연결 실패"));
    });
  });
});