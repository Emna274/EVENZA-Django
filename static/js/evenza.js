const toggle = document.querySelector("#nav-toggle");
const sidebar = document.querySelector("#sidebar");
const closeMenu = document.querySelector("#nav-close");
const backdrop = document.querySelector("#nav-backdrop");
const workspace = document.querySelector(".workspace");

if (toggle && sidebar && closeMenu && backdrop && workspace) {
    const mobileLayout = window.matchMedia("(max-width: 990px)");

    function setNavigation(open, restoreFocus = false) {
        if (open) {
            sidebar.classList.add("is-open");
            sidebar.setAttribute("role", "dialog");
            sidebar.setAttribute("aria-modal", "true");
            closeMenu.focus();
        } else {
            workspace.inert = false;
            if (restoreFocus && mobileLayout.matches) toggle.focus();
            sidebar.classList.remove("is-open");
            sidebar.removeAttribute("role");
            sidebar.removeAttribute("aria-modal");
        }
        workspace.inert = open;
        backdrop.hidden = !open;
        document.body.classList.toggle("nav-open", open);
        toggle.setAttribute("aria-expanded", String(open));
    }

    toggle.addEventListener("click", () => setNavigation(true));
    closeMenu.addEventListener("click", () => setNavigation(false, true));
    backdrop.addEventListener("click", () => setNavigation(false, true));
    mobileLayout.addEventListener("change", () => {
        if (sidebar.classList.contains("is-open")) setNavigation(false);
    });
    document.addEventListener("keydown", (event) => {
        if (!sidebar.classList.contains("is-open")) return;
        if (event.key === "Escape") {
            event.preventDefault();
            setNavigation(false, true);
        } else if (event.key === "Tab") {
            const items = sidebar.querySelectorAll("a[href], button:not([disabled])");
            const first = items[0];
            const last = items[items.length - 1];
            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        }
    });
}

const confirmation = document.querySelector("#action-confirmation");
if (confirmation && typeof confirmation.showModal === "function") {
    let pending;
    const confirmed = new WeakSet();

    for (const form of document.querySelectorAll("form[data-confirm]")) {
        form.addEventListener("submit", (event) => {
            if (confirmed.delete(form)) return;
            event.preventDefault();
            pending = {form, submitter: event.submitter};
            confirmation.querySelector("[data-confirmation-text]").textContent = form.dataset.confirm;
            confirmation.returnValue = "cancel";
            confirmation.showModal();
        });
    }

    confirmation.addEventListener("close", () => {
        if (confirmation.returnValue === "confirm" && pending) {
            const {form, submitter} = pending;
            confirmed.add(form);
            if (submitter) form.requestSubmit(submitter);
            else form.requestSubmit();
            confirmed.delete(form);
        }
        pending = undefined;
    });
} else {
    for (const form of document.querySelectorAll("form[data-confirm]")) {
        form.addEventListener("submit", (event) => {
            if (!window.confirm(form.dataset.confirm)) event.preventDefault();
        });
    }
}
