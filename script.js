// Replace with your Render deployed backend URL after deployment
const API_URL = "https://cnn-image-classifier-avinab-9f5fa.containers.snapdeploy.app";

document.getElementById('imageInput').addEventListener('change', function (e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            document.getElementById('imagePreview').src = e.target.result;
            document.getElementById('previewContainer').classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }
});

async function uploadImage() {
    const fileInput = document.getElementById('imageInput');
    if (!fileInput.files[0]) {
        alert("Please select an image first!");
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (response.ok) {
            document.getElementById('resLabel').innerText = data.predicted_label;
            document.getElementById('resConfidence').innerText = data.confidence;
            document.getElementById('result').classList.remove('hidden');
            fetchHistory();
        } else {
            alert("Error: " + data.detail);
        }
    } catch (err) {
        console.error(err);
        alert("Failed to connect to backend server.");
    }
}

async function fetchHistory() {
    try {
        const response = await fetch(`${API_URL}/history`);
        const data = await response.json();
        const historyList = document.getElementById('historyList');
        historyList.innerHTML = '';

        data.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${item.predicted_label}</strong> (${item.confidence}%) - <em>${item.filename}</em>`;
            historyList.appendChild(li);
        });
    } catch (err) {
        console.error("Failed to load history:", err);
    }
}