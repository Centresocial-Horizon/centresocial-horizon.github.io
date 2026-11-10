'use strict';
(async () => {
  const pending = document.querySelector('#editor-pending');
  function message(title, detail) {
    pending.hidden = false;
    pending.querySelector('h1').textContent = title;
    pending.querySelector('p').textContent = detail;
  }
  try {
    const response = await fetch('/admin/config.yml', {cache: 'no-store'});
    if (!response.ok) throw new Error('La configuration de l’éditeur ne peut pas être chargée.');
    const config = await response.text();
    const configured = /^\s*turbo_site_id:\s*['"]?[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}['"]?\s*$/im.test(config);
    if (!configured) {
      message('La première connexion reste à terminer.', 'Les formulaires sont prêts. L’autorisation du compte du centre doit encore être raccordée pour enregistrer et publier vos changements.');
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/decap-cms@3.17.0/dist/decap-cms.js';
    script.crossOrigin = 'anonymous';
    script.integrity = 'sha384-uh1IAMxJHPiQw7HR3dq6Nf1B/f7b5/Tj3XkNWpRWZhDsxZSqWZPbzWx+STgCBKQJ';
    script.onload = () => {
      if (!window.CMS) {
        message('L’éditeur n’a pas pu s’ouvrir.', 'Rechargez la page. Si le problème continue, vérifiez votre connexion Internet.');
        return;
      }
      pending.hidden = true;
      window.CMS.init();
    };
    script.onerror = () => message('Le chargement de l’éditeur est bloqué.', 'Vérifiez votre connexion Internet et les réglages de votre navigateur, puis rechargez la page.');
    document.body.appendChild(script);
  } catch (error) {
    message('L’éditeur est momentanément indisponible.', error.message || 'Rechargez la page dans quelques instants.');
  }
})();
