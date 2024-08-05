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

  // Import CSV File
  document.getElementById("import-csv-btn").addEventListener("click", () => {
    document.getElementById("csv-file").click();
  });

  document.getElementById("csv-file").addEventListener("change", () => {
    document.getElementById("import-csv-form").submit();
  });

  // Handle edit button click with event delegation
  document.addEventListener("click", (e) => {
    let target = e.target;

    // Check if the target is the edit button or an <i> element inside the button
    if (target.classList.contains("edit-btn") || target.closest(".edit-btn")) {
      const editButton = target.closest(".edit-btn");
      const productId = editButton.getAttribute("data-product-id");

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
          toggleButton.textContent = "Cancel";
          formContainer.style.display = "none"; // Hide the add form
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

  // Delete Product button using event delegation for dynamic content
  document.addEventListener("click", (e) => {
    let target = e.target;

    // Check if the target is the delete button or an <i> element inside the button
    if (
      target.classList.contains("delete-btn") ||
      target.closest(".delete-btn")
    ) {
      const deleteButton = target.closest(".delete-btn");
      const productId = deleteButton.getAttribute("data-product-id");

      const isConfirmed = confirm(
        "Are you sure you want to delete this product?"
      );

      if (isConfirmed) {
        fetch(`/delete_product/${productId}`, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.success) {
              e.target.closest(".product-item").remove();
            } else {
              alert("Failed to delete the product.");
            }
          })
          .catch((error) => {
            console.error("Error:", error);
            alert("An error occurred while deleting the product.");
          });
      }
    }
  });

  // Layout toggle functionality
  const layoutSelector = document.getElementById("layout-selector");
  const productList = document.getElementById("product-list");

  // Initialize layout from local storage if it exists
  const savedLayout = localStorage.getItem("layout") || "grid";
  productList.classList.add(`${savedLayout}-layout`);
  layoutSelector.value = savedLayout;

  layoutSelector.addEventListener("change", () => {
    const selectedLayout = layoutSelector.value;
    productList.classList.remove("grid-layout", "list-layout");
    productList.classList.add(`${selectedLayout}-layout`);
    localStorage.setItem("layout", selectedLayout);
  });

  // Filter products by price and search term
  const minPriceInput = document.getElementById("min-price");
  const maxPriceInput = document.getElementById("max-price");
  const searchInput = document.getElementById("product-search");

  function filterProducts() {
    const minPrice = parseFloat(minPriceInput.value) || 0;
    const maxPrice = parseFloat(maxPriceInput.value) || Infinity;
    const query = searchInput.value.toLowerCase();

    document.querySelectorAll(".product-item").forEach((productItem) => {
      const productName = productItem
        .querySelector("h2")
        .textContent.toLowerCase();
      const productCategory = productItem
        .querySelector(".category")
        .textContent.toLowerCase();
      const productPrice = parseFloat(
        productItem.querySelector(".price").textContent.replace(/[^\d.-]/g, "")
      );

      const matchesSearch =
        productName.includes(query) || productCategory.includes(query);
      const matchesPrice = productPrice >= minPrice && productPrice <= maxPrice;

      if (matchesSearch && matchesPrice) {
        productItem.style.display = "block";
      } else {
        productItem.style.display = "none";
      }
    });
  }

  // Attach event listeners for filtering
  minPriceInput.addEventListener("input", filterProducts);
  maxPriceInput.addEventListener("input", filterProducts);
  searchInput.addEventListener("input", filterProducts);
});
