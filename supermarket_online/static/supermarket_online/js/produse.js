
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("searchInput");
    const productCards = Array.from(
        document.querySelectorAll(".product-card")
    );
    const productCount = document.getElementById("productCount");
    const noResults = document.getElementById("noResults");

    function filterProducts() {
        const query = searchInput.value
            .trim()
            .toLocaleLowerCase("ro");

        let visibleCount = 0;

        productCards.forEach((card) => {
            const productText = card.textContent
                .toLocaleLowerCase("ro");

            const matches = productText.includes(query);

            card.hidden = !matches;

            if (matches) {
                visibleCount++;
            }
        });

        if (visibleCount === 1) {
            productCount.textContent = "1 produs găsit";
        } else {
            productCount.textContent =
                `${visibleCount} produse găsite`;
        }

        noResults.hidden = visibleCount !== 0;
    }

    searchInput.addEventListener("input", filterProducts);

    document.querySelectorAll(".cart-button").forEach((button) => {
        button.addEventListener("click", () => {
            const productName = button.dataset.productName;

            alert(
                `Ai selectat produsul: ${productName}.\n` +
                "Coșul de cumpărături va fi implementat ulterior."
            );
        });
    });

    filterProducts();
});
