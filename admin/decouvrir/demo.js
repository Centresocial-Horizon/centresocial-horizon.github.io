'use strict';
(() => {
  const status = document.querySelector('#demo-status');
  const script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/decap-cms@3.17.0/dist/decap-cms.js';
  script.crossOrigin = 'anonymous';
    script.integrity = 'sha384-uh1IAMxJHPiQw7HR3dq6Nf1B/f7b5/Tj3XkNWpRWZhDsxZSqWZPbzWx+STgCBKQJ';
  script.onload = () => {
    if (!window.CMS) return;
    status.hidden = true;
    window.CMS.init();
  };
  script.onerror = () => {
    status.querySelector('h1').textContent = 'L’essai n’a pas pu se charger.';
    status.querySelector('p').textContent = 'Vérifiez votre connexion Internet, puis rechargez la page. Aucun contenu du site n’a été modifié.';
  };
  document.body.appendChild(script);
})();
