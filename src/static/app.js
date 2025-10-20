document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

  // Clear select options (mantener placeholder en español)
  activitySelect.innerHTML = '<option value="">-- Selecciona una actividad --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Build participants HTML
        let participantsHTML = "";
        if (Array.isArray(details.participants) && details.participants.length > 0) {
          participantsHTML += `<div class="participants"><h5>Participantes</h5><ul class="participants-list">`;
          participantsHTML += details.participants
              .map((p) => {
                // derive initials from the part before '@' and from words / separators
                const namePart = String(p).split("@")[0] || "";
                const initials = namePart
                  .replace(/[._-]/g, " ")
                  .split(" ")
                  .map((s) => s.charAt(0))
                  .filter(Boolean)
                  .slice(0, 2)
                  .join("")
                  .toUpperCase() || p.charAt(0).toUpperCase();
                // Use data attributes and a delete button; the actual handler is attached later
                // Accessible SVG icon button with aria-label and title in Spanish
                const svgIcon = `
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
                    <path d="M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M6 18L18 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>`;

                return `<li class="participant-item"><div class="participant-left"><span class="avatar">${initials}</span><span class="participant-email">${p}</span></div><button class="participant-delete" data-activity="${encodeURIComponent(
                  name
                )}" data-email="${encodeURIComponent(p)}" aria-label="Dar de baja a ${p} de ${name}" title="Dar de baja">${svgIcon}</button></li>`;
              })
              .join("");
          participantsHTML += `</ul></div>`;
        } else {
          participantsHTML = `<p class="no-participants">No hay participantes aún</p>`;
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Horario:</strong> ${details.schedule}</p>
          <p><strong>Disponibilidad:</strong> ${spotsLeft} plazas disponibles</p>
          ${participantsHTML}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    const signupButton = document.getElementById("signup-button");
    const spinner = signupButton.querySelector(".spinner");
    const btnLabel = signupButton.querySelector(".btn-label");

    // show spinner and disable button
    signupButton.disabled = true;
    spinner.classList.remove("hidden");
    btnLabel.setAttribute("aria-hidden", "true");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message || "Inscripción realizada con éxito";
        messageDiv.className = "success";
        signupForm.reset();
        // refrescar la lista de actividades para mostrar el nuevo participante
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "Ocurrió un error";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Ocultar mensaje después de 5 segundos
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "No se pudo inscribir. Inténtalo de nuevo.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    } finally {
      // hide spinner and enable button
      signupButton.disabled = false;
      spinner.classList.add("hidden");
      btnLabel.removeAttribute("aria-hidden");
      // Ensure message is available to screen readers (aria-live region)
      messageDiv.setAttribute("role", "status");
    }
  });

  // Initialize app
  fetchActivities();

  // Delegate click handler for delete buttons inside activitiesList
  activitiesList.addEventListener("click", async (e) => {
    const btn = e.target.closest(".participant-delete");
    if (!btn) return;

    const activityName = decodeURIComponent(btn.getAttribute("data-activity") || "");
    const email = decodeURIComponent(btn.getAttribute("data-email") || "");

    if (!activityName || !email) return;

    const confirmRemove = window.confirm(
      `¿Estás seguro de que deseas dar de baja a ${email} de ${activityName}?`
    );
    if (!confirmRemove) return;

    try {
      const res = await fetch(
        `/activities/${encodeURIComponent(activityName)}/participants?email=${encodeURIComponent(
          email
        )}`,
        { method: "DELETE" }
      );

      const result = await res.json();
      if (res.ok) {
        // show brief success message
  messageDiv.textContent = result.message || "Baja realizada con éxito";
  messageDiv.className = "success";
        messageDiv.classList.remove("hidden");
        setTimeout(() => messageDiv.classList.add("hidden"), 3000);
        // refresh activities
        fetchActivities();
      } else {
  messageDiv.textContent = result.detail || "No se pudo dar de baja";
  messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
      }
    } catch (err) {
      console.error("Error unregistering:", err);
  messageDiv.textContent = "No se pudo dar de baja. Inténtalo de nuevo.";
  messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
    }
  });
});
