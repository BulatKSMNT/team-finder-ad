(function () {
  document.addEventListener("DOMContentLoaded", function () {
    const completeBtn = document.getElementById("complete-project-btn");

    if (!completeBtn) return;

    completeBtn.addEventListener("click", function (event) {
      event.preventDefault();

      const form = completeBtn.closest("form");
      if (!form) return;

      fetch(form.action, {
        method: "POST",
        headers: {
          "X-CSRFToken": window.getCookie ? window.getCookie("csrftoken") : "",
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({}),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "ok" && data.project_status === "closed") {
            document.querySelectorAll(".project-status-black").forEach((element) => {
              element.textContent = "Закрыт";
            });

            form.remove();

            if (window.toast) {
              window.toast("Проект завершён", { type: "info" });
            }
          } else if (window.toast) {
            window.toast(data.message || "Ошибка при завершении проекта", { type: "error" });
          } else {
            alert(data.message || "Ошибка при завершении проекта");
          }
        })
        .catch((error) => {
          console.error("Ошибка запроса:", error);

          if (window.toast) {
            window.toast("Ошибка сети", { type: "error" });
          }
        });
    });
  });
})();
