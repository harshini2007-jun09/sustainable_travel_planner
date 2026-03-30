/**
 * dashboard.js — Renders the full Sustainable Travel Dashboard
 *
 * Sections:
 *   A. Travel option cards
 *   B. Comparison bar charts (Chart.js)
 *   C. Smart recommendation
 *   D. Greener alternatives
 *   F. Trip summary widget
 *   G. Eco add-ons
 */

// ─── Retrieve data stored by home page ──────────────────────────────────────
const rawData = sessionStorage.getItem("tripData");
let tripData  = null;
let selectedMode = null;

if (!rawData) {
  // If no data, redirect home
  window.location.href = "/";
} else {
  tripData = JSON.parse(rawData);
  initDashboard(tripData);
}

// ─── Main init ───────────────────────────────────────────────────────────────
function initDashboard(data) {
  // Hide loader, show dash
  document.getElementById("dashLoading").style.display = "none";
  document.getElementById("dashMain").style.display    = "flex";

  // Nav route
  document.getElementById("navRoute").textContent =
    `${data.source} → ${data.destination}  (${data.distance_km} km)`;

  // Constraint warning
  if (data.constraint_msg) {
    const banner = document.getElementById("constraintBanner");
    document.getElementById("constraintText").textContent = data.constraint_msg;
    banner.style.display = "flex";
  }

  renderOptions(data.options, data.preference);
  renderCharts(data.chart_data);
  renderRecommendation(data.recommendation);
  renderAlternatives(data.alternatives);
  renderSummary(data.summary, data.destination);
  renderAddons(data.eco_addons, data.destination);

  // Route meta
  document.getElementById("routeMeta").textContent =
    `${data.source} → ${data.destination} · ${data.distance_km} km · Preference: ${data.preference}`;
}

// ─── A. Travel option cards ───────────────────────────────────────────────────
function renderOptions(options, preference) {
  const grid = document.getElementById("optionsGrid");
  grid.innerHTML = "";

  options.forEach((opt, idx) => {
    const card = document.createElement("div");
    card.className = "option-card" + (opt.recommended ? " recommended" : "")
                     + (!opt.meets_deadline ? " deadline-miss" : "");
    card.style.animationDelay = `${idx * 0.07}s`;
    card.style.animation = "fadeUp .5s ease both";

    const ecoClass = opt.eco_score.class;
    const deadlineNote = !opt.meets_deadline
      ? `<div style="font-size:.75rem;color:#c0392b;margin-top:6px;">⚠️ Won't meet arrival time</div>` : "";

    card.innerHTML = `
      ${opt.recommended ? '<div class="rec-badge">⭐ Recommended</div>' : ""}
      <span class="card-icon">${opt.icon}</span>
      <div class="card-mode">${opt.label}</div>
      <div class="card-stats">
        <div class="card-stat">
          <span class="stat-key">💰 Cost</span>
          <span class="stat-val">$${opt.cost_usd.toFixed(0)}</span>
        </div>
        <div class="card-stat">
          <span class="stat-key">⏱ Time</span>
          <span class="stat-val">${opt.travel_time_display}</span>
        </div>
        <div class="card-stat">
          <span class="stat-key">🌿 CO₂</span>
          <span class="stat-val">${opt.co2_kg} kg</span>
        </div>
      </div>
      <div class="eco-badge ${ecoClass}">${opt.eco_score.badge} ${opt.eco_score.label} Impact</div>
      ${deadlineNote}
      <button class="btn-select" onclick="selectOption('${opt.mode}', this)">
        Select ${opt.label}
      </button>
    `;
    grid.appendChild(card);
  });
}

// Handle card selection
function selectOption(mode, btn) {
  selectedMode = mode;

  // Visual: reset all, activate clicked
  document.querySelectorAll(".option-card").forEach((c) => c.classList.remove("selected"));
  btn.closest(".option-card").classList.add("selected");

  // Update floating bar
  const opt = tripData.options.find((o) => o.mode === mode);
  if (opt) {
    document.getElementById("selectedBarText").textContent =
      `${opt.icon} ${opt.label} selected — $${opt.cost_usd.toFixed(0)} · ${opt.travel_time_display} · ${opt.co2_kg} kg CO₂`;
    document.getElementById("selectedBar").style.display = "flex";
  }
}

function confirmSelection() {
  if (!selectedMode) return;
  const opt = tripData.options.find((o) => o.mode === selectedMode);
  alert(`✅ Trip confirmed!\n\n${opt.icon} ${opt.label}\n💰 $${opt.cost_usd.toFixed(0)}\n⏱ ${opt.travel_time_display}\n🌿 ${opt.co2_kg} kg CO₂\n\nEnjoy your sustainable journey! 🌍`);
}

// ─── B. Comparison charts ─────────────────────────────────────────────────────
function renderCharts(chartData) {
  const colors = {
    flight: { bg: "rgba(224,122,95,.75)",  border: "#e07a5f" },
    train:  { bg: "rgba(82,183,136,.75)",  border: "#52b788" },
    bus:    { bg: "rgba(232,168,56,.75)",  border: "#e8a838" },
    car:    { bg: "rgba(72,149,239,.75)",  border: "#4895ef" },
  };
  const modes  = ["flight", "train", "bus", "car"];
  const bgColors     = modes.map((m) => colors[m].bg);
  const borderColors = modes.map((m) => colors[m].border);

  const chartConfig = (label, dataArr, unit) => ({
    type: "bar",
    data: {
      labels: chartData.labels,
      datasets: [{
        label: unit,
        data: dataArr,
        backgroundColor: bgColors,
        borderColor: borderColors,
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.parsed.y} ${unit}`,
          },
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { family: "'DM Sans'" } } },
        y: {
          beginAtZero: true,
          grid: { color: "rgba(0,0,0,.06)" },
          ticks: { font: { family: "'DM Sans'" } },
        },
      },
    },
  });

  new Chart(document.getElementById("chartCost"), chartConfig("Cost", chartData.cost, "USD"));
  new Chart(document.getElementById("chartTime"), chartConfig("Hours", chartData.time, "hrs"));
  new Chart(document.getElementById("chartCo2"),  chartConfig("kg CO₂", chartData.co2, "kg CO₂"));
}

// ─── C. Smart recommendation ──────────────────────────────────────────────────
function renderRecommendation(rec) {
  if (!rec || !rec.mode) return;
  const card = document.getElementById("recCard");
  card.innerHTML = `
    <div class="rec-icon-wrap">${rec.icon}</div>
    <div>
      <div class="rec-title">Best Pick: ${rec.label}</div>
      <div class="rec-text">${rec.explanation}</div>
      ${rec.co2_saved > 0
        ? `<span class="rec-savings">🌿 Saves ${rec.co2_saved} kg CO₂ (${rec.co2_pct}%)</span>`
        : ""}
    </div>
  `;
}

// ─── D. Alternatives ─────────────────────────────────────────────────────────
function renderAlternatives(alts) {
  if (!alts || alts.length === 0) {
    document.getElementById("altSection").style.display = "none";
    return;
  }
  const list = document.getElementById("altList");
  list.innerHTML = alts.map((alt) => `
    <div class="alt-item">
      <span class="alt-item-icon">${alt.icon}</span>
      <span class="alt-item-text">${alt.text}</span>
    </div>
  `).join("");
}

// ─── F. Trip summary ──────────────────────────────────────────────────────────
function renderSummary(summary, destination) {
  const grid = document.getElementById("summaryGrid");
  grid.innerHTML = `
    <div class="summary-tile">
      <span class="tile-icon">💰</span>
      <span class="tile-value">$${summary.total_cost.toFixed(0)}</span>
      <span class="tile-label">Total Cost</span>
    </div>
    <div class="summary-tile">
      <span class="tile-icon">🌿</span>
      <span class="tile-value">${summary.total_co2} kg</span>
      <span class="tile-label">CO₂ Emissions</span>
    </div>
    <div class="summary-tile highlight">
      <span class="tile-icon">♻️</span>
      <span class="tile-value">${summary.co2_saved} kg</span>
      <span class="tile-label">CO₂ Saved vs Flight</span>
    </div>
    <div class="summary-tile">
      <span class="tile-icon">⏱</span>
      <span class="tile-value">${summary.travel_time}</span>
      <span class="tile-label">Travel Time</span>
    </div>
    <div class="eco-msg">${summary.eco_message}</div>
  `;
}

// ─── G. Eco add-ons ───────────────────────────────────────────────────────────
function renderAddons(addons, destination) {
  document.getElementById("addonsDestLabel").textContent = `at ${destination}`;
  const grid = document.getElementById("addonsGrid");

  // Column 1: Places
  const placesCol = document.createElement("div");
  placesCol.className = "addon-col";
  placesCol.innerHTML = `<h4>🌿 Eco Places</h4>` +
    addons.places.map((p) => `
      <div class="addon-item">
        <span class="addon-item-icon">${p.icon}</span>
        <div>
          <div class="addon-item-name">${p.name}</div>
          <div class="addon-item-sub">${p.type}</div>
        </div>
      </div>
    `).join("");

  // Column 2: Hotels
  const hotelsCol = document.createElement("div");
  hotelsCol.className = "addon-col";
  hotelsCol.innerHTML = `<h4>🏨 Green Hotels</h4>` +
    addons.hotels.map((h) => `
      <div class="addon-item">
        <span class="addon-item-icon">${h.icon}</span>
        <div>
          <div class="addon-item-name">${h.name} ${h.rating}</div>
          <div class="addon-item-sub">${h.cert}</div>
        </div>
      </div>
    `).join("");

  // Column 3: Local transport
  const transCol = document.createElement("div");
  transCol.className = "addon-col";
  transCol.innerHTML = `<h4>🚶 Local Transport</h4>` +
    addons.local_transport.map((t) => `
      <div class="addon-item">
        <span class="addon-item-icon">${t.icon}</span>
        <div>
          <div class="addon-item-name">${t.mode}</div>
          <div class="addon-item-sub">${t.tip}</div>
        </div>
      </div>
    `).join("");

  grid.appendChild(placesCol);
  grid.appendChild(hotelsCol);
  grid.appendChild(transCol);
}
