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


// ===============================
// SEARCH FUNCTION
// ===============================

const searchInput = document.getElementById("searchInput");
const searchableItems = document.querySelectorAll(".searchable");

if (searchInput && searchableItems.length) {
    searchInput.addEventListener("keyup", () => {

        const searchValue = searchInput.value.toLowerCase();


        searchableItems.forEach(item => {

            const text = item.innerText.toLowerCase();


            if (text.includes(searchValue)) {

                item.style.display = "";

            } else {

                item.style.display = "none";

            }

        });

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