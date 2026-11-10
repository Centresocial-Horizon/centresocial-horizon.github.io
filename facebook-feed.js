'use strict';
(()=>{
 const load=document.querySelector('#facebook-load');const frame=document.querySelector('#facebook-feed');const hide=document.querySelector('#facebook-hide');const controls=document.querySelector('#facebook-hide-controls');
 if(!load||!frame||!hide||!controls)return;
 const page=document.querySelector('#social-live')?.dataset?.facebookPage||'https://www.facebook.com/p/Centre-Social-et-Socioculturel-Horizon-100067073132159/';
 function closeFeed(){frame.replaceChildren();frame.hidden=true;controls.hidden=true;load.hidden=false;load.setAttribute('aria-expanded','false');load.focus()}
 load.addEventListener('click',()=>{
  if(frame.querySelector('iframe'))return;
  const params=new URLSearchParams({href:page,tabs:'timeline',width:'500',height:'420',small_header:'true',adapt_container_width:'true',hide_cover:'true',show_facepile:'false'});
  const iframe=document.createElement('iframe');iframe.src='https://www.facebook.com/plugins/page.php?'+params.toString();iframe.title='Publications Facebook du Centre social et socioculturel Horizon';iframe.width='500';iframe.height='420';iframe.tabIndex=0;iframe.style.border='0';iframe.style.overflow='hidden';iframe.setAttribute('scrolling','no');iframe.setAttribute('allow','encrypted-media; picture-in-picture');iframe.setAttribute('referrerpolicy','strict-origin-when-cross-origin');
  frame.replaceChildren(iframe);frame.hidden=false;controls.hidden=false;load.hidden=true;load.setAttribute('aria-expanded','true');iframe.focus();
 });
 hide.addEventListener('click',closeFeed);
})();
