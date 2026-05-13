/* ── Avatar: Upload from local device ── */
const avatarUpload = document.getElementById("avatarUpload");
const avatarImg = document.getElementById("avatarImg");
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || "";

avatarUpload.addEventListener("change", function () {
    const file = this.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
        saveAvatar(e.target.result);
    };
    reader.readAsDataURL(file);
});

/* ── Avatar: Random generated locally ── */
document.getElementById("randomAvatarBtn").addEventListener("click", async function () {
    const seed = Math.random().toString(36).substring(2, 8);
    saveAvatar(createRandomAvatar(seed));
});

async function saveAvatar(avatarData) {
    const res = await fetch("/profile/update_avatar", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
        body: JSON.stringify({ avatar_data: avatarData })
    });

    if (res.ok) {
        const data = await res.json();
        avatarImg.src = `${data.avatar_url}?v=${Date.now()}`;
    }
}

function createRandomAvatar(seed) {
    const colors = ["#143543", "#16a34a", "#2563eb", "#dc2626", "#f59e0b", "#7c3aed"];
    const colorA = colors[seed.charCodeAt(0) % colors.length];
    const colorB = colors[seed.charCodeAt(1) % colors.length];
    const colorC = colors[seed.charCodeAt(2) % colors.length];
    const initials = seed.slice(0, 2).toUpperCase();
    const svg = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">
            <rect width="120" height="120" rx="60" fill="${colorA}"/>
            <circle cx="32" cy="34" r="24" fill="${colorB}" opacity="0.85"/>
            <circle cx="88" cy="88" r="30" fill="${colorC}" opacity="0.75"/>
            <text x="60" y="68" text-anchor="middle" font-family="Arial, sans-serif"
                  font-size="34" font-weight="700" fill="white">${initials}</text>
        </svg>
    `;
    return `data:image/svg+xml;base64,${btoa(svg)}`;
}

/* ── Email toggle ── */
const emailText = document.getElementById("emailText");
const revealEmailBtn = document.getElementById("revealEmailBtn");
const realEmail = emailText.dataset.email;
let emailVisible = false;

function toggleEmail() {
    emailVisible = !emailVisible;
    emailText.textContent = emailVisible ? realEmail : "••••••••••";
    revealEmailBtn.textContent = emailVisible ? "Hide" : "Show";
}

/* ── Bio: character counter ── */
const bioText = document.getElementById("bioText");
const bioCount = document.getElementById("bioCount");

bioCount.textContent = bioText.value.length;
bioText.addEventListener("input", function () {
    bioCount.textContent = this.value.length;
});

/* ── Bio: save ── */
document.getElementById("saveBioBtn").addEventListener("click", async function () {
    const bio = bioText.value.trim();
    const res = await fetch("/profile/update_bio", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
        body: JSON.stringify({ bio })
    });
    if (res.ok) {
        const btn = this;
        btn.textContent = "Saved ✓";
        btn.style.background = "#16a34a";
        setTimeout(() => {
            btn.textContent = "Save";
            btn.style.background = "";
        }, 1500);
    }
});

/* ── Hide holdings toggle ── */
document.getElementById("hideHoldingsToggle").addEventListener("change", async function () {
    await fetch("/profile/update_hide_holdings", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
        body: JSON.stringify({ hide_holdings: this.checked })
    });
});

/* ── Delete account modal ── */
const deleteModal = document.getElementById("deleteModal");

document.getElementById("deleteAccountBtn").addEventListener("click", function () {
    deleteModal.classList.add("active");
});

document.getElementById("cancelDeleteBtn").addEventListener("click", function () {
    deleteModal.classList.remove("active");
});

deleteModal.addEventListener("click", function (e) {
    if (e.target === deleteModal) {
        deleteModal.classList.remove("active");
    }
});

document.querySelector('.btn-confirm-delete').addEventListener('click', function() {
    document.getElementById('modalPassword').value = document.getElementById('deletePassword').value;
});

/* ── Assets & Holdings ── */
const stockValue = document.getElementById("stockValue");
const totalAssets = document.getElementById("totalAssets");
const availableCash = document.getElementById("availableCash");
const totalProfit = document.getElementById("totalProfit");
const holdingsBody = document.getElementById("holdingsBody");

function formatMoney(value) {
    return Number(value || 0).toLocaleString("en-US", {
        style: "currency",
        currency: "USD"
    });
}

function renderHoldings(holdings) {
    if (!holdings.length) {
        holdingsBody.innerHTML = '<tr><td colspan="6" class="empty-msg">No holdings yet.</td></tr>';
        return;
    }

    holdingsBody.innerHTML = holdings.map((holding) => `
        <tr>
            <td>${holding.symbol}</td>
            <td>${holding.quantity}</td>
            <td>${formatMoney(holding.averageCost)}</td>
            <td>${formatMoney(holding.currentPrice)}</td>
            <td>${formatMoney(holding.marketValue)}</td>
            <td class="${holding.unrealizedProfit >= 0 ? "profit-up" : "profit-down"}">
                ${formatMoney(holding.unrealizedProfit)}
            </td>
        </tr>
    `).join("");
}

async function loadPortfolioSummary() {
    const res = await fetch("/api/portfolio");

    if (!res.ok) {
        holdingsBody.innerHTML = '<tr><td colspan="6" class="empty-msg">Unable to load holdings.</td></tr>';
        return;
    }

    const portfolio = await res.json();
    availableCash.textContent = formatMoney(portfolio.cash);
    stockValue.textContent = formatMoney(portfolio.stockValue);
    totalAssets.textContent = formatMoney(portfolio.totalAssets);
    totalProfit.textContent = formatMoney(portfolio.totalProfit);
    totalProfit.classList.toggle("profit-up", portfolio.totalProfit >= 0);
    totalProfit.classList.toggle("profit-down", portfolio.totalProfit < 0);
    renderHoldings(portfolio.holdings || []);
}

loadPortfolioSummary();
