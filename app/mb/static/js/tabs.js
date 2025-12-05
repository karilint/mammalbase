function openTab(evt, tabName) {
  var i, x, tablinks;
  x = document.getElementsByClassName('tab');
  for (i = 0; i < x.length; i++) {
    x[i].style.display = 'none';
  }
  tablinks = document.getElementsByClassName('tablink');
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].classList.remove('w3-teal');
  }
  document.getElementById(tabName).style.display = 'block';
  if (evt) {
    evt.currentTarget.classList.add('w3-teal');
  }
}
