function filterUsers() {

    // Get search input
    const searchInput = document.getElementById("searchInput");
    const searchValue = searchInput.value.trim().toLowerCase();

    // Get all user rows
    const userRows = document.querySelectorAll(".user-row");

    // No results message
    const noResultsMessage = document.getElementById("noResultsMessage");

    let matchedUsers = 0;

    userRows.forEach((row) => {
        const userId = row.cells[0]?.textContent.trim().toLowerCase() || "";
        const username = row.cells[1]?.querySelector(".user-profile-link")?.textContent.trim().toLowerCase() || "";
        const matchesSearch = userId.includes(searchValue) || username.includes(searchValue);

        if (matchesSearch) {
            row.style.display = "";
            matchedUsers++;
        } else {
            row.style.display = "none";
        }
    });

    // Toggle no results message
    if (matchedUsers === 0) {
        noResultsMessage.classList.remove("hidden");
    } else {
        noResultsMessage.classList.add("hidden");
    }
}
