
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("searchInput");
    const productList = document.getElementById("productList");
    const productCount = document.getElementById("productCount");
    const noResults = document.getElementById("noResults");
    const categoryButtons = document.querySelectorAll("[data-category-filter]");

    if (!productList || !searchInput) return;

    const products = Array.from(
        productList.querySelectorAll(".product-card")
    );

    let selectedCategory = "";

    function normalize(value) {
        return (value || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLocaleLowerCase("ro")
            .trim();
    }

    function filterProducts() {
        const query = normalize(searchInput.value);
        let visibleCount = 0;

        products.forEach((product) => {
            const category = normalize(product.dataset.productCategory);
            const content = normalize(product.textContent);

            const matchesSearch = content.includes(query);
            const matchesCategory =
                !selectedCategory || category === normalize(selectedCategory);

            const visible = matchesSearch && matchesCategory;

            product.hidden = !visible;

            if (visible) visibleCount++;
        });

        if (productCount) {
            productCount.textContent =
                `Produse afișarte: ${visibleCount} din ${products.length}`;
        }

        if (noResults) {
            noResults.hidden = visibleCount !== 0;
        }
    }

    searchInput.addEventListener("input", filterProducts);

    // Gestionarea selectării unei categorii prin apăsarea butonului
    categoryButtons.forEach((button) => {
        button.addEventListener("click", () => {
            selectedCategory = button.dataset.categoryFilter || "";
            searchInput.value = "";

            filterProducts();

            document.getElementById("catalog")?.scrollIntoView({
                behavior: "smooth"
            });
        });
    });

    filterProducts();
});
