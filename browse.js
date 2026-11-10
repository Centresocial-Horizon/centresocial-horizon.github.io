'use strict';
(() => {
 const params=new URLSearchParams(location.search);
 const form=document.querySelector('#directory-search');
 const query=document.querySelector('#directory-query');
 const kind=document.querySelector('#directory-kind');
 const category=document.querySelector('#directory-category');
 const year=document.querySelector('#directory-year');
 const results=document.querySelector('#result-list');
 const count=document.querySelector('#result-count');
 const more=document.querySelector('#more-results');
 const shown=document.querySelector('#shown-count');
 const norm=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr').replace(/[’']/g,' ');
 const escapeHTML=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 let data,filtered=[],visible=18;
 query.value=params.get('q')||params.get('recherche')||'';
 kind.value=['post','page'].includes(params.get('type'))?params.get('type'):'all';
 function syncURL(){
  const p=new URLSearchParams();if(query.value.trim())p.set('q',query.value.trim());if(kind.value!=='all')p.set('type',kind.value);if(category.value)p.set('categorie',category.value);if(year.value)p.set('annee',year.value);
  history.replaceState(null,'',location.pathname+(p.size?'?'+p.toString():''));
 }
 function render(){
  const selected=filtered.slice(0,visible);
  results.innerHTML=selected.map(item=>{
   const isPost=item.kind==='post';const d=isPost&&item.date?new Date(item.date):null;const date=d&&!Number.isNaN(d.getTime())?d.toLocaleDateString('fr-FR',{day:'numeric',month:'long',year:'numeric'}):'';
   const excerpt=(item.excerpt||'').replace(/\[&hellip;\]|\[\.\.\.\]/g,'').trim();
   return `<article class="directory-card"><a href="${escapeHTML(item.url)}"><span class="result-kind">${isPost?'La vie du centre':'Rubrique & activité'}</span><h3>${escapeHTML(item.title)}</h3>${excerpt?`<p>${escapeHTML(excerpt.length>180?excerpt.slice(0,177)+'…':excerpt)}</p>`:''}<span class="result-bottom">${isPost?`<time datetime="${escapeHTML(item.date.slice(0,10))}">${escapeHTML(date)}</time>`:'Découvrir la rubrique'}<span class="result-arrow" aria-hidden="true">→</span></span></a></article>`;
  }).join('');
  if(!filtered.length)results.innerHTML='<div class="directory-empty"><h3>Aucun résultat pour ces critères.</h3><p>Essayez un autre mot ou élargissez les filtres.</p><p>Besoin d’un coup de main ? <a href="/#contact">Contactez l’accueil</a>.</p></div>';
  count.textContent=filtered.length+(filtered.length>1?' contenus à découvrir':' contenu à découvrir');
  shown.textContent=filtered.length?`${selected.length} sur ${filtered.length}`:'';
  more.parentElement.hidden=selected.length>=filtered.length;
 }
 function search(update=true){
  if(!data)return;
  const words=norm(query.value).trim().split(/\s+/).filter(Boolean);
  filtered=HorizonSearch.search(data.items,query.value).filter(item=>{
   if(kind.value!=='all'&&item.kind!==kind.value)return false;
   if(category.value&&!item.categories.includes(Number(category.value)))return false;
   if(year.value&&(item.kind!=='post'||!item.date.startsWith(year.value)))return false;
   return true;
  });
  visible=18;render();if(update)syncURL();
 }
 form.addEventListener('submit',e=>{e.preventDefault();search()});
 let timer;query.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>search(),150)});
 [kind,category,year].forEach(field=>field.addEventListener('change',()=>search()));
 document.querySelector('#reset-search').addEventListener('click',()=>{query.value='';kind.value='all';category.value='';year.value='';search();query.focus()});
 more.addEventListener('click',()=>{visible+=18;render()});
 try{
  data=JSON.parse(document.querySelector('#directory-data').textContent);
  const categories=data.categories.filter(c=>data.items.some(i=>HorizonSearch.isCurrent(i)&&i.categories.includes(c.id))).sort((a,b)=>a.name.localeCompare(b.name,'fr'));
  category.innerHTML='<option value="">Tous les thèmes</option>'+categories.map(c=>`<option value="${c.id}">${escapeHTML(c.name)}</option>`).join('');
  const years=[...new Set(data.items.filter(i=>i.kind==='post'&&HorizonSearch.isCurrent(i)).map(i=>i.date.slice(0,4)))].sort().reverse();
  year.innerHTML='<option value="">Toutes les années</option>'+years.map(y=>`<option value="${y}">${y}</option>`).join('');
  const requestedCategory=params.get('categorie')||params.get('cat');if(requestedCategory&&categories.some(c=>String(c.id)===requestedCategory)){category.value=requestedCategory;kind.value='post'}
  const requestedYear=params.get('annee');if(requestedYear&&years.includes(requestedYear)){year.value=requestedYear;kind.value='post'}
  search(false);
 }catch(error){results.innerHTML='<div class="directory-empty"><h3>Le répertoire ne peut pas s’afficher.</h3><p>Rechargez la page ou <a href="/#contact">contactez l’accueil</a>.</p></div>';count.textContent='';more.parentElement.hidden=true;console.error('Répertoire indisponible',error)}
})();
