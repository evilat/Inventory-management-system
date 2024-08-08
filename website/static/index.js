document.addEventListener("DOMContentLoaded", () => {
  // Import CSV File
  const importCsvBtn = document.getElementById("import-csv-btn");
  const csvFileInput = document.getElementById("csv-file");
  const importCsvForm = document.getElementById("import-csv-form");

  if (importCsvBtn && csvFileInput && importCsvForm) {
    importCsvBtn.addEventListener("click", () => {
      csvFileInput.click();
    });

    csvFileInput.addEventListener("change", () => {
      importCsvForm.submit();
    });
  }

  // Flash messages duration
  const flashMessages = document.getElementById("flash-messages");

  if (flashMessages) {
    setTimeout(() => {
      flashMessages.classList.add("fade-out");
    }, 4000);

    setTimeout(() => {
      flashMessages.style.display = "none";
    }, 5000);
  }

  // Delete Product button using event delegation for dynamic content
  document.addEventListener("click", (e) => {
    let target = e.target;

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
  
  // Sorting functionality
  const sortSelector = document.getElementById("sort-selector");
  const productItemsContainer = document.getElementById("product-list");

  if (sortSelector && productItemsContainer) {
    function sortProductsByName(order) {
      const productItems = Array.from(
        productItemsContainer.querySelectorAll(".product-item")
      );

      productItems.sort((a, b) => {
        const nameA = a
          .querySelector(".product-name")
          .textContent.toLowerCase();
        const nameB = b
          .querySelector(".product-name")
          .textContent.toLowerCase();

        return order === "name-az"
          ? nameA.localeCompare(nameB)
          : nameB.localeCompare(nameA);
      });

      productItemsContainer.innerHTML = "";
      productItems.forEach((item) => productItemsContainer.appendChild(item));
    }

    sortSelector.addEventListener("change", () => {
      const selectedSort = sortSelector.value;
      if (selectedSort === "name-az" || selectedSort === "name-za") {
        sortProductsByName(selectedSort);
      }
    });
  }

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
        .querySelector(".product-name")
        .textContent.toLowerCase();
      const productCategory = productItem
        .querySelector("p:first-of-type")
        .textContent.toLowerCase();
      const productPriceText = productItem.querySelector("p:nth-of-type(2)");

      if (productPriceText) {
        const productPrice = parseFloat(
          productPriceText.textContent.replace(/[^\d.-]/g, "")
        );

        const matchesSearch =
          productName.includes(query) || productCategory.includes(query);
        const matchesPrice =
          productPrice >= minPrice && productPrice <= maxPrice;

        if (matchesSearch && matchesPrice) {
          productItem.style.display = "block";
        } else {
          productItem.style.display = "none";
        }
      } else {
        console.error("Product price text not found.");
      }
    });
  }

  if (minPriceInput) minPriceInput.addEventListener("input", filterProducts);
  if (maxPriceInput) maxPriceInput.addEventListener("input", filterProducts);
  if (searchInput) searchInput.addEventListener("input", filterProducts);
});
