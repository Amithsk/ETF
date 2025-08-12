document.addEventListener("DOMContentLoaded", function () {
  // ===== TILE CLICK HANDLING =====
  const tiles = document.querySelectorAll(".tile-card");
  const sections = document.querySelectorAll("main section");

  tiles.forEach(tile => {
    tile.addEventListener("click", function () {
      const targetId = this.dataset.target;

      // Hide all sections
      sections.forEach(sec => sec.classList.add("d-none"));

      // Show target section
      const targetSection = document.getElementById(targetId);
      if (targetSection) {
        targetSection.classList.remove("d-none");
      }

      // Scroll into view for better UX
      targetSection.scrollIntoView({ behavior: "smooth" });
    });
  });

  // ===== ETF CARD CLICK HANDLING =====
  const etfCards = document.querySelectorAll(".etf-card");
  const modal = new bootstrap.Modal(document.getElementById("etfDetailModal"));

  etfCards.forEach(card => {
    card.addEventListener("click", function () {
      const etfId = this.dataset.etfId;
      document.getElementById("etfDetailTitle").innerText = this.dataset.etfName;

      // Summary
      document.getElementById("etf-summary").innerHTML = `
        <p><strong>Fundhouse:</strong> ${this.dataset.etfFundhouse}</p>
        <p><strong>Category:</strong> ${this.dataset.etfCategory}</p>
        <p><strong>Last Price:</strong> ₹${this.dataset.etfPrice}</p>
        <p><strong>Latest AUM:</strong> ₹${this.dataset.etfAum}</p>
        <p><strong>Latest Expense Ratio:</strong> ${this.dataset.etfExpense}%</p>
        <p><strong>Tracking Error (SL):</strong> ${this.dataset.etfTeSl}</p>
      `;

      // History data from preloaded variable
      if (window.etfDataHistory && window.etfDataHistory[etfId]) {
        const history = window.etfDataHistory[etfId];

        document.getElementById("etf-aum-history").innerHTML =
          history.aum.map(x => `${x.month} ${x.year}: ₹${x.aum}`).join("<br>");

        document.getElementById("etf-expense-history").innerHTML =
          history.expense.map(x => `${x.month} ${x.year}: ${x.value}%`).join("<br>");

        let teHTML = "";
        for (let tp in history.te) {
          teHTML += `<strong>${tp}</strong><br>` +
            history.te[tp].map(x => `${x.month} ${x.year}: ${x.value}`).join("<br>") + "<br>";
        }
        document.getElementById("etf-te-history").innerHTML = teHTML;
      }

      modal.show();
    });
  });
});
