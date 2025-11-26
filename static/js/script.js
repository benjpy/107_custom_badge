document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('customizer-form');
    const generateBtn = document.getElementById('generate-btn');
    const previewImage = document.getElementById('preview-image');
    const placeholderText = document.getElementById('placeholder-text');
    const downloadLink = document.getElementById('download-link');
    const previewContainer = document.getElementById('preview-container');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI Feedback
        const originalBtnText = generateBtn.innerText;
        generateBtn.innerText = 'Generating...';
        generateBtn.disabled = true;

        const formData = new FormData(form);

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            const blob = await response.blob();
            const imageUrl = URL.createObjectURL(blob);

            // Update Preview
            previewImage.src = imageUrl;
            previewImage.style.display = 'block';
            placeholderText.style.display = 'none';
            previewContainer.style.border = 'none'; // Remove dashed border

            // Update Download Link
            downloadLink.href = imageUrl;
            downloadLink.style.display = 'inline-block';

        } catch (error) {
            console.error('Error:', error);
            alert('Failed to generate image: ' + error.message);
        } finally {
            generateBtn.innerText = originalBtnText;
            generateBtn.disabled = false;
        }
    });
});
