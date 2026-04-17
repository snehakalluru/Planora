(function () {
    function applySavedTheme() {
        const savedTheme = localStorage.getItem("theme");
        if (savedTheme === "dark") {
            document.body.classList.add("dark-mode");
        } else {
            document.body.classList.remove("dark-mode");
        }
        document.dispatchEvent(new CustomEvent("themechange"));
    }

    function setupCursorGlow() {
        const glow = document.querySelector(".cursor-glow");
        if (!glow) {
            return;
        }

        const shouldDisableGlow = window.matchMedia("(hover: none), (pointer: coarse)").matches;
        if (shouldDisableGlow) {
            glow.style.display = "none";
            return;
        }

        let x = 0;
        let y = 0;
        let frameRequested = false;

        function renderGlow() {
            glow.style.left = x + "px";
            glow.style.top = y + "px";
            frameRequested = false;
        }

        document.addEventListener("mousemove", (event) => {
            x = event.clientX;
            y = event.clientY;

            if (!frameRequested) {
                frameRequested = true;
                window.requestAnimationFrame(renderGlow);
            }
        });
    }

    window.onload = function () {
        applySavedTheme();
        setupCursorGlow();

        const toggle = document.getElementById("theme-toggle");
        if (toggle) {
            toggle.addEventListener("click", () => {
                document.body.classList.toggle("dark-mode");

                if (document.body.classList.contains("dark-mode")) {
                    localStorage.setItem("theme", "dark");
                } else {
                    localStorage.setItem("theme", "light");
                }

                document.dispatchEvent(new CustomEvent("themechange"));
            });
        }
    };
}());
