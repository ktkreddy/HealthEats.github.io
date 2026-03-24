const API = "/api";

function splitList(raw) {
  if (!raw || !String(raw).trim()) return [];
  return String(raw)
    .split(";")
    .map((s) => s.trim())
    .filter(Boolean);
}

function collectNutrition(form) {
  const order = [
    "Calories",
    "FatContent",
    "SaturatedFatContent",
    "CholesterolContent",
    "SodiumContent",
    "CarbohydrateContent",
    "FiberContent",
    "SugarContent",
    "ProteinContent",
  ];
  return order.map((name) => Number(form.elements[name].value));
}

function renderRecipes(output) {
  const root = document.getElementById("results");
  root.innerHTML = "";
  if (!output || output.length === 0) {
    root.textContent = "No recipes matched those filters. Try relaxing ingredient constraints.";
    return;
  }
  for (const r of output) {
    const el = document.createElement("article");
    el.className = "recipe";
    const ing = (r.RecipeIngredientParts || []).slice(0, 12);
    const steps = (r.RecipeInstructions || []).slice(0, 8);
    el.innerHTML = `
      <h3>${escapeHtml(r.Name)}</h3>
      <p class="meta">Cook ${escapeHtml(String(r.CookTime))} · Prep ${escapeHtml(String(r.PrepTime))} · Total ${escapeHtml(String(r.TotalTime))}</p>
      <p><strong>Calories</strong> ${fmt(r.Calories)} · <strong>Protein</strong> ${fmt(r.ProteinContent)}g</p>
      <details>
        <summary>Ingredients</summary>
        <ul class="compact">${ing.map((i) => `<li>${escapeHtml(i)}</li>`).join("")}</ul>
      </details>
      <details>
        <summary>Instructions</summary>
        <ol class="compact">${steps.map((i) => `<li>${escapeHtml(i)}</li>`).join("")}</ol>
      </details>
    `;
    root.appendChild(el);
  }
}

function fmt(n) {
  if (n == null || Number.isNaN(n)) return "—";
  return Number(n).toFixed(1);
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

document.getElementById("predict-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const status = document.getElementById("status");
  const btn = form.querySelector('button[type="submit"]');
  status.textContent = "Calling API…";
  btn.disabled = true;
  document.getElementById("results").innerHTML = "";

  const nutrition_input = collectNutrition(form);
  const ingredients = splitList(form.elements.include.value);
  const avoidRaw = form.elements.avoid.value;
  const ingredients_to_avoid_txt = splitList(avoidRaw);
  const n_neighbors = Math.min(20, Math.max(1, Number(form.elements.n_neighbors.value) || 5));

  const body = {
    nutrition_input,
    ingredients,
    ingredients_to_avoid_txt,
    params: { n_neighbors, return_distance: false },
  };

  try {
    const res = await fetch(`${API}/predict/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      status.textContent = `Error ${res.status}: ${data.detail ? JSON.stringify(data.detail) : res.statusText}`;
      return;
    }
    status.textContent = `Got ${(data.output && data.output.length) || 0} recipe(s).`;
    renderRecipes(data.output);
  } catch (err) {
    status.textContent = `Request failed: ${err.message || err}`;
  } finally {
    btn.disabled = false;
  }
});
