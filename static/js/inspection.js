// ==========================================================================
// OnionVision AI - Inspection Controller (Camera, Upload, Demo Samples)
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const dropzoneArea = document.getElementById("dropzoneArea");
    const imageInput = document.getElementById("imageInput");
    const browseBtn = document.getElementById("browseBtn");
    const cameraBtn = document.getElementById("cameraBtn");
    const cameraSection = document.getElementById("cameraSection");
    const cameraVideo = document.getElementById("cameraVideo");
    const cameraCanvas = document.getElementById("cameraCanvas");
    const cameraSelect = document.getElementById("cameraSelect");
    const captureBtn = document.getElementById("captureBtn");
    const timerSnapBtn = document.getElementById("timerSnapBtn");
    const closeCameraBtn = document.getElementById("closeCameraBtn");
    const cameraCountdown = document.getElementById("cameraCountdown");
    const previewSection = document.getElementById("previewSection");
    const imagePreview = document.getElementById("imagePreview");
    const removeImageBtn = document.getElementById("removeImageBtn");
    const analyzeBtn = document.getElementById("analyzeBtn");
    const loadingSection = document.getElementById("loadingSection");
    const alertBox = document.getElementById("alertBox");
    const sampleCards = document.querySelectorAll(".sample-card");

    let currentFile = null;
    let cameraStream = null;

    // Synthesized Audio Shutter Effect using Web Audio API
    function playShutterSound() {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = "sine";
            osc.frequency.setValueAtTime(800, ctx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(200, ctx.currentTime + 0.08);
            gain.gain.setValueAtTime(0.3, ctx.currentTime);
            gain.gain.linearRampToValueAtTime(0.01, ctx.currentTime + 0.08);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.08);
        } catch (e) {
            // Audio context not allowed or unsupported
        }
    }

    // Browse Button
    browseBtn.addEventListener("click", () => imageInput.click());

    // File Input Changed
    imageInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            handleFileSelection(e.target.files[0]);
        }
    });

    // Drag & Drop Handlers
    dropzoneArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzoneArea.classList.add("dragover");
    });

    dropzoneArea.addEventListener("dragleave", () => {
        dropzoneArea.classList.remove("dragover");
    });

    dropzoneArea.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzoneArea.classList.remove("dragover");
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFileSelection(e.dataTransfer.files[0]);
        }
    });

    // Clipboard Paste Support
    document.addEventListener("paste", (e) => {
        const items = (e.clipboardData || e.originalEvent.clipboardData).items;
        for (let item of items) {
            if (item.kind === "file" && item.type.startsWith("image/")) {
                const blob = item.getAsFile();
                handleFileSelection(blob);
                break;
            }
        }
    });

    // Demo Sample Picker
    sampleCards.forEach(card => {
        card.addEventListener("click", async () => {
            sampleCards.forEach(c => c.classList.remove("selected"));
            card.classList.add("selected");
            const sampleName = card.getAttribute("data-sample");
            const imgPath = `/static/demo/${sampleName}`;
            
            try {
                showAlert("Loading sample image...", "info");
                const response = await fetch(imgPath);
                const blob = await response.blob();
                const file = new File([blob], sampleName, { type: blob.type || "image/jpeg" });
                handleFileSelection(file);
                hideAlert();
            } catch (err) {
                showAlert("Failed to load sample image: " + err.message, "danger");
            }
        });
    });

    // File Handler
    function handleFileSelection(file) {
        const validTypes = ["image/jpeg", "image/png", "image/webp", "image/jpg"];
        if (!validTypes.includes(file.type)) {
            showAlert("Invalid file format. Please upload JPG, PNG, or WEBP.", "danger");
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            showAlert("File is too large. Maximum size allowed is 10MB.", "danger");
            return;
        }

        currentFile = file;
        hideAlert();

        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            dropzoneArea.classList.add("d-none");
            cameraSection.classList.add("d-none");
            stopCamera();
            previewSection.classList.remove("d-none");
        };
        reader.readAsDataURL(file);
    }

    // Remove Image
    removeImageBtn.addEventListener("click", () => {
        currentFile = null;
        imageInput.value = "";
        imagePreview.src = "";
        previewSection.classList.add("d-none");
        dropzoneArea.classList.remove("d-none");
        sampleCards.forEach(c => c.classList.remove("selected"));
        hideAlert();
    });

    // Camera Support
    cameraBtn.addEventListener("click", async () => {
        dropzoneArea.classList.add("d-none");
        previewSection.classList.add("d-none");
        cameraSection.classList.remove("d-none");
        await startCamera();
    });

    closeCameraBtn.addEventListener("click", () => {
        stopCamera();
        cameraSection.classList.add("d-none");
        dropzoneArea.classList.remove("d-none");
    });

    cameraSelect.addEventListener("change", async () => {
        stopCamera();
        await startCamera();
    });

    async function startCamera() {
        try {
            const facingMode = cameraSelect ? cameraSelect.value : "environment";
            const constraints = {
                video: {
                    facingMode: facingMode,
                    width: { ideal: 1920 },
                    height: { ideal: 1080 }
                },
                audio: false
            };
            cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
            cameraVideo.srcObject = cameraStream;
        } catch (err) {
            showAlert("Unable to access camera: " + err.message + ". Please ensure camera permissions are allowed.", "danger");
            cameraSection.classList.add("d-none");
            dropzoneArea.classList.remove("d-none");
        }
    }

    function stopCamera() {
        if (cameraStream) {
            cameraStream.getTracks().forEach(track => track.stop());
            cameraStream = null;
        }
    }

    // Capture Snapshot
    captureBtn.addEventListener("click", () => {
        snapFromCamera();
    });

    // 3s Timer Snap
    timerSnapBtn.addEventListener("click", () => {
        let count = 3;
        cameraCountdown.textContent = count;
        cameraCountdown.classList.remove("d-none");

        const interval = setInterval(() => {
            count--;
            if (count > 0) {
                cameraCountdown.textContent = count;
            } else {
                clearInterval(interval);
                cameraCountdown.classList.add("d-none");
                snapFromCamera();
            }
        }, 1000);
    });

    function snapFromCamera() {
        playShutterSound();
        cameraCanvas.width = cameraVideo.videoWidth || 1280;
        cameraCanvas.height = cameraVideo.videoHeight || 720;
        const ctx = cameraCanvas.getContext("2d");
        ctx.drawImage(cameraVideo, 0, 0, cameraCanvas.width, cameraCanvas.height);

        cameraCanvas.toBlob((blob) => {
            const file = new File([blob], `camera_snap_${Date.now()}.jpg`, { type: "image/jpeg" });
            handleFileSelection(file);
        }, "image/jpeg", 0.95);
    }

    // Analyze Button Click (API Request)
    analyzeBtn.addEventListener("click", async () => {
        if (!currentFile) {
            showAlert("Please select or capture an image first.", "warning");
            return;
        }

        previewSection.classList.add("d-none");
        loadingSection.classList.remove("d-none");
        hideAlert();

        const formData = new FormData();
        formData.append("image", currentFile);

        try {
            const response = await fetch("/api/analyze", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || "Quality inspection failed");
            }

            // Redirect to results page
            const targetUrl = data.redirect_url || `/results/${data.id}`;
            window.location.href = targetUrl;
        } catch (err) {
            loadingSection.classList.add("d-none");
            previewSection.classList.remove("d-none");
            showAlert("Inspection error: " + err.message, "danger");
        }
    });

    // Helper: Show Alert
    function showAlert(msg, type = "info") {
        alertBox.className = `alert alert-${type} rounded-3`;
        alertBox.innerHTML = `<i class="bi bi-info-circle-fill me-2"></i> ${msg}`;
        alertBox.classList.remove("d-none");
    }

    function hideAlert() {
        alertBox.classList.add("d-none");
    }
});
