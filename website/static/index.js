document.addEventListener('DOMContentLoaded', function() {
    const toggleFormBtn = document.getElementById('toggle-form-btn');
    const productForm = document.getElementById('product-form');

    toggleFormBtn.addEventListener('click', function() {
        if (productForm.classList.contains('hidden')) {
            productForm.classList.remove('hidden');
        } else {
            productForm.classList.add('hidden');
        }
    });
});