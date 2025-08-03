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

  
  // Tile click → show relevant section
  document.querySelectorAll(".tile-card").forEach((card) => {
    card.addEventListener("click", () => {
      const target = card.dataset.target;
      document.querySelectorAll("#etf-section, #category-section, #fund-section").forEach((sec) => {
      if (sec.id === target) {
        sec.classList.remove("d-none");
        sec.classList.add("fade-in");
      } else {
        sec.classList.add("d-none");
      }
      });
    });
  });
});
