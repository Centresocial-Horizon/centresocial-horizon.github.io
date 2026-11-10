'use strict';
(()=>{
 const api=window.HorizonSearch;if(!api)return;const today=api.dateInParis(),limit=api.cutoff(today);
 document.querySelectorAll('[data-published-on],[data-expires-on]').forEach(el=>{const expiry=el.dataset.expiresOn||el.dataset.publishedOn;if(expiry&&expiry<limit){el.remove();}});
 const story=document.querySelector('[data-story-date]');
 if(story&&story.dataset.storyDate<limit){const article=story.querySelector('.content-article');if(article)article.innerHTML='<div class="document-help"><h2>Cette actualité n’est plus affichée.</h2><p>Elle date de plus de deux mois. Retrouvez les informations récentes et les activités actuelles du centre.</p><a href="/tout-horizon/">Voir les informations actuelles →</a></div>';document.querySelector('.content-heading h1')?.replaceChildren(document.createTextNode('Cette actualité n’est plus affichée.'));document.querySelector('.content-heading time')?.remove();let robots=document.querySelector('meta[name="robots"]');if(!robots){robots=document.createElement('meta');robots.name='robots';document.head.append(robots)}robots.content='noindex,follow';}
 document.querySelectorAll('.news').forEach(section=>{if(!section.querySelector('.news-card'))section.hidden=true});
})();
