function toggleStops(routeId) {
    const stopsList = document.getElementById(routeId);
    const icon = stopsList.previousElementSibling.querySelector('.dropdown-icon');
  
    if (stopsList.style.display === "none" || !stopsList.style.display) {
        stopsList.style.display = "block";
        icon.classList.add('open');
    } else {
        stopsList.style.display = "none";
        icon.classList.remove('open');
    }
  }