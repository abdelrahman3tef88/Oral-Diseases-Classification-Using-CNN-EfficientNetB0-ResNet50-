const form = document.getElementById("predictForm");
const imageInput = document.getElementById("imageInput");
const dropZone = document.getElementById("dropZone");
const previewShell = document.getElementById("previewShell");
const imagePreview = document.getElementById("imagePreview");
const clearButton = document.getElementById("clearButton");
const predictButton = document.getElementById("predictButton");
const errorMessage = document.getElementById("errorMessage");
const resultPanel = document.getElementById("resultPanel");
const predictedClass = document.getElementById("predictedClass");
const confidenceScore = document.getElementById("confidenceScore");
const probabilityChart = document.getElementById("probabilityChart");

let selectedFile = null;

function setError(message) {
  errorMessage.textContent = message || "";
}

function setLoading(isLoading) {
  predictButton.disabled = isLoading || !selectedFile;
  predictButton.classList.toggle("is-loading", isLoading);
  predictButton.querySelector(".button-label").textContent = isLoading ? "Predicting" : "Predict";
}

function resetResults() {
  resultPanel.classList.add("is-empty");
  predictedClass.textContent = "-";
  confidenceScore.textContent = "0%";
  probabilityChart.innerHTML = "";
}

function clearSelection() {
  selectedFile = null;
  imageInput.value = "";
  imagePreview.removeAttribute("src");
  previewShell.classList.add("is-hidden");
  predictButton.disabled = true;
  setError("");
  resetResults();
}

function handleFile(file) {
  setError("");

  if (!file) {
    clearSelection();
    return;
  }

  if (!file.type.startsWith("image/")) {
    clearSelection();
    setError("Please select a valid image file.");
    return;
  }

  selectedFile = file;
  const objectUrl = URL.createObjectURL(file);
  imagePreview.onload = () => URL.revokeObjectURL(objectUrl);
  imagePreview.src = objectUrl;
  previewShell.classList.remove("is-hidden");
  predictButton.disabled = false;
  resetResults();
}

function formatPercent(value) {
  const numericValue = Number(value);
  if (Number.isNaN(numericValue)) {
    return "0.00%";
  }
  return `${numericValue.toFixed(2)}%`;
}

function renderProbabilities(predictions) {
  probabilityChart.innerHTML = "";

  Object.entries(predictions)
    .sort(([, a], [, b]) => Number(b) - Number(a))
    .forEach(([className, probability]) => {
      const row = document.createElement("div");
      row.className = "probability-row";

      const label = document.createElement("span");
      label.className = "class-name";
      label.textContent = className;

      const track = document.createElement("div");
      track.className = "bar-track";

      const fill = document.createElement("div");
      fill.className = "bar-fill";
      fill.style.width = `${Math.max(0, Math.min(100, Number(probability)))}%`;

      const value = document.createElement("span");
      value.className = "probability-value";
      value.textContent = formatPercent(probability);

      track.appendChild(fill);
      row.append(label, track, value);
      probabilityChart.appendChild(row);
    });
}

function renderResult(result) {
  predictedClass.textContent = result.predicted_class;
  confidenceScore.textContent = formatPercent(result.confidence);
  renderProbabilities(result.all_predictions || {});
  resultPanel.classList.remove("is-empty");
}

async function submitPrediction(event) {
  event.preventDefault();

  if (!selectedFile) {
    setError("Please choose an image first.");
    return;
  }

  const formData = new FormData();
  formData.append("file", selectedFile);
  setError("");
  setLoading(true);

  try {
    const response = await fetch("/predict", {
      method: "POST",
      body: formData,
    });

    const payload = await response.json().catch(() => null);

    if (!response.ok) {
      const detail = payload?.detail || "Prediction failed. Please try another image.";
      throw new Error(Array.isArray(detail) ? detail.map((item) => item.msg).join(" ") : detail);
    }

    renderResult(payload);
  } catch (error) {
    setError(error.message || "Prediction failed. Please try again.");
  } finally {
    setLoading(false);
  }
}

imageInput.addEventListener("change", (event) => {
  handleFile(event.target.files[0]);
});

clearButton.addEventListener("click", clearSelection);
form.addEventListener("submit", submitPrediction);

["dragenter", "dragover"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add("is-dragging");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove("is-dragging");
  });
});

dropZone.addEventListener("drop", (event) => {
  handleFile(event.dataTransfer.files[0]);
});
