const transportDataEl = document.getElementById("transport-data");
const modeData = transportDataEl ? JSON.parse(transportDataEl.textContent) : {};
const buttons = Array.from(document.querySelectorAll(".tab-btn"));
const tableBody = document.querySelector("#details-table tbody");
const detailTitle = document.getElementById("detail-title");

function renderRows(mode) {
  const rows = modeData[mode] || [];
  detailTitle.textContent = `${mode.charAt(0).toUpperCase() + mode.slice(1)} options`;

  if (!rows.length) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="7">No options available for this transport type.</td>
      </tr>
    `;
    return;
  }

  tableBody.innerHTML = rows
    .map((option) => {
      const status = option.is_valid ? "Meets arrival" : "Late arrival";
      return `
      <tr class="${option.is_valid ? "valid" : "invalid"}">
        <td>${option.service_name}</td>
        <td>${option.departure_time}</td>
        <td>${option.arrival_time}</td>
        <td>${option.duration_min} min</td>
        <td>INR ${option.cost}</td>
        <td>${option.carbon_kg} kg</td>
        <td>${status}</td>
      </tr>
      `;
    })
    .join("");
}

buttons.forEach((button) => {
  button.addEventListener("click", () => {
    buttons.forEach((b) => b.classList.remove("active"));
    button.classList.add("active");
    renderRows(button.dataset.mode);
  });
});

if (buttons.length) {
  buttons[0].classList.add("active");
  renderRows(buttons[0].dataset.mode);
}
