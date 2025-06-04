import { invoke } from "@tauri-apps/api/tauri";

let isRecording = false;
const button = document.getElementById("toggle-btn");
const bubble = document.getElementById("bubble");
const serviceSelector = document.getElementById("service-selector");
const transcriptionArea = document.getElementById("transcription-area");
const notificationArea = document.getElementById("notification-area");

button.addEventListener("click", async () => {
  console.log("Button clicked. isRecording:", isRecording);
  if (!isRecording) {
    // Currently in "Start" state, initiate recording
    console.log("Attempting to start recording...");
    const selectedService = serviceSelector.value;
    console.log("Selected service:", selectedService);
    const response = await invoke("start_recording", { service: selectedService });
    console.log("Rust response:", response);
    isRecording = true;
    button.innerText = "Stop";
    serviceSelector.disabled = true; // Disable selector while recording
    bubble.innerText = "🎙️ Recording...";
  } else {
    // Currently in "Stop" state, stop recording
    console.log("Attempting to stop recording...");
    const response = await invoke("stop_transcription");
    console.log("Recording stopped:", response);
    isRecording = false;
    button.innerText = "Start";
    serviceSelector.disabled = false; // Re-enable selector
    bubble.innerText = "🎙️ Waiting...";
  }
});

window.__TAURI__.event.listen("transcript", (event) => {
  // Create a new text element for each transcript segment
  const textElement = document.createElement("div");
  textElement.classList.add("transcription-text");
  textElement.innerText = event.payload;

  // Add the element to the transcription area
  transcriptionArea.appendChild(textElement);

  // Remove the element after the animation finishes
  textElement.addEventListener("animationend", () => {
    textElement.remove();
  });

  // Update the bubble with the latest transcription (optional, based on desired behavior)
  // bubble.innerText = event.payload;
});

// Listen for notification events from the backend
window.__TAURI__.event.listen("notification", (event) => {
  const message = event.payload;
  console.log("Notification received:", message);

  // Create a new notification element
  const notificationElement = document.createElement("div");
  notificationElement.classList.add("notification-message");
  notificationElement.innerText = message;

  // Add the notification to the area
  notificationArea.appendChild(notificationElement);

  // Remove the notification after its animation ends
  notificationElement.addEventListener("animationend", () => {
    notificationElement.remove();
  });
});
