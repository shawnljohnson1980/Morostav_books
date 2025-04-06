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

