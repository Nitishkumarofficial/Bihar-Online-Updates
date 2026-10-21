// ===============================
// MOBILE MENU
// ===============================

const menuBtn = document.getElementById("menuBtn");
const navMenu = document.getElementById("navMenu");

if (menuBtn && navMenu) {
    menuBtn.addEventListener("click", () => {

        navMenu.classList.toggle("active");

    });
}


// ===============================
// CLOSE MOBILE MENU AFTER CLICK
// ===============================

const navLinks = document.querySelectorAll(".nav-menu a");

navLinks.forEach(link => {

    link.addEventListener("click", () => {

        if (navMenu) {
            navMenu.classList.remove("active");
        }

    });

});


// ===============================
// SEARCH BOX
// ===============================

const searchBtn = document.getElementById("searchBtn");
const searchBox = document.getElementById("searchBox");
const searchClose = document.getElementById("searchClose");

if (searchBtn && searchBox) {
    searchBtn.addEventListener("click", () => {

        searchBox.classList.toggle("active");

    });
}

if (searchClose && searchBox) {
    searchClose.addEventListener("click", () => {

        searchBox.classList.remove("active");

    });
}

const copyUpdateLink = document.getElementById("copyUpdateLink");
const copyStatus = document.getElementById("copyStatus");
const detailShare = document.querySelector(".detail-share");
const nativeShareUpdate = document.getElementById("nativeShareUpdate");

if (detailShare) {
    const shareTitle = detailShare.dataset.shareTitle;
    const shareUrl = detailShare.dataset.shareUrl;
    const shareUrlParams = (values) => new URLSearchParams(values).toString();
    const shareText = `${shareTitle}\n${shareUrl}`;
    const shareLinks = {
        whatsapp: `https://wa.me/?${shareUrlParams({ text: shareText })}`,
        telegram: `https://t.me/share/url?${shareUrlParams({
            url: shareUrl,
            text: shareTitle
        })}`,
        facebook: `https://www.facebook.com/sharer/sharer.php?${shareUrlParams({
            u: shareUrl
        })}`,
        x: `https://twitter.com/intent/tweet?${shareUrlParams({
            url: shareUrl,
            text: shareTitle
        })}`,
        linkedin: `https://www.linkedin.com/sharing/share-offsite/?${shareUrlParams({
            url: shareUrl
        })}`
    };

    Object.entries(shareLinks).forEach(([platform, href]) => {
        const link = detailShare.querySelector(`[data-share-platform="${platform}"]`);
        if (link) {
            link.href = href;
        }
    });

    if (nativeShareUpdate) {
        nativeShareUpdate.addEventListener("click", async () => {
            if (!navigator.share) {
                copyStatus.textContent =
                    "Device sharing is not supported here. Choose a social app above or copy the link.";
                return;
            }

            try {
                await navigator.share({ title: shareTitle, text: shareTitle, url: shareUrl });
                copyStatus.textContent = "Share options opened.";
            } catch (error) {
                if (error.name === "AbortError") {
                    copyStatus.textContent = "Sharing cancelled.";
                    return;
                }
                copyStatus.textContent =
                    "Could not open device sharing. Choose a social app above or copy the link.";
            }
        });
    }
}

if (copyUpdateLink && copyStatus) {
    copyUpdateLink.addEventListener("click", async () => {
        try {
            const shareUrl = detailShare?.dataset.shareUrl || window.location.href;
            await navigator.clipboard.writeText(shareUrl);
            copyStatus.textContent = "Link copied.";
        } catch {
            const shareUrl = detailShare?.dataset.shareUrl || window.location.href;
            const fallbackInput = document.createElement("textarea");
            fallbackInput.value = shareUrl;
            fallbackInput.setAttribute("readonly", "");
            fallbackInput.style.position = "fixed";
            fallbackInput.style.opacity = "0";
            document.body.appendChild(fallbackInput);
            fallbackInput.select();
            const copied = document.execCommand("copy");
            fallbackInput.remove();

            if (copied) {
                copyStatus.textContent = "Link copied.";
            } else {
                copyStatus.textContent =
                    "Could not copy automatically. Select and copy this link:";
                window.prompt("Copy update link", shareUrl);
            }
        }
    });
}


// ===============================
// SMOOTH SCROLL
// ===============================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {

    anchor.addEventListener("click", function (e) {

        const target = document.querySelector(this.getAttribute("href"));

        if (target) {

            e.preventDefault();

            target.scrollIntoView({

                behavior: "smooth"

            });

        }

    });

});


// ===============================
// ACTIVE NAVIGATION
// ===============================

window.addEventListener("scroll", () => {

    const sections = document.querySelectorAll("section[id]");

    const scrollY = window.pageYOffset;


    sections.forEach(section => {

        const sectionHeight = section.offsetHeight;
        const sectionTop = section.offsetTop - 120;
        const sectionId = section.getAttribute("id");

        const navLink = document.querySelector(
            '.nav-menu a[href="#' + sectionId + '"]'
        );


        if (
            scrollY >= sectionTop &&
            scrollY < sectionTop + sectionHeight
        ) {

            if (navLink) {

                document.querySelectorAll(".nav-menu a")
                    .forEach(link =>
                        link.classList.remove("active")
                    );

                navLink.classList.add("active");

            }

        }

    });

});


// ===============================
// SCROLL TO TOP BUTTON
// ===============================

const scrollTopButton = document.createElement("button");

scrollTopButton.innerHTML =
    '<i class="fa-solid fa-arrow-up"></i>';

scrollTopButton.classList.add("scroll-top");

document.body.appendChild(scrollTopButton);


window.addEventListener("scroll", () => {

    if (window.scrollY > 500) {

        scrollTopButton.style.display = "flex";

    } else {

        scrollTopButton.style.display = "none";

    }

});


scrollTopButton.addEventListener("click", () => {

    window.scrollTo({

        top: 0,

        behavior: "smooth"

    });

});


// Add scroll top CSS dynamically

const style = document.createElement("style");

style.innerHTML = `

.scroll-top {

    position: fixed;

    right: 25px;

    bottom: 25px;

    width: 45px;

    height: 45px;

    border: none;

    border-radius: 50%;

    background: #ff7a00;

    color: white;

    cursor: pointer;

    display: none;

    align-items: center;

    justify-content: center;

    font-size: 16px;

    box-shadow: 0 5px 15px rgba(0,0,0,0.2);

    z-index: 999;

}

.scroll-top:hover {

    transform: translateY(-3px);

}

`;

document.head.appendChild(style);

document.addEventListener("DOMContentLoaded", function () {

    const filterButtons = document.querySelectorAll(".filter-btn");
    const updateCards = document.querySelectorAll(".update-card, .all-update-card");

    if (!filterButtons.length || !updateCards.length) {
        return;
    }

    filterButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const selectedFilter = button.dataset.filter || "all";

            filterButtons.forEach(function (btn) {
                btn.classList.toggle("active", btn === button);
            });

            updateCards.forEach(function (card) {

                const category = (card.dataset.category || "").toLowerCase();

                if (
                    selectedFilter === "all" ||
                    category === selectedFilter
                ) {
                    card.style.display = "";
                } else {
                    card.style.display = "none";
                }

            });

        });

    });

});