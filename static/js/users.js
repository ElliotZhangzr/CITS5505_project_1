function filterUsers() {
    const input = document.getElementById("searchInput");
    const filter = input.value.trim().toLowerCase();
    const rows = document.querySelectorAll(".user-row");
    const noResultsMessage = document.getElementById("noResultsMessage");

    let visibleRows = 0;

    rows.forEach((row) => {
        const rowText = row.textContent.toLowerCase();

        if (rowText.includes(filter)) {
            row.style.display = "";
            visibleRows++;
        } else {
            row.style.display = "none";
        }
    });

    if (visibleRows === 0) {
        noResultsMessage.classList.remove("d-none");
    } else {
        noResultsMessage.classList.add("d-none");
    }
}