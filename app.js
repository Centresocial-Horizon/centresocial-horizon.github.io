'use strict';
const contentHref = id => ({336:"/jeunesse/",1343:"/equipe/",4108:"/famille/",2564:"/seniors/",324:"/clas-primaire/",264:"/salles/"}[id] || `/contenus/${id}/`);
const activities = [
 {id:'famille', title:'En famille', icon:'heart', color:'green', groups:['famille'], desc:'Grandir ensemble, s’amuser et partager de beaux moments.', label:'Des moments à partager', page:4108, text:'Des activités pour se retrouver entre parents et enfants : les Mercredis Animés, le Thé des parents, les sorties et les propositions pendant les vacances.', info:'Les Mercredis Animés accueillent les parents et leurs enfants de 0 à 10 ans, de 15 h à 17 h. Inscription auprès de l’accueil.'},
 {id:'jeunesse', title:'Jeunesse', icon:'sun', color:'peach', groups:['jeunesse'], desc:'Des projets, des sorties et un espace pour être soi.', label:'Faire le plein de découvertes', page:336, text:'L’Espace Ados propose des temps d’accueil, des loisirs et des projets à construire avec les jeunes. Retrouvez ici les programmes des vacances et les projets du secteur jeunesse.', info:'Hors vacances : mercredi et samedi de 14 h à 18 h ; vendredi de 17 h à 21 h 30. Pendant les vacances, les créneaux varient, généralement le mercredi et le jeudi après-midi. Renseignez-vous auprès de l’équipe jeunesse.'},
 {id:'adultes', title:'Adultes & seniors', icon:'people', color:'blue', groups:['adultes'], desc:'Bouger, échanger et cultiver le plaisir d’être ensemble.', label:'Du lien au quotidien', page:2564, text:'Ensemble vocal, gym d’entretien, Joyeux retraités, Café Particip’Age et réseau d’entraide : de multiples occasions de se rencontrer et de partager.', info:'Café Particip’Age + Mémoire : le jeudi de 14 h à 16 h, tous les quinze jours. Prochaines dates et inscription auprès de l’accueil.'},
 {id:'savoirs', title:'Échanges de savoirs', icon:'spark', color:'yellow', groups:['adultes','famille','jeunesse'], desc:'Couture, cuisine, langues… Et si on apprenait les uns des autres ?', label:'Apprendre & transmettre', page:61, text:'Partagez vos savoir-faire et découvrez ceux des autres : couture, cuisine, langues, art floral, danse, informatique, randonnées ou robotique.', info:'Les inscriptions sont annuelles et l’adhésion au centre est nécessaire. Certaines activités ont un nombre de places limité. Contactez l’accueil pour les horaires, les tarifs et les âges concernés.'},
 {id:'mercredis', title:'Les Mercredis Animés', icon:'sun', color:'peach', groups:['famille'], desc:'Un moment complice pour les parents et les enfants de 0 à 10 ans.', label:'Jouer & découvrir ensemble', page:3060, text:'Des animations à vivre en famille pour prendre le temps de jouer, de créer et de se rencontrer.', info:'De 15 h à 17 h. Pour les enfants de 0 à 10 ans accompagnés de leurs parents. Dates et inscription à l’accueil.'},
 {id:'clas-primaire',title:'CLAS primaire',icon:'book',color:'blue',groups:['famille'],desc:'Du CP au CM2, un accompagnement pour apprendre et prendre confiance.',label:'Grandir avec confiance',page:324,text:'Le CLAS primaire accompagne les enfants du CP au CM2 avec de l’aide aux devoirs et des activités d’éveil, aux côtés des familles et de l’école.',info:'Hors vacances scolaires : lundi 16 h 45–18 h 15 et mercredi 10 h–12 h, d’octobre à juin. Inscription sur rendez-vous auprès d’Hélène MIRANDA.'},
 {id:'lecture', title:'Bibliothèque Tire-Lire', icon:'book', color:'blue', groups:['famille','jeunesse','adultes'], desc:'Le plaisir de lire, des découvertes et des livres à emprunter.', label:'Des histoires à partager', page:269, text:'Une bibliothèque de proximité pour trouver sa prochaine lecture et découvrir les coups de cœur de Tire-Lire. Le prêt de livres est gratuit.', info:'Mardi et jeudi de 16 h à 18 h ; mercredi de 10 h à 12 h.'},
 {id:'numerique', title:'Espace numérique', icon:'spark', color:'green', groups:['jeunesse','adultes'], desc:'Prendre confiance avec son smartphone ou son ordinateur.', label:'Avancer à son rythme', page:5244, text:'Un espace pour vous accompagner dans les usages du numérique. Retrouvez les informations et les ateliers proposés dans notre rubrique numérique.', info:'Pour connaître les créneaux et modalités : 02 41 62 63 07.'}
];
const grid = document.querySelector('#activity-grid');
function renderActivities(filter='all') {
 const visible = filter==='all' ? activities.slice(0,4) : activities.filter(a=>a.groups.includes(filter));
 grid.innerHTML = visible.map(a=>`<button class="activity-card" data-activity="${a.id}" data-color="${a.color}" aria-label="Découvrir : ${a.title}"><span class="activity-icon"><svg class="icon" aria-hidden="true"><use href="#${a.icon}"/></svg></span><span class="activity-title">${a.title}</span><span class="activity-description">${a.desc}</span><span class="card-bottom"><span>${a.label}</span><span aria-hidden="true">↗</span></span></button>`).join('');
}
renderActivities();
document.querySelectorAll('.filter').forEach(button=>button.addEventListener('click',()=>{
 document.querySelectorAll('.filter').forEach(b=>{b.classList.remove('active');b.setAttribute('aria-pressed','false')});
 button.classList.add('active');button.setAttribute('aria-pressed','true');renderActivities(button.dataset.filter);
}));
const dialog = document.querySelector('#detail-dialog');
let previousFocus;
function openDialog(content){previousFocus=document.activeElement;document.querySelector('#dialog-content').innerHTML=content;dialog.showModal()}
function closeDialog(){dialog.close()}
dialog.querySelector('.dialog-close').addEventListener('click',closeDialog);
dialog.addEventListener('close',()=>previousFocus?.focus());
dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)closeDialog()}});
grid.addEventListener('click',e=>{
 const button=e.target.closest('[data-activity]');if(!button)return;
 const a=activities.find(a=>a.id===button.dataset.activity);
 openDialog(`<div class="dialog-icon"><svg class="icon" aria-hidden="true"><use href="#${a.icon}"/></svg></div><div class="eyebrow">LES ACTIVITÉS D’HORIZON</div><h2 id="dialog-title">${a.title}</h2><p>${a.text}</p><div class="dialog-info">${a.info}</div><div class="dialog-actions"><a class="button" href="${contentHref(a.page)}">Détails et programme <span aria-hidden="true">↗</span></a><a class="text-link" href="tel:+33241651388">Appeler l’accueil ↗</a></div>`);
});
document.querySelectorAll('[data-news="couture"]').forEach(button=>button.addEventListener('click',e=>{
 e.preventDefault();openDialog(`<div class="eyebrow">SOLIDARITÉ · 2 NOVEMBRE 2026</div><h2 id="dialog-title">Des petites mains pour une grande cause</h2><p>Les bénévoles de la commission handicap présentent les créations en couture réalisées au fil de l’année, à l’occasion du Téléthon.</p><p>Venez les rencontrer et découvrir leurs créations aux horaires d’ouverture du Centre Social Horizon.</p><div class="dialog-actions"><a class="button" href="${contentHref(8092)}" id="couture-original">Lire l’article complet ↗</a><a class="text-link" href="tel:+33241651388">Se renseigner ↗</a></div>`);
}));
const menuButton=document.querySelector('.menu-toggle');const nav=document.querySelector('#main-nav');
function closeMenu(){menuButton.setAttribute('aria-expanded','false');menuButton.querySelector('.sr-only').textContent='Ouvrir le menu';nav.classList.remove('open')}
menuButton.addEventListener('click',()=>{const open=menuButton.getAttribute('aria-expanded')!=='true';menuButton.setAttribute('aria-expanded',String(open));menuButton.querySelector('.sr-only').textContent=open?'Fermer le menu':'Ouvrir le menu';nav.classList.toggle('open',open)});
nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMenu));
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeMenu()});
window.matchMedia('(min-width: 1201px)').addEventListener('change',e=>{if(e.matches)closeMenu()});
