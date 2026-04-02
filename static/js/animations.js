// Timeline slide-in on scroll
(function () {
  function revealTimelineItems() {
    var items = document.querySelectorAll('.timeline-item');
    var windowBottom = window.scrollY + window.innerHeight;
    items.forEach(function (item) {
      var itemTop = item.getBoundingClientRect().top + window.scrollY;
      if (itemTop < windowBottom - 60) {
        item.classList.add('visible');
      }
    });
  }

  if (document.querySelector('.timeline-item')) {
    window.addEventListener('scroll', revealTimelineItems);
    revealTimelineItems(); // run once on load for items already in view
  }
})();

// Heart bounce on like button click
// The CSS animation is triggered by the 'liked' class.
// HTMX swaps the button HTML, so the animation runs on the new element naturally.
// This block re-processes any newly swapped like buttons for HTMX.
document.addEventListener('htmx:afterSwap', function (evt) {
  var btn = evt.detail.elt;
  if (btn && btn.classList && btn.classList.contains('like-btn')) {
    btn.classList.add('liked');
  }
});
