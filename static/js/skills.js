(function () {
  document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("skills-container");
    if (!container) return;

    const projectId = container.dataset.projectId;
    if (!projectId) return;

    const skillsUrl = "/projects/skills/";
    const addUrl = `/projects/${projectId}/skills/add`;
    const removeUrl = (skillId) => `/projects/${projectId}/skills/${skillId}/remove/`;

    const addBtn = document.getElementById("add-skill-btn");
    const inputWrapper = document.getElementById("skill-input-wrapper");
    const input = document.getElementById("skill-input");
    const suggestions = document.getElementById("skill-suggestions");

    if (!addBtn || !inputWrapper || !input || !suggestions) return;

    addBtn.addEventListener("click", () => {
      addBtn.classList.add("hidden");
      inputWrapper.classList.remove("hidden");
      input.value = "";
      suggestions.innerHTML = "";
      suggestions.classList.add("hidden");
      input.focus();
    });

    let timer = null;

    input.addEventListener("input", () => {
      const q = input.value.trim();

      clearTimeout(timer);

      if (!q) {
        suggestions.classList.add("hidden");
        suggestions.innerHTML = "";
        return;
      }

      timer = setTimeout(async () => {
        const response = await fetch(`${skillsUrl}?q=${encodeURIComponent(q)}`);

        if (!response.ok) return;

        const data = await response.json();

        suggestions.innerHTML = "";

        data.forEach((skill) => {
          const li = document.createElement("li");
          li.textContent = skill.name;
          li.dataset.id = skill.id;
          li.dataset.name = skill.name;
          li.className = "suggestion-item";
          suggestions.appendChild(li);
        });

        const exact = data.some(
          (skill) => skill.name.toLowerCase() === q.toLowerCase()
        );

        if (!exact) {
          const liNew = document.createElement("li");
          liNew.textContent = `Создать «${q}»`;
          liNew.dataset.name = q;
          liNew.className = "create-new";
          suggestions.appendChild(liNew);
        }

        suggestions.classList.remove("hidden");
      }, 200);
    });

    suggestions.addEventListener("mousedown", async (event) => {
      const li = event.target.closest("li");
      if (!li) return;

      if (li.classList.contains("create-new")) {
        await addSkillByName(li.dataset.name);
      } else if (li.dataset.id) {
        await addSkillById(li.dataset.id, li.dataset.name);
      }

      hideInput();
    });

    input.addEventListener("keydown", async (event) => {
      if (event.key === "Enter") {
        event.preventDefault();

        const q = input.value.trim();
        if (!q) return;

        const first = suggestions.querySelector("li");

        if (first && first.dataset.id) {
          await addSkillById(first.dataset.id, first.dataset.name);
        } else {
          await addSkillByName(q);
        }

        hideInput();
      }

      if (event.key === "Escape") {
        hideInput();
      }
    });

    input.addEventListener("blur", () => {
      setTimeout(hideInput, 120);
    });

    container.addEventListener("click", async (event) => {
      if (!event.target.classList.contains("remove-skill-btn")) return;

      const chip = event.target.closest(".skill-chip");
      if (!chip) return;

      const skillId = chip.dataset.id;

      const response = await fetch(removeUrl(skillId), {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
        },
      });

      if (response.ok) {
        chip.remove();
        ensureEmptyText();
      } else if (window.toast) {
        window.toast("Ошибка при удалении навыка", { type: "error" });
      }
    });

    async function addSkillById(skillId, displayName) {
      const response = await fetch(addUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ skill_id: skillId }),
      });

      if (response.ok) {
        const data = await response.json();
        appendChip(data.skill_id, displayName);
      } else if (window.toast) {
        window.toast("Ошибка при добавлении навыка", { type: "error" });
      }
    }

    async function addSkillByName(name) {
      const response = await fetch(addUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ name }),
      });

      if (response.ok) {
        const data = await response.json();
        appendChip(data.skill_id, name);
      } else if (window.toast) {
        window.toast("Ошибка при создании навыка", { type: "error" });
      }
    }

    function appendChip(id, name) {
      if (container.querySelector(`.skill-chip[data-id="${id}"]`)) return;

      const empty = container.querySelector(".skill-empty");

      if (empty) {
        empty.remove();
      }

      const chip = document.createElement("span");
      chip.className = "skill-chip";
      chip.dataset.id = id;

      chip.appendChild(document.createTextNode(`${name} `));

      const removeButton = document.createElement("button");
      removeButton.type = "button";
      removeButton.className = "remove-skill-btn";
      removeButton.setAttribute("aria-label", "Удалить");
      removeButton.title = "Удалить";
      removeButton.textContent = "×";

      chip.appendChild(removeButton);
      container.insertBefore(chip, addBtn);
    }

    function ensureEmptyText() {
      const hasSkills = container.querySelector(".skill-chip");

      if (!hasSkills && !container.querySelector(".skill-empty")) {
        const empty = document.createElement("span");
        empty.className = "skill-empty";
        empty.textContent = "Навыки не указаны";
        container.insertBefore(empty, addBtn);
      }
    }

    function hideInput() {
      inputWrapper.classList.add("hidden");
      suggestions.classList.add("hidden");
      suggestions.innerHTML = "";
      addBtn.classList.remove("hidden");
    }

    function getCookie(name) {
      if (window.getCookie) {
        return window.getCookie(name);
      }

      let cookieValue = null;

      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
          cookie = cookie.trim();

          if (cookie.startsWith(name + "=")) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }

      return cookieValue;
    }
  });
})();
