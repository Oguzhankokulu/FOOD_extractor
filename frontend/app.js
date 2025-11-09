// Configuration
const API_URL = 'http://localhost:8000';

// Elements
const toggleTipsBtn = document.getElementById('toggleTipsBtn');
const photoTips = document.getElementById('photoTips');
const cameraBtn = document.getElementById('cameraBtn');
const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const cameraSection = document.getElementById('cameraSection');
const video = document.getElementById('video');
const captureBtn = document.getElementById('captureBtn');
const closeCameraBtn = document.getElementById('closeCameraBtn');
const canvas = document.getElementById('canvas');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const processBtn = document.getElementById('processBtn');
const loading = document.getElementById('loading');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');
const resetBtn = document.getElementById('resetBtn');
const errorResetBtn = document.getElementById('errorResetBtn');
const toggleJsonBtn = document.getElementById('toggleJsonBtn');
const jsonResult = document.getElementById('jsonResult');

// State
let currentStream = null;
let currentImageBlob = null;

// Event Listeners
toggleTipsBtn.addEventListener('click', toggleTips);
cameraBtn.addEventListener('click', openCamera);
uploadBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
captureBtn.addEventListener('click', capturePhoto);
closeCameraBtn.addEventListener('click', closeCamera);
processBtn.addEventListener('click', processImage);
resetBtn.addEventListener('click', reset);
errorResetBtn.addEventListener('click', reset);
toggleJsonBtn.addEventListener('click', toggleJson);

// Functions
function toggleTips() {
    if (photoTips.style.display === 'none') {
        photoTips.style.display = 'block';
        toggleTipsBtn.textContent = '📸 Hide Photo Tips';
    } else {
        photoTips.style.display = 'none';
        toggleTipsBtn.textContent = '📸 Show Photo Tips';
    }
}

async function openCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' } // Prefer back camera on mobile
        });
        
        currentStream = stream;
        video.srcObject = stream;
        cameraSection.style.display = 'block';
        imagePreview.style.display = 'none';
        
    } catch (error) {
        showError('Could not access camera: ' + error.message);
    }
}

function closeCamera() {
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
        currentStream = null;
    }
    cameraSection.style.display = 'none';
}

function capturePhoto() {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);
    
    canvas.toBlob((blob) => {
        currentImageBlob = blob;
        const url = URL.createObjectURL(blob);
        previewImg.src = url;
        imagePreview.style.display = 'block';
        closeCamera();
    }, 'image/jpeg', 0.9);
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        if (!file.type.startsWith('image/')) {
            showError('Please select an image file');
            return;
        }
        
        currentImageBlob = file;
        const url = URL.createObjectURL(file);
        previewImg.src = url;
        imagePreview.style.display = 'block';
        closeCamera();
    }
}

async function processImage() {
    if (!currentImageBlob) {
        showError('No image selected');
        return;
    }
    
    // Hide other sections
    imagePreview.style.display = 'none';
    errorSection.style.display = 'none';
    resultsSection.style.display = 'none';
    
    // Show loading
    loading.style.display = 'block';
    
    try {
        // Create form data
        const formData = new FormData();
        formData.append('file', currentImageBlob, 'image.jpg');
        
        // Send to API
        const response = await fetch(`${API_URL}/upload-image`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Server error');
        }
        
        const result = await response.json();
        
        // Hide loading
        loading.style.display = 'none';
        
        // Display results
        displayResults(result);
        
    } catch (error) {
        loading.style.display = 'none';
        showError('Failed to process image: ' + error.message);
    }
}

function displayResults(result) {
    if (!result.success) {
        showError(result.message || 'Failed to extract data from image');
        return;
    }
    
    const data = result.data;
    
    // Add method badge (barcode or OCR)
    const methodBadge = result.method === 'barcode' 
        ? '<span class="badge badge-barcode">📊 From Barcode</span>'
        : '<span class="badge badge-ocr">🔍 From OCR</span>';
    
    // Add product name if available (from barcode)
    let productHeader = '';
    if (data.product_name) {
        productHeader = `
            <div class="product-header">
                <h2>${data.product_name}</h2>
                ${data.brands ? `<p class="brands">${data.brands}</p>` : ''}
                ${methodBadge}
            </div>
        `;
    } else {
        productHeader = `<div class="method-badge">${methodBadge}</div>`;
    }
    
    // Insert product header before results
    const resultsSection = document.getElementById('resultsSection');
    const existingHeader = resultsSection.querySelector('.product-header, .method-badge');
    if (existingHeader) {
        existingHeader.remove();
    }
    resultsSection.querySelector('h2').insertAdjacentHTML('afterend', productHeader);
    
    // Display calories
    const caloriesDiv = document.getElementById('caloriesResult');
    if (data.calories && data.calories.found) {
        let caloriesHTML = `
            <span class="value">${data.calories.value}</span> 
            <span class="unit">${data.calories.unit}</span>
        `;
        if (data.calories.value_serving) {
            caloriesHTML += `<p class="serving-info">Per serving: ${data.calories.value_serving} ${data.calories.unit}</p>`;
        }
        caloriesDiv.innerHTML = caloriesHTML;
    } else {
        caloriesDiv.innerHTML = '<p class="no-data">Not found</p>';
    }
    
    // Display serving size
    const servingSizeDiv = document.getElementById('servingSizeResult');
    if (data.serving_size && data.serving_size.found) {
        servingSizeDiv.innerHTML = `<p class="value">${data.serving_size.value}</p>`;
    } else {
        servingSizeDiv.innerHTML = '<p class="no-data">Not found</p>';
    }
    
    // Display ingredients
    const ingredientsDiv = document.getElementById('ingredientsResult');
    if (data.ingredients && data.ingredients.found && data.ingredients.list.length > 0) {
        const ingredientsList = data.ingredients.list
            .map(ing => `<li>${ing}</li>`)
            .join('');
        ingredientsDiv.innerHTML = `<ul class="ingredient-list">${ingredientsList}</ul>`;
    } else {
        ingredientsDiv.innerHTML = '<p class="no-data">Not found</p>';
    }
    
    // Display nutrition facts
    const nutritionDiv = document.getElementById('nutritionResult');
    if (data.nutrition_facts && Object.keys(data.nutrition_facts).length > 0) {
        let nutritionHTML = '<table class="nutrition-table">';
        for (const [key, value] of Object.entries(data.nutrition_facts)) {
            const displayName = key.charAt(0).toUpperCase() + key.slice(1);
            nutritionHTML += `
                <tr>
                    <td>${displayName}</td>
                    <td>${value.value} ${value.unit}</td>
                </tr>
            `;
        }
        nutritionHTML += '</table>';
        nutritionDiv.innerHTML = nutritionHTML;
    } else {
        nutritionDiv.innerHTML = '<p class="no-data">Not found</p>';
    }
    
    // Display allergens
    const allergensDiv = document.getElementById('allergensResult');
    if (data.allergens && data.allergens.found && data.allergens.list.length > 0) {
        const allergensList = data.allergens.list
            .map(allergen => `<li>${allergen}</li>`)
            .join('');
        allergensDiv.innerHTML = `<ul class="allergen-list">${allergensList}</ul>`;
    } else {
        allergensDiv.innerHTML = '<p class="no-data">None detected</p>';
    }
    
    // Display raw JSON
    jsonResult.textContent = JSON.stringify(result, null, 2);
    
    // Show results section
    resultsSection.style.display = 'block';
}

function showError(message) {
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    imagePreview.style.display = 'none';
    resultsSection.style.display = 'none';
}

function reset() {
    // Reset state
    currentImageBlob = null;
    fileInput.value = '';
    
    // Hide all sections
    imagePreview.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    loading.style.display = 'none';
    jsonResult.style.display = 'none';
    toggleJsonBtn.textContent = 'Show JSON';
    
    // Close camera if open
    closeCamera();
}

function toggleJson() {
    if (jsonResult.style.display === 'none') {
        jsonResult.style.display = 'block';
        toggleJsonBtn.textContent = 'Hide JSON';
    } else {
        jsonResult.style.display = 'none';
        toggleJsonBtn.textContent = 'Show JSON';
    }
}

// Check API health on load
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_URL}/`);
        if (!response.ok) {
            console.warn('API server may not be running');
        }
    } catch (error) {
        console.warn('Could not connect to API server. Make sure it is running on', API_URL);
    }
}

// Initialize
checkAPIHealth();
