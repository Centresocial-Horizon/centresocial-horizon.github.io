'use strict';
const menu=document.querySelector('.menu-toggle');const nav=document.querySelector('#main-nav');
function closeMenu(){menu.setAttribute('aria-expanded','false');menu.querySelector('.sr-only').textContent='Ouvrir le menu';nav.classList.remove('open')}
menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));menu.querySelector('.sr-only').textContent=open?'Fermer le menu':'Ouvrir le menu';nav.classList.toggle('open',open)});
nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMenu));document.addEventListener('keydown',e=>{if(e.key==='Escape')closeMenu()});window.matchMedia('(min-width:1201px)').addEventListener('change',e=>{if(e.matches)closeMenu()});
