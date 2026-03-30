/**
 * home.js — Homepage interactions for Sustainable Travel Planner
 * Handles: preference selection, form validation, API call, redirect
 */

// ─── Animate background leaf particles ──────────────────────────────────────
(function spawnLeaves() {
  const canvas = document.getElementById("bgCanvas");
  const leaves = ["🍃", "🌿", "🍀", "🌱", "🌾"];
  const count = 18;

  for (let i = 0; i < count; i++) {
    const el = document.createElement("span");
    el.className = "leaf-particle";
    el.textContent = leaves[Math.floor(Math.random() * leaves.length)];
    el.style.left = `${Math.random() * 100}%`;
    el.style.animationDuration = `${8 + Math.random() * 14}s`;
    el.style.animationDelay    = `${Math.random() * 12}s`;
    el.style.fontSize = `${0.8 + Math.random() * 1.2}rem`;
    canvas.appendChild(el);
  }
})();

// ─── Preference card selection ───────────────────────────────────────────────
document.querySelectorAll(".pref-card").forEach((card) => {
  card.addEventListener("click", () => {
    // Update active class
    document.querySelectorAll(".pref-card").forEach((c) => c.classList.remove("active"));
    card.classList.add("active");
    // Check the hidden radio
    card.querySelector("input[type=radio]").checked = true;
  });
});

// Set today as default date
const dateInput = document.getElementById("travelDate");
if (dateInput) {
  const today = new Date().toISOString().split("T")[0];
  dateInput.value = today;
  dateInput.min   = today;
}

// ─── Form submission ─────────────────────────────────────────────────────────
function submitForm() {
  const source      = document.getElementById("source").value.trim();
  const destination = document.getElementById("destination").value.trim();
  const travelDate  = document.getElementById("travelDate").value;
  const arrivalTime = document.getElementById("arrivalTime").value;
  const preference  = document.querySelector('input[name="preference"]:checked')?.value || "eco";

  // Validation
  const errorEl = document.getElementById("formError");
  if (!source || !destination) {
    errorEl.textContent = "⚠️ Please enter both source and destination.";
    errorEl.style.display = "block";
    return;
  }
  if (source.toLowerCase() === destination.toLowerCase()) {
    errorEl.textContent = "⚠️ Source and destination cannot be the same.";
    errorEl.style.display = "block";
    return;
  }
  errorEl.style.display = "none";

  // Show loader
  const btn  = document.getElementById("planBtn");
  btn.querySelector(".btn-text").style.display   = "none";
  btn.querySelector(".btn-loader").style.display = "inline";
  btn.disabled = true;

  // POST to Flask backend
  fetch("/plan", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source, destination, travel_date: travelDate, arrival_time: arrivalTime, preference }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        throw new Error(data.error);
      }
      // Store in sessionStorage, redirect to dashboard
      sessionStorage.setItem("tripData", JSON.stringify(data));
      window.location.href = "/dashboard";
    })
    .catch((err) => {
      errorEl.textContent = `⚠️ ${err.message || "Something went wrong. Please try again."}`;
      errorEl.style.display = "block";
      btn.querySelector(".btn-text").style.display   = "inline";
      btn.querySelector(".btn-loader").style.display = "none";
      btn.disabled = false;
    });
}

// Allow Enter key to submit
document.addEventListener("keydown", (e) => {
  if (e.key === "Enter") submitForm();
});
