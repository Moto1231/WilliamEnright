const slides = document.querySelectorAll(".slide");

let current = 0;

function show(index) {

  slides[current].classList.remove("active");

  current = index;

  slides[current].classList.add("active");

}