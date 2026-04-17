(function () {
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop().split(";").shift();
        }
        return "";
    }

    function syncHabitCard(card, data) {
        card.querySelector("[data-field='streak']").textContent = data.streak;
        card.querySelector("[data-field='progress']").textContent = data.progress;
        card.querySelector("[data-field='risk']").textContent = data.risk;
        card.querySelector("[data-field='insight']").textContent = data.insight;
        card.querySelector("[data-field='status']").textContent = data.today_done ? "Completed today" : "Waiting for today's rep";
        card.querySelector("[data-field='difficulty']").textContent = data.difficulty;
        card.querySelector("[data-field='progressbar']").style.width = `${data.progress}%`;

        const riskChip = card.querySelector(".risk-chip");
        riskChip.textContent = data.risk_band;
        riskChip.className = `risk-chip risk-chip--${data.risk_band.toLowerCase()}`;

        const buttons = card.querySelectorAll(".habit-action");
        buttons.forEach((button) => {
            const action = button.dataset.action;
            if (action === "toggle") {
                button.textContent = data.today_done ? "Undo Today" : "Complete Today";
            }
            if (action === "focus") {
                button.textContent = data.focus_mode ? "Exit Focus" : "Focus Mode";
            }
        });
    }

    async function postForm(url, payload) {
        const formData = new URLSearchParams(payload || {});
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: formData.toString(),
        });
        if (!response.ok) {
            throw new Error("Request failed");
        }
        return response.json();
    }

    const moodForm = document.getElementById("mood-form");
    const moodStatus = document.getElementById("mood-status");
    if (moodForm) {
        moodForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const formData = new FormData(moodForm);
            try {
                const response = await fetch(moodForm.action, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"),
                    },
                    body: formData,
                });
                const data = await response.json();
                moodStatus.textContent = data.message || "Mood updated.";
            } catch (error) {
                moodStatus.textContent = "Mood logging failed. Please try again.";
            }
        });
    }

    document.querySelectorAll(".habit-card").forEach((card) => {
        card.addEventListener("click", async (event) => {
            const button = event.target.closest(".habit-action");
            if (!button) {
                return;
            }

            const action = button.dataset.action;
            const url = action === "toggle"
                ? card.dataset.toggleUrl
                : action === "focus"
                    ? card.dataset.focusUrl
                    : card.dataset.recoveryUrl;

            const payload = action === "focus"
                ? { enabled: button.textContent.includes("Focus Mode") ? "true" : "false" }
                : {};

            const originalText = button.textContent;
            button.disabled = true;
            button.textContent = "Working...";

            try {
                const data = await postForm(url, payload);
                syncHabitCard(card, data.habit);
                const profileLevel = document.getElementById("profile-level");
                const profileProgress = document.getElementById("profile-progress");
                if (profileLevel) {
                    profileLevel.textContent = data.profile.level;
                }
                if (profileProgress) {
                    profileProgress.style.width = `${data.profile.progress}%`;
                }
            } catch (error) {
                button.textContent = "Try Again";
            } finally {
                button.disabled = false;
                if (button.textContent === "Working...") {
                    button.textContent = originalText;
                }
            }
        });
    });
}());
