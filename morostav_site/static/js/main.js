// Navbar glow on scroll
document.addEventListener("scroll", () => {
    const nav = document.querySelector(".navbar");
    if (nav && window.scrollY > 50) {
      nav.classList.add("scrolled");
    } else {
      nav.classList.remove("scrolled");
    }
  });
  
  // Future: Gallery lightbox, modal triggers, theme toggles? Put them here.

  const scrollBtn = document.createElement('button');
scrollBtn.innerText = "↑";
scrollBtn.id = "scrollToTop";
scrollBtn.style = "position:fixed;bottom:20px;right:20px;padding:10px;display:none;";
document.body.appendChild(scrollBtn);

window.addEventListener("scroll", () => {
  scrollBtn.style.display = window.scrollY > 300 ? "block" : "none";
});

scrollBtn.addEventListener("click", () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

const currentUrl = window.location.pathname;
document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
  if (link.getAttribute('href') === currentUrl) {
    link.classList.add('active');
  }
});

const cards = document.querySelectorAll('.card');
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('fade-in');
    }
  });
}, { threshold: 0.2 });

cards.forEach(card => {
  observer.observe(card);
});


  document.addEventListener("DOMContentLoaded", function () {
    const faders = document.querySelectorAll(".fade-in-scroll");

    const appearOptions = {
      threshold: 0.1,
      rootMargin: "0px 0px -100px 0px"
    };

    const appearOnScroll = new IntersectionObserver(function (entries, appearOnScroll) {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("visible");
        appearOnScroll.unobserve(entry.target);
      });
    }, appearOptions);

    faders.forEach(fader => {
      appearOnScroll.observe(fader);
    });
  });
  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".ban-btn").forEach(button => {
      button.addEventListener("click", function () {
        const ip = this.getAttribute("data-ip");
        if (confirm(`Are you sure you want to ban IP: ${ip}?`)) {
          fetch("/ban-ip/", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ ip: ip })
          })
          .then(response => response.json())
          .then(data => {
            if (data.message) {
              alert(data.message);
              this.disabled = true;
              this.textContent = "Banned";
            } else {
              alert("Failed to ban IP.");
            }
          })
          .catch(error => {
            alert("Something went wrong.");
            console.error("Error banning IP:", error);
          });
        }
      });
    });
  });
  
  function confirmBan(button) {
    const ip = button.getAttribute("data-ip");
    const username = button.getAttribute("data-username");

    document.getElementById("banTargetIP").textContent = ip;
    document.getElementById("banTargetUser").textContent = username;

    const confirmBtn = document.getElementById("confirmBanBtn");
    confirmBtn.onclick = function () {
        fetch("/ban_ip/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ ip_address: ip })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("User has been banished.");
                location.reload();  // Optional: Refresh to reflect ban
            } else {
                alert("Could not ban. Something went wrong.");
            }
        });

        const modal = bootstrap.Modal.getInstance(document.getElementById('banConfirmModal'));
        modal.hide();
    };

    const modal = new bootstrap.Modal(document.getElementById('banConfirmModal'));
    modal.show();
}

// CSRF helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const trimmed = cookie.trim();
            if (trimmed.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

<script>
window.addEventListener("beforeunload", function (e) {
    navigator.sendBeacon("{% url 'logout' %}");
});
</script>