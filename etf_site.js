// etf_site.js
document.addEventListener("DOMContentLoaded", () => {
  console.log("ETF Dashboard Loaded");

  // Example: Animate counters if you want to show animated totals
  const animateCount = (el, end) => {
    let current = 0;
    const duration = 1000;
    const stepTime = Math.max(Math.floor(duration / end), 10);

    const counter = setInterval(() => {
      current += 1;
      el.textContent = current;
      if (current >= end) {
        clearInterval(counter);
      }
    }, stepTime);
  };

  const totalEtfsEl = document.getElementById("total-etfs");
  const totalCategoriesEl = document.getElementById("total-categories");
  const totalFundsEl = document.getElementById("total-funds");

  if (totalEtfsEl && totalCategoriesEl && totalFundsEl) {
    animateCount(totalEtfsEl, parseInt(totalEtfsEl.dataset.count));
    animateCount(totalCategoriesEl, parseInt(totalCategoriesEl.dataset.count));
    animateCount(totalFundsEl, parseInt(totalFundsEl.dataset.count));
  }

  // Example: Add a theme toggle
  const themeToggle = document.getElementById("theme-toggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      document.documentElement.classList.toggle("dark");
    });
  }
});
