// Theme Toggle
document.addEventListener("DOMContentLoaded", function () {
  const toggleBtn = document.getElementById("theme-toggle");
  const icon = toggleBtn.querySelector("i");

  toggleBtn.addEventListener("click", () => {
    document.body.classList.toggle("light-mode");

    // Icon change
    icon.classList.toggle("bi-moon-fill");
    icon.classList.toggle("bi-sun-fill");
  });

  // Tile click -> toggle sections
  document.querySelectorAll(".tile-card").forEach((tile) => {
    tile.addEventListener("click", () => {
      const targetId = tile.getAttribute("data-target");
      const sections = ["etf-section", "category-section", "list-fund"];

      sections.forEach((id) => {
        const el = document.getElementById(id);
        if (!el) return;
        if (id === targetId) {
          el.classList.toggle("d-none");
          el.classList.add("fade-in");
        } else {
          el.classList.add("d-none");
        }
      });
    });
  });
});
