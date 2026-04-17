(function () {
    function applySavedTheme() {
        const savedTheme = localStorage.getItem("theme");
        if (savedTheme === "dark") {
            document.body.classList.add("dark-mode");
        } else {
            document.body.classList.remove("dark-mode");
        }
    }

    window.onload = function () {
        applySavedTheme();

        const toggle = document.getElementById("theme-toggle");
        if (!toggle) {
            return;
        }

        toggle.addEventListener("click", () => {
            document.body.classList.toggle("dark-mode");

            if (document.body.classList.contains("dark-mode")) {
                localStorage.setItem("theme", "dark");
            } else {
                localStorage.setItem("theme", "light");
            }
        });
    };
}());
