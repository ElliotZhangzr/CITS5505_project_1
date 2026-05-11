/* ── Avatar: Upload from local device ── */
const avatarUpload = document.getElementById("avatarUpload");
const avatarImg = document.getElementById("avatarImg");

avatarUpload.addEventListener("change", function () {
    const file = this.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
        avatarImg.src = e.target.result;
        saveAvatar(e.target.result);
    };
    reader.readAsDataURL(file);
});

/* ── Avatar: Random from public API (DiceBear) ── */
document.getElementById("randomAvatarBtn").addEventListener("click", async function () {
    const seed = Math.random().toString(36).substring(2, 8);
    const url = `https://api.dicebear.com/8.x/thumbs/svg?seed=${seed}`;
    avatarImg.src = url;
    saveAvatar(url);
});

function saveAvatar(url) {
    fetch("/profile/update_avatar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ avatar_url: url })
    });
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
        headers: { "Content-Type": "application/json" },
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
        headers: { "Content-Type": "application/json" },
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
