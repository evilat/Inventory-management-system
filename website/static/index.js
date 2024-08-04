document.addEventListener("DOMContentLoaded", () => {
  // Toggle add product form
  const toggleButton = document.getElementById("toggle-form-btn");
  const formContainer = document.getElementById("product-form-container");

  toggleButton.addEventListener("click", () => {
    if (
      formContainer.style.display === "none" ||
      formContainer.style.display === ""
    ) {
      formContainer.style.display = "block";
      toggleButton.textContent = "Cancel";
    } else {
      formContainer.style.display = "none";
      toggleButton.textContent = "Add New Product";
    }
  });
  // Handle edit button click with event delegation
  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("edit-btn")) {
      const productId = e.target.getAttribute("data-product-id");

      // Fetch product data from the server
      fetch(`/get_product/${productId}`)
        .then((response) => response.json())
        .then((data) => {
          // Populate the edit form with the fetched data
          document.getElementById("edit-product-id").value = productId;
          document.getElementById("edit-name").value = data.name;
          document.getElementById("edit-sku").value = data.sku;
          document.getElementById("edit-category").value = data.category;
          document.getElementById("edit-price").value = data.price;
          document.getElementById("edit-quantity").value = data.quantity;
          document.getElementById("edit-supplier").value = data.supplier;
          document.getElementById("edit-description").value = data.description;

          const editFormContainer = document.getElementById(
            "edit-form-container"
          );
          const editForm = document.getElementById("edit-product-form");

          editForm.action = `/edit_product/${productId}`;
          editFormContainer.style.display = "block";
        })
        .catch((error) => console.error("Error:", error));
    }
  });

  // Flash messages duration
  const flashMessages = document.getElementById("flash-messages");

  if (flashMessages) {
    // Start fade-out after 4 seconds, then hide the element
    setTimeout(() => {
      flashMessages.classList.add("fade-out");
    }, 4000); // 4000 milliseconds = 4 seconds

    // Fully hide after the fade-out animation completes (1 second)
    setTimeout(() => {
      flashMessages.style.display = "none";
    }, 5000); // 5000 milliseconds = 5 seconds
  }

  // Delete Product button
  const deleteButtons = document.querySelectorAll(".delete-btn");

  deleteButtons.forEach((button) => {
    button.addEventListener("click", (e) => {
      const productId = e.target.getAttribute("data-product-id");

      console.log("Delete button clicked for product ID:", productId);

      const isConfirmed = confirm(
        "Are you sure you want to delete this product?"
      );

      if (isConfirmed) {
        console.log("User confirmed deletion for product ID:", productId);

        fetch(`/delete_product/${productId}`, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
        })
          .then((response) => response.json())
          .then((data) => {
            console.log("Server response:", data);
            if (data.success) {
              e.target.parentElement.remove();
            } else {
              alert("Failed to delete the product.");
            }
          })
          .catch((error) => {
            console.error("Error:", error);
            alert("An error occurred while deleting the product.");
          });
      }
    });
  });
});
