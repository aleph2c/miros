/**
 * Inserts the current year.
 *
 * This function will find all elements with the class "js-year"
 * and set its text content to the current year.
 */
function currentYear() {
  const year = new Date().getFullYear();
  const yearEls = document.querySelectorAll('.js-year');
  for (let i = 0; i < yearEls.length; i++) {
    yearEls[i].textContent = year;
  }
}

/**
 * Toggle the sidebar
 */
function toggleSidebar() {
  const sidebar = document.getElementById('js-main-sidebar');
  const sidebar_mask = document.getElementById('js-sidebar-mask');
  sidebar.classList.toggle('main-sidebar--open');
  sidebar_mask.classList.toggle('sidebar-mask--open');

}

/**
 * Add the language to codeblocks
 */
function codeblockLanguage() {
  let codeblocks = document.querySelectorAll('div[class^="highlight-"]');
  for (let i = 0; i < codeblocks.length; i++) {
    let language = codeblocks[i].className.split(' ')[0].split('-')[1];
    if (language !== 'default') {
      let el = document.createElement('div');
      el.className = 'code-block-language';
      el.textContent = language;
      codeblocks[i].appendChild(el);
    }
  }
}


window.addEventListener('load', function() {
  if (document.querySelector('.js-year')) {
    currentYear();
    codeblockLanguage();
  }
}, false);

window.addEventListener('click', function(e) {
  // console.log(e.target);
  if (e.target.matches('#js-sidebar-menu-button') ||
      e.target.matches('#js-sidebar-mask') ||
      e.target.matches('#js-main-sidebar li a')) {
    toggleSidebar();
  }
}, false);

window.addEventListener('touchstart', function(e) {
  // console.log(e.target);
  if (e.target.matches('#js-sidebar-menu-button') ||
      e.target.matches('#js-sidebar-mask')) {
    toggleSidebar();
  }
}, false);
