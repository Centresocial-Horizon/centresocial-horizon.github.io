'use strict';
(async () => {
  const status = document.querySelector('#connection-status');
  const setup = document.querySelector('#setup-panel');
  const button = document.querySelector('#open-editor');
  try {
    const response = await fetch('/admin/config.yml', {cache: 'no-store'});
    if (!response.ok) throw new Error('config');
    const text = await response.text();
    const match = text.match(/^\s*turbo_site_id:\s*['"]?([0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})['"]?\s*$/im);
    if (match && /^\s*name:\s*turbo-github\s*$/m.test(text)) {
      status.textContent = 'Éditeur configuré · connexion à votre compte requise';
      status.classList.add('ready');
      button.hidden = false;
      setup.hidden = true;
    } else {
      status.textContent = 'Connexion initiale à terminer';
    }
  } catch (_) {
    status.textContent = 'Configuration momentanément indisponible';
    const heading = setup.querySelector('h2');
    if (heading) heading.textContent = 'La connexion ne peut pas encore être vérifiée.';
  }
})();
