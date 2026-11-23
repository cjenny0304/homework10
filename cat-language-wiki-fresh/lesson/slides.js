'use strict';

const slides = Array.from(document.querySelectorAll('.slide'));
const previous = document.querySelector('#previous');
const next = document.querySelector('#next');
const progress = document.querySelector('#progress');
const position = document.querySelector('#position');
let active = 0;

function show(index, focusHeading = true) {
  if (index < 0 || index >= slides.length) return;
  active = index;
  slides.forEach((slide, number) => { slide.hidden = number !== active; });
  position.textContent = `${String(active + 1).padStart(2, '0')} / ${slides.length}`;
  progress.value = active + 1;
  previous.disabled = active === 0;
  next.disabled = active === slides.length - 1;
  if (focusHeading) {
    window.scrollTo(0, 0);
    slides[active].querySelector('h1').focus({preventScroll: true});
  }
}

previous.addEventListener('click', () => show(active - 1));
next.addEventListener('click', () => show(active + 1));
document.addEventListener('keydown', (event) => {
  if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || event.defaultPrevented) return;
  if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
  event.preventDefault();
  show(active + (event.key === 'ArrowRight' ? 1 : -1));
});

document.querySelectorAll('.guess button').forEach((button) => {
  button.addEventListener('click', () => {
    const group = button.closest('.guess');
    group.querySelectorAll('button').forEach((choice) => choice.setAttribute('aria-pressed', String(choice === button)));
    group.nextElementSibling.textContent = button.dataset.feedback;
  });
});

document.querySelectorAll('.flip').forEach((button) => {
  button.addEventListener('click', () => {
    const open = button.getAttribute('aria-expanded') !== 'true';
    button.setAttribute('aria-expanded', String(open));
    button.querySelector('.back').hidden = !open;
    button.querySelector('.flip-label').textContent = open ? '收起解答' : '翻開解答';
  });
});

const questions = Array.from(document.querySelectorAll('.question'));
const score = document.querySelector('#score');

function updateScore() {
  const answered = questions.filter((question) => question.querySelector('[aria-pressed="true"]'));
  const correct = answered.filter((question) => question.querySelector('[aria-pressed="true"]').dataset.correct === 'true');
  score.textContent = answered.length === questions.length
    ? `答對 ${correct.length} / ${questions.length} 題`
    : `已作答 ${answered.length} / ${questions.length} 題`;
}

questions.forEach((question) => {
  const choices = question.querySelectorAll('.answer');
  choices.forEach((button) => {
    button.addEventListener('click', () => {
      choices.forEach((choice) => choice.setAttribute('aria-pressed', String(choice === button)));
      const result = button.dataset.correct === 'true' ? '答對了。' : '再想一想。';
      question.querySelector('.feedback').textContent = result + question.dataset.explanation;
      updateScore();
    });
  });
});

document.querySelector('#reset').addEventListener('click', () => {
  questions.forEach((question) => {
    question.querySelectorAll('.answer').forEach((choice) => choice.setAttribute('aria-pressed', 'false'));
    question.querySelector('.feedback').textContent = '';
  });
  updateScore();
  questions[0].querySelector('.answer').focus();
});

show(0, false);
