// etf_site.js

document.addEventListener("DOMContentLoaded", () => {
  // Theme toggle
  const themeBtn = document.getElementById("theme-toggle");
  themeBtn?.addEventListener("click", () => {
    document.body.classList.toggle("bg-dark");
    document.body.classList.toggle("text-white");

    const icon = themeBtn.querySelector("i");
    icon.classList.toggle("bi-moon-fill");
    icon.classList.toggle("bi-sun-fill");
  });

  // Card clicks reveal sections
  const cards = document.querySelectorAll(".tile-card");
  cards.forEach(card => {
    card.addEventListener("click", () => {
      const target = card.dataset.target;

      ["etf-section", "category-section", "fund-section"].forEach(id => {
        const section = document.getElementById(id);
        if (section) {
          if (id === target) {
            section.classList.remove("d-none");
          } else {
            section.classList.add("d-none");
          }
        }
      });
    });
  });
});
