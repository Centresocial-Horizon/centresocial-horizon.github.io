#!/usr/bin/env python3
"""Build the public Horizon site from the French editor's JSON files.

No remote request is made. --site-root supports both the Sites dist directory and
an independent GitHub Pages repository. Validation finishes before any output is
written. Source JSON remains the single editorial source; generated HTML and
search metadata are updated together.
"""
from __future__ import annotations
import argparse, calendar, copy, html as H, json, math, re
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit, quote, unquote
from zoneinfo import ZoneInfo
from datetime import datetime
from lxml import html, etree
try:
    from markdown_it import MarkdownIt
except ImportError:
    raise SystemExit('Install the build dependencies from requirements-editor.txt first.')

OLD_HOSTS={'centresocial-horizon.fr','www.centresocial-horizon.fr'}
SPECIAL={264:('/salles/',['/contenus/264/']),1343:('/equipe/',['/contenus/1343/']),4429:('/contenus/4429/',[])}
MD=MarkdownIt('commonmark',{'html':True,'linkify':False}).enable('table')


def esc(value): return H.escape(str(value if value is not None else ''),quote=True)
def text(fragment):
    return ' '.join(html.fromstring('<div>'+fragment+'</div>').text_content().split())
def dump(data): return json.dumps(data,ensure_ascii=False,indent=2)+'\n'
def json_script(data): return json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e')
def cutoff(today):
    month=today.month-2; year=today.year
    if month<1: month+=12;year-=1
    return date(year,month,min(today.day,calendar.monthrange(year,month)[1]))
def day(value,field='date'):
    try:return date.fromisoformat(str(value)[:10])
    except (TypeError,ValueError):raise ValueError(f'{field}: date attendue au format AAAA-MM-JJ')
def url(value,*,media=False,empty=False):
    value=str(value or '').strip()
    if not value and empty:return ''
    if not value or any(ord(c)<32 for c in value) or '\\' in value:raise ValueError('Adresse vide ou incorrecte')
    p=urlsplit(value)
    if p.hostname in OLD_HOSTS:raise ValueError('Les liens vers l’ancien site sont interdits : '+value)
    if value.startswith('//'):raise ValueError('Adresse sans protocole interdite : '+value)
    if p.scheme and p.scheme not in ({'https'} if media else {'https','http','mailto','tel'}):raise ValueError('Protocole interdit : '+value)
    if not p.scheme and not value.startswith(('/','#')):raise ValueError('Utiliser une adresse locale commençant par / : '+value)
    if any(part=='..' for part in unquote(p.path).split('/')):raise ValueError('Chemin parent interdit')
    return value

def route(value):
    value=url(value)
    if not value.startswith('/') or value.startswith('//') or urlsplit(value).query or urlsplit(value).fragment or not value.endswith('/') or value=='/':raise ValueError('Chemin de page incorrect : '+value)
    if value.split('/')[1] in {'admin','edition','assets','uploads','media','documents','data','tout-horizon'}:raise ValueError('Chemin de page réservé : '+value)
    return value

def safe_html(fragment):
    """Allow editorial formatting, never scripts or executable attributes."""
    root=html.fragment_fromstring(fragment or '<p></p>',create_parent='div')
    for node in list(root.iterdescendants()):
        tag=node.tag.lower() if isinstance(node.tag,str) else ''
        if tag in {'script','style','object','embed','form','input','button','textarea','select','base','meta','link','svg','math'}:
            node.drop_tree();continue
        if tag=='iframe' and not (node.get('src','').startswith(('/documents/','/media/','/uploads/')) and node.get('src','').split('?')[0].lower().endswith('.pdf')):
            node.drop_tree();continue
        for attr in list(node.attrib):
            if attr.lower().startswith('on') or attr.lower() in {'srcdoc','style'}:del node.attrib[attr]
            elif attr in {'href','src','poster','action','data'}:
                try:node.set(attr,url(node.get(attr),media=attr!='href'))
                except ValueError:del node.attrib[attr]
        if tag=='a' and node.get('target')=='_blank':node.set('rel','noopener noreferrer')
    return (H.escape(root.text or '')+''.join(etree.tostring(c,encoding='unicode',method='html') for c in root))

def markdown(value):return safe_html(MD.render(str(value or '')))
def euro(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:raise ValueError('Un tarif doit être un nombre positif ou nul')
    return f'{value:g}'.replace('.',',')+' €'
def set_html(node,fragment):
    for c in list(node):node.remove(c)
    node.text=''
    for part in html.fragments_fromstring(fragment):
        if isinstance(part,str):node.text=(node.text or '')+part
        else:node.append(part)
def set_text(node,value):
    for c in list(node):node.remove(c)
    node.text=str(value or '')
def initials(name):return ''.join(p[0] for p in str(name).split()[:2]).upper()


class Builder:
    def __init__(self,root,today):
        self.root=Path(root);self.today=today;self.limit=cutoff(today);self.output={};self.documents={}
        self.original=json.loads((self.root/'content-index.json').read_text())
        self.items={str(i['id']):copy.deepcopy(i) for i in self.original['items']}
        self.edition=self.root/'edition';self.manifest={};self.records=[]
        self.previous=json.loads((self.edition/'.generated.json').read_text()) if (self.edition/'.generated.json').exists() else {}
        self.template=(self.root/'contenus/239/index.html').read_text()
    def read(self,name):return json.loads((self.edition/name).read_text())
    def doc(self,path):
        path=Path(path)
        if path not in self.documents:
            file=self.root/path
            self.documents[path]=html.fromstring(file.read_text() if file.exists() else self.template)
        return self.documents[path]
    def page(self,where,title,content,*,published=True,story_date=None):
        where=route(where);path=Path(where.lstrip('/'))/'index.html';tree=self.doc(path)
        for robots in tree.xpath('//meta[@name="robots"]'):robots.drop_tree()
        if not published:
            content='<div class="document-help"><h2>Ce contenu n’est plus affiché.</h2><p>Retrouvez les informations actuelles du centre dans toutes les rubriques.</p><a href="/tout-horizon/">Consulter les informations actuelles →</a></div>'
            tree.xpath('//head')[0].append(etree.Element('meta',name='robots',content='noindex,follow'))
        block=tree.xpath('//div[@class="migrated-content"]')[0];set_html(block,content)
        headings=tree.xpath('//section[contains(concat(" ",normalize-space(@class)," ")," content-heading ")]/h1')
        if headings:set_text(headings[0],title)
        set_text(tree.xpath('//title')[0],title+' — Horizon Cholet')
        description=tree.xpath('//meta[@name="description"]')
        if description:description[0].set('content',text(content)[:180])
        for node in tree.xpath('//*[@data-story-date]'):node.attrib.pop('data-story-date',None)
        times=tree.xpath('//section[contains(@class,"content-heading")]/time')
        for node in times:node.drop_tree()
        if story_date:
            tree.xpath('//main')[0].set('data-story-date',story_date)
            heading=tree.xpath('//section[contains(@class,"content-heading")]')[0]
            time=etree.SubElement(heading,'time',datetime=story_date);time.text=day(story_date).strftime('%d/%m/%Y')
        self.output[path]=None
        return tree
    def register(self,key,title,where,content,*,kind='page',source=None,published=True):
        old=self.items.get(str(key),{})
        item={**old,**{k:v for k,v in (source or {}).items() if k in ['date','parent','categories','sectors','sectorLanding','tags','expiresOn']},
              'id':key,'title':str(title),'url':where,'kind':kind,'excerpt':str((source or {}).get('excerpt') or text(content)[:280]),'searchText':text(content),'retired':not published}
        item.setdefault('date',self.today.isoformat());item.setdefault('categories',[]);item.setdefault('tags',[]);item.setdefault('sectors',[]);item.setdefault('parent',0)
        self.items[str(key)]=item
    def active(self,r,kind):
        if r.get('published',True) is False:return False
        if kind=='post':return self.limit<=day(r.get('date'),r.get('title','date'))<=self.today
        return True
    def record_pages(self):
        occupied={p for primary,aliases in SPECIAL.values() for p in [primary]+aliases}
        for folder,kind,prefix in [('pages','page','rubriques'),('actualites','post','actualites')]:
            for file in sorted((self.edition/folder).glob('*.json')):
                r=json.loads(file.read_text());stem=file.stem
                if not str(r.get('title','')).strip():raise ValueError(file.name+' : titre obligatoire')
                canonical=route(r.get('route') or '/'+prefix+'/'+stem+'/')
                aliases=[route(a) for a in r.get('aliases',[]) if a!=canonical]
                for p in [canonical]+aliases:
                    if p in occupied:raise ValueError('Deux contenus utilisent '+p)
                    occupied.add(p)
                r={**r,'route':canonical,'aliases':aliases,'id':r.get('id') or f'cms:{folder}:{stem}','_folder':folder,'_stem':stem}
                active=self.active(r,kind);body=markdown(r.get('body',''))
                for p in [canonical]+aliases:self.page(p,r['title'],body,published=active,story_date=str(r['date'])[:10] if kind=='post' and active else None)
                self.register(r['id'],r['title'],canonical,body,kind=kind,source=r,published=active)
                self.records.append(r);self.manifest[str(r['id'])]={'routes':[canonical]+aliases,'title':r['title']}
        # A deleted editor record must not leave its formerly published page available.
        for key,entry in self.previous.items():
            if key not in self.manifest:
                for p in entry['routes']:self.page(p,entry.get('title','Contenu indisponible'),'',published=False)
                if key in self.items:self.items[key]['retired']=True
        # Do not resurrect old WordPress news absent from the editor.
        for item in self.items.values():
            if item['kind']=='post' and (not item.get('date') or not self.limit<=day(item['date'])<=self.today):item['retired']=True
    def team(self):
        data=self.read('equipe.json');members=data.get('members',[])
        if not isinstance(members,list):raise ValueError('Liste d’équipe incorrecte')
        def cards(subset):
            result='<div class="team-grid">'
            for m in subset:
                if not str(m.get('name','')).strip() or not str(m.get('role','')).strip():raise ValueError('Chaque membre doit avoir un nom et un poste')
                avatar='<img class="team-portrait" src="'+esc(url(m['photo'],media=True))+'" alt="" loading="lazy" width="96" height="96">' if m.get('photo') else '<span class="team-initials" aria-hidden="true">'+esc(initials(m['name']))+'</span>'
                result+='<article class="team-card">'+avatar+'<h3>'+esc(m['name'])+'</h3><p>'+esc(m['role'])+'</p></article>'
            return result+'</div>'
        content='<p>'+esc(data.get('intro',''))+'</p>'+cards(members)
        for p in ['/equipe/','/contenus/1343/']:self.page(p,'L’équipe du centre social Horizon',content)
        self.register(1343,'L’équipe du centre social Horizon','/equipe/',content,source={'sectors':['equipe'],'tags':[m['name'] for m in members]+['équipe']})
        home=self.doc('index.html');old=home.xpath('//*[@id="equipe"]//div[contains(@class,"team-grid")]')
        if old:old[0].getparent().replace(old[0],html.fromstring(cards(members)))
        for p in ['/jeunesse/','/contenus/336/']:
            tree=self.doc(Path(p.lstrip('/'))/'index.html')
            for old in tree.xpath('//div[@class="migrated-content"]//div[contains(@class,"team-grid")]'):
                old.getparent().replace(old,html.fromstring(cards([m for m in members if 'jeunesse' in m['role'].lower()])))
    def rentals(self):
        r=self.read('salles.json');photos=r.get('photos',{})
        for row in r['salles']:
            for k in ['secteur','horsSecteur','cautionSecteur','cautionHorsSecteur']:euro(row[k])
            if row.get('capacite') is not None and (not isinstance(row['capacite'],int) or row['capacite']<1):raise ValueError('Capacité de salle incorrecte')
        for dish in r['vaisselle']:euro(dish['prix'])
        euro(r['preparation']['prixParSalle'])
        names=list(dict.fromkeys(row['salle'] for row in r['salles']))
        gallery='<section id="salles-en-images" aria-labelledby="room-gallery-title"><h2 id="room-gallery-title">Les salles en images</h2><p>Découvrez les espaces du centre. Cliquez sur une photo pour l’agrandir.</p><div class="room-gallery">'
        tables='';homecards='';alerts=''
        for name in names:
            rows=[row for row in r['salles'] if row['salle']==name];opened=any(row.get('disponible') for row in rows)
            key='bora' if name=='Bora-Bora' else 'belle';src=url(photos.get(key) or '/assets/salle-'+('bora-bora' if key=='bora' else 'belle-ile')+'.jpg',media=True)
            alt=str(photos.get(key+'Alt') or 'La salle '+name+(' avant travaux' if not opened else ''))
            caption='Vue de la salle.' if opened else 'Photo avant travaux — salle actuellement indisponible.'
            picture='<img src="'+esc(src)+'" alt="'+esc(alt)+'" loading="lazy" decoding="async">'
            gallery+='<figure><a class="room-gallery-photo" href="'+esc(src)+'" target="_blank" rel="noopener noreferrer" aria-label="Agrandir la photo de '+esc(name)+' (nouvel onglet)">'+picture+'</a><figcaption><strong>'+esc(name)+'</strong>'+caption+'</figcaption></figure>'
            if not opened:alerts+='<div class="rental-alert"><strong>'+esc(name)+' : indisponible pendant les travaux.</strong><p>La salle ne peut pas être louée pour le moment. Aucune réservation n’est possible jusqu’à sa réouverture. Les tarifs sont donnés à titre d’information.</p></div>'
            cap=name+(' — location à la journée de '+str(r['horairesJournee']) if opened else ' — indisponible pendant les travaux. Tarifs indicatifs à la journée')
            tables+='<h3>'+esc(name)+(' <span class="room-status">Indisponible — travaux</span>' if not opened else '')+'</h3><div class="tariff-scroll" role="region" tabindex="0" aria-label="'+esc(cap)+'"><table class="tariff-table"><caption>'+esc(cap)+'</caption><thead><tr><th scope="col">Formule</th><th scope="col">Location<br>secteur</th><th scope="col">Location<br>hors secteur</th><th scope="col">Caution<br>secteur</th><th scope="col">Caution<br>hors secteur</th></tr></thead><tbody>'
            for row in rows:
                tables+='<tr'+(' class="unavailable-rate"' if not row.get('disponible') else '')+'><th scope="row">'+esc(row['formule'])+('<small>'+str(row['capacite'])+' personnes maximum</small>' if row.get('capacite') else '')+'</th>'+''.join('<td>'+euro(row[k])+'</td>' for k in ['secteur','horsSecteur','cautionSecteur','cautionHorsSecteur'])+'</tr>'
            tables+='</tbody></table></div>'
            status='Location — renseignements à l’accueil' if opened else 'Indisponible — travaux en cours'
            desc='Pour vos réunions et vos événements, avec ou sans cuisine.' if opened else 'La salle ne peut pas être louée pour le moment. Aucune réservation n’est possible pendant les travaux.'
            price=min(row['secteur'] for row in rows if row.get('disponible')) if opened else None
            homecards+='<article class="room-home-card'+(' room-unavailable' if not opened else '')+'"><figure class="room-home-photo"><a href="/salles/#salles-en-images">'+picture+'</a>'+('<figcaption>Photo avant travaux</figcaption>' if not opened else '')+'</figure><span class="room-home-status">'+status+'</span><h3>Salle '+esc(name)+'</h3><p>'+desc+'</p>'+('<div class="room-home-prices"><strong>Dès '+euro(price)+' <small>/ journée</small></strong><span>Tarif secteur · '+esc(r['horairesJournee'])+'</span></div>' if opened else '<p>Tarifs consultables à titre d’information.</p>')+'<a class="'+('button' if opened else 'text-link')+'" href="/salles/#tarifs">'+('Voir les formules et tarifs →' if opened else 'Informations et tarifs →')+'</a></article>'
        gallery+='</div></section>'
        dishes=''.join('<tr><th scope="row">'+esc(v['article'])+'</th><td>'+esc(v['quantite'])+'</td><td>'+euro(v['prix'])+'</td></tr>' for v in r['vaisselle'])
        prep=r['preparation'];conditions=''.join('<li>'+esc(c)+'</li>' for c in r['conditions'])
        content='<p>Une réunion, une fête de famille ou un événement associatif ? Retrouvez ici les formules, les tarifs et les démarches pour louer une salle à Horizon.</p>'+alerts+gallery+'<section id="tarifs"><h2>Les tarifs de location</h2><p>Journée de <strong>'+esc(r['horairesJournee'])+'</strong>. Le prix de la location et la caution sont indiqués séparément.</p>'+tables+'<p class="tariff-note">Pour connaître le tarif secteur qui vous concerne et les conditions de la caution, contactez l’accueil. '+esc(r.get('reveillons',''))+'</p></section><section id="preparation"><h2>Préparer votre événement</h2><p><strong>'+euro(prep['prixParSalle'])+' par salle</strong>, '+esc(prep['jour'])+' de <strong>'+esc(prep['horaires'])+'</strong>, pour la préparation. Cette possibilité concerne uniquement les salles ouvertes à la location.</p></section><section id="vaisselle"><h2>La location de vaisselle</h2><table class="dish-table"><caption>Prix par lot de 50 pièces</caption><thead><tr><th scope="col">Vaisselle</th><th scope="col">Quantité</th><th scope="col">Tarif</th></tr></thead><tbody>'+dishes+'</tbody></table></section><section id="reserver"><h2>Comment réserver ?</h2><ol>'+conditions+'</ol><p><a class="button" href="tel:'+esc(self.phone_href)+'">Appeler l’accueil — '+esc(self.hours['phone'])+'</a></p><p><a href="mailto:'+esc(self.hours['email'])+'">Écrire à l’accueil</a> · <a href="/#contact">Horaires et accès</a></p></section>'
        for p in ['/salles/','/contenus/264/']:self.page(p,'Location de salles et tarifs',content)
        self.register(264,'Location de salles et tarifs','/salles/',content,source={'sectors':['salles'],'tags':['location','tarif','prix','caution','Bora-Bora','Belle-Île','cuisine','vaisselle','réservation']})
        for node in self.doc('index.html').xpath('//*[@id="location-salles"]//div[@class="room-home-grid"]'):set_html(node,homecards)
        self.output[Path('data/salles-tarifs.json')]=dump(r)
    def contact(self):
        r=self.read('horaires.json');self.hours=r;self.phone_href=re.sub(r'[^+0-9]','',r['phone'])
        if self.phone_href.startswith('0'):self.phone_href='+33'+self.phone_href[1:]
        if not re.fullmatch(r'\+?[0-9]{6,16}',self.phone_href):raise ValueError('Numéro de téléphone incorrect')
        if not re.fullmatch(r'[^\s<>@]+@[^\s<>@]+\.[^\s<>@]+',r['email']):raise ValueError('Adresse e-mail incorrecte')
        rows=''.join('<div><dt>'+esc(h['label'])+'</dt><dd>'+esc(h['hours'])+'</dd></div>' for h in r['openingHours'])
        home=self.doc('index.html')
        for node in home.xpath('//*[@id="infos"]//div[@class="hours"]/dl'):set_html(node,rows)
        for node in home.xpath('//*[@id="infos"]//p[@class="address"]/span'):set_html(node,'<br>'.join(esc(line) for line in r['address'].splitlines()))
        body='<h2>Les horaires de l’accueil</h2><dl class="cms-opening-hours">'+rows+'</dl><h2>Venir au centre</h2><p>'+esc(r['address'])+'</p><p><a href="tel:'+esc(self.phone_href)+'">'+esc(r['phone'])+'</a><br><a href="mailto:'+esc(r['email'])+'">'+esc(r['email'])+'</a></p><h2>Nous joindre par secteur</h2>'
        # Preserve the other published sector contacts while the main reception is editable.
        for label,email in [('Direction','direction'),('Comptabilité','comptable'),('Seniors','senior'),('Jeunesse','jeunesse'),('Famille','famille'),('Numérique','numerique')]:body+='<p>'+label+' : <a href="mailto:'+email+'@centresocial-horizon.fr">'+email+'@centresocial-horizon.fr</a></p>'
        body+='<p><a href="https://www.google.com/maps/search/?api=1&amp;query='+quote(r['address'])+'" target="_blank" rel="noopener noreferrer">Voir l’itinéraire →</a></p>'
        self.page('/contenus/4429/','Horaires, accès et contact',body);self.register(4429,'Horaires, accès et contact','/contenus/4429/',body)
        youth=r.get('youth',{})
        for p in ['/jeunesse/','/contenus/336/']:
            tree=self.doc(Path(p.lstrip('/'))/'index.html');block=tree.xpath('//div[@class="migrated-content"]')[0]
            for heading in block.xpath('./h2'):
                if 'Hors vacances' in heading.text_content():
                    nxt=heading.getnext()
                    if nxt is not None and nxt.tag in {'p','table','div'}:nxt.getparent().replace(nxt,html.fromstring('<p>'+esc(youth.get('outside',''))+'</p>'))
                elif 'Pendant les vacances' in heading.text_content():
                    nxt=heading.getnext()
                    if nxt is not None and nxt.tag=='p':set_text(nxt,youth.get('holidays',''))
    def programmes(self):
        all_programmes=[];active=[]
        sectors={'jeunesse':336,'famille':4108,'seniors':2564}
        for file in sorted((self.edition/'programmes').glob('*.json')):
            r=json.loads(file.read_text());r['id']=r.get('id') or 'cms:programmes:'+file.stem;r['route']=route(r.get('route') or '/programmes/'+file.stem+'/')
            if not r.get('title'):raise ValueError('Un programme doit avoir un titre')
            r['pdf']=url(r.get('pdf'),media=True)
            if not urlsplit(r['pdf']).path.lower().endswith('.pdf'):raise ValueError('Le programme doit être un fichier PDF')
            start=day(r.get('date'));end=day(r['fin']) if r.get('fin') else start
            visible=r.get('published',True) is not False and start<=self.today and end>=self.limit
            body=markdown(r.get('description',''))+'<p><a class="button" href="'+esc(r['pdf'])+'" target="_blank" rel="noopener noreferrer">Télécharger '+esc(r['title'])+' — PDF ↗</a></p>'
            self.page(r['route'],r['title'],body,published=visible)
            sector=str(r.get('secteur','')).lower()
            source={'date':start.isoformat(),'expiresOn':end.isoformat(),'sectors':[sector] if sector in sectors else [],'tags':['programme',sector],'excerpt':text(markdown(r.get('description','')))[:280]}
            self.register(r['id'],r['title'],r['route'],body,source=source,published=visible)
            self.manifest[str(r['id'])]={'routes':[r['route']],'title':r['title']}
            if visible:active.append(r)
            all_programmes.append(r)
        listing='<p>Les programmes disponibles au centre, avec leurs documents à télécharger.</p>'
        if active:
            listing+='<div class="topic-links">'+''.join('<a href="'+esc(r['route'])+'">'+esc(r['title'])+' →</a>' for r in active)+'</div>'
        else:listing+='<p>Aucun nouveau programme n’est publié ici pour le moment. Contactez l’accueil pour connaître les prochaines activités.</p>'
        self.page('/programmes/','Les programmes à télécharger',listing)
        self.register('cms:programmes','Les programmes à télécharger','/programmes/',listing,source={'tags':['programme','vacances'],'sectors':[]})
        home=self.doc('index.html')
        for old in home.xpath('//*[@id="programmes"]'):old.drop_tree()
        if active:
            section=html.fromstring('<section class="section container cms-programmes" id="programmes"><div class="section-heading"><h2>Les programmes à télécharger</h2></div>'+listing+'</section>')
            activities=home.xpath('//*[@id="activites"]')
            if activities:activities[0].addprevious(section)
        for sector,ident in sectors.items():
            related=[r for r in active if str(r.get('secteur','')).lower() in {sector,'tout public','tous publics','toutpublic'}]
            for rec in self.records:
                if str(rec['id'])!=str(ident):continue
                for p in [rec['route']]+rec.get('aliases',[]):
                    block=self.doc(Path(p.lstrip('/'))/'index.html').xpath('//div[@class="migrated-content"]')[0]
                    for old in block.xpath('.//section[contains(@class,"cms-programmes")]'):old.drop_tree()
                    if related:block.append(html.fromstring('<section class="cms-programmes"><h2>Les programmes du secteur</h2><div class="topic-links">'+''.join('<a href="'+esc(r['route'])+'">'+esc(r['title'])+' →</a>' for r in related)+'</div></section>'))
        # Programmes also participate in deletion retirement, after they are known.
        for key,entry in self.previous.items():
            if key.startswith('cms:programmes:') and key not in self.manifest:
                for p in entry['routes']:self.page(p,entry.get('title','Programme indisponible'),'',published=False)
                if key in self.items:self.items[key]['retired']=True
    def homepage(self):
        r=self.read('accueil.json');tree=self.doc('index.html')
        for node in tree.xpath('//div[@class="hero-copy"]/h1'):
            second=str(r.get('heroLine2',''))
            if second.startswith('Des liens '):
                ending='.' if second.endswith('.') else ''
                second='Des liens <span class="underline">'+esc(second[len('Des liens '):].removesuffix('.'))+'<svg viewBox="0 0 420 20" preserveAspectRatio="none" aria-hidden="true"><path d="M4 13Q180 0 413 8M40 18Q205 7 380 13"></path></svg></span>'+ending
            else:second=esc(second)
            set_html(node,esc(r.get('heroLine1',''))+'<br>'+second)
        for node in tree.xpath('//div[@class="hero-copy"]/p'):set_text(node,r.get('heroIntro',''))
        for node in tree.xpath('//img[contains(@class,"hero-photo")]'):
            node.set('src',url(r.get('heroPhoto'),media=True));node.set('alt',str(r.get('heroPhotoAlt','')))
        for node in tree.xpath('//*[@id="news-title"]'):set_html(node,esc(r.get('newsTitle','La vie du centre'))+'<span class="coral">.</span>')
        # Home uses current news first, with explicitly selected permanent activities as a fallback.
        posts=[n for n in self.records if n['_folder']=='actualites' and self.active(n,'post')]
        selected=sorted([n for n in posts if n.get('home')],key=lambda n:str(n.get('date','')),reverse=True)+sorted([n for n in posts if not n.get('home')],key=lambda n:str(n.get('date','')),reverse=True)
        pinned=[n for n in self.records if n['_folder']=='pages' and n.get('home') and n.get('published',True)]
        selected=(selected+pinned)[:3]
        cards=''
        for n in selected:
            image=url(n.get('image'),media=True,empty=True)
            visual=('<img src="'+esc(image)+'" alt="'+esc(n.get('imageAlt') or n['title'])+'" loading="eager" fetchpriority="high">' if image else '<span class="cms-news-placeholder" aria-hidden="true">Horizon</span>')
            recent=n['_folder']=='actualites';when=str(n.get('date',''))[:10]
            cards+='<article class="news-card"'+(' data-published-on="'+esc(when)+'"' if recent else '')+'><a href="'+esc(n['route'])+'" class="news-image">'+visual+'</a><div class="news-content">'+('<time datetime="'+esc(when)+'">'+day(when).strftime('%d/%m/%Y')+'</time>' if recent else '<span class="news-date">À découvrir toute l’année</span>')+'<h3><a href="'+esc(n['route'])+'">'+esc(n['title'])+'</a></h3><p>'+esc(n.get('excerpt') or text(markdown(n.get('body','')))[:150])+'</p><a class="text-link" href="'+esc(n['route'])+'">Découvrir →</a></div></article>'
        grid=tree.xpath('//*[@id="actualites"]//div[@class="news-grid"]')
        if grid:set_html(grid[0],cards or '<p>Retrouvez bientôt les prochaines nouvelles du centre.</p>')
        main=tree.xpath('//main')[0];news=tree.xpath('//*[@id="actualites"]')[0]
        news.getparent().remove(news);main.insert(0,news)
    def globals(self):
        social=self.read('reseaux.json');links=social.get('links',[])
        for entry in links:url(entry['url'])
        # Update every generated and retained page, so phone/email/footer do not diverge.
        paths=set(self.root.rglob('*.html'))
        paths={p.relative_to(self.root) for p in paths if not {'admin','edition'}.intersection(p.relative_to(self.root).parts)}|set(self.documents)
        for path in paths:
            tree=self.doc(path)
            head=tree.xpath('//head')[0]
            if not tree.xpath('//link[@href="/editor-content.css"]'):
                css=etree.Element('link',rel='stylesheet',href='/editor-content.css')
                final=tree.xpath('//link[@href="/frontpage.css"]')
                if final:final[0].addprevious(css)
                else:head.append(css)
            for node in tree.xpath('//a[starts-with(@href,"tel:")]'):
                if node.get('data-contact')=='phone' or re.sub(r'[^0-9]','',node.get('href','')) in {'33241651388','0241651388'}:
                    node.set('href','tel:'+self.phone_href)
                    node.set('data-contact','phone')
                    for c in list(node):
                        if c.tag!='svg':node.remove(c)
                    svg=node.find('svg')
                    if svg is not None:svg.tail=self.hours['phone']
                    else:node.text=self.hours['phone']
            for node in tree.xpath('//a[@href="mailto:accueil@centresocial-horizon.fr" or @data-contact="email"]'):
                node.set('href','mailto:'+self.hours['email'])
                if 'accueil@' in node.text_content() or node.get('data-contact')=='email-address':set_text(node,self.hours['email']);node.set('data-contact','email-address')
                elif node.get('data-contact')!='email-address':node.set('data-contact','email')
            for node in tree.xpath('//a[@data-contact="email-address"]'):
                node.set('href','mailto:'+self.hours['email']);set_text(node,self.hours['email'])
            for node in tree.xpath('//a[contains(@href,"google.com/maps/search/")]'):
                node.set('href','https://www.google.com/maps/search/?api=1&query='+quote(self.hours['address']))
            for footer in tree.xpath('//div[contains(concat(" ",normalize-space(@class)," ")," footer-socials ")]'):
                set_html(footer,''.join('<a href="'+esc(x['url'])+'" target="_blank" rel="noopener noreferrer">'+esc(x['label'])+' ↗</a>' for x in links))
            for block in tree.xpath('//*[@id="reseaux"]//div[@class="social-links"]'):
                set_html(block,''.join('<a href="'+esc(x['url'])+'" target="_blank" rel="noopener noreferrer"><strong>'+esc(x['label'])+' ↗</strong></a>' for x in links))
            self.output[path]=None
    def index(self):
        # Re-extract final HTML, including structured team, hours, tariffs and programme links.
        records={str(r['id']):r for r in self.records}
        for item in self.items.values():
            if item.get('retired'):continue
            path=Path(item['url'].lstrip('/'))/'index.html'
            if path in self.documents:
                blocks=self.documents[path].xpath('//div[@class="migrated-content"]')
                if blocks:item['searchText']=' '.join(blocks[0].text_content().split())
            # Imported PDF contents are retained separately from the editable prose.
            document_text=records.get(str(item['id']),{}).get('documentText','')
            if document_text:item['searchText']+=' '+' '.join(str(document_text).split())
        data={**self.original,'items':list(self.items.values())}
        self.output[Path('content-index.json')]=dump(data)
        tree=self.doc('tout-horizon/index.html')
        for node in tree.xpath('//script[@id="directory-data"]'):node.text=json_script(data)
        current=[i for i in data['items'] if not i.get('retired') and (i['kind']!='post' or self.limit<=day(i['date'])<=self.today)]
        cards=''.join('<article class="directory-card"><a href="'+esc(i['url'])+'"><span class="result-kind">'+('La vie du centre' if i['kind']=='post' else 'Rubrique & activité')+'</span><h3>'+esc(i['title'])+'</h3><span class="result-bottom">Découvrir →</span></a></article>' for i in current[:18])
        for node in tree.xpath('//*[@id="result-list"]'):set_html(node,cards)
        for node in tree.xpath('//noscript//div[@class="noscript-links"]'):set_html(node,''.join('<a href="'+esc(i['url'])+'">'+esc(i['title'])+'</a>' for i in current[18:]))
        self.output[Path('tout-horizon/index.html')]=None
    def build(self):
        self.record_pages();self.contact();self.team();self.rentals();self.programmes();self.homepage();self.globals();self.index()
        self.output[Path('edition/.generated.json')]=dump(self.manifest)
        # Finish all validation and serialization before writing any changed output.
        for path,tree in self.documents.items():self.output[path]='<!doctype html>'+etree.tostring(tree,encoding='unicode',method='html')
        changed=0
        for path,body in self.output.items():
            if body is None:continue
            target=self.root/path;data=body.encode()
            if not target.exists() or target.read_bytes()!=data:
                target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);changed+=1
        return {'records':len(self.records),'pages_written':changed,'date':self.today.isoformat(),'cutoff':self.limit.isoformat()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-root',type=Path,default=Path(__file__).resolve().parents[1]/'dist')
    parser.add_argument('--today',help='Explicit date for reproducible validation (AAAA-MM-JJ)')
    args=parser.parse_args();today=day(args.today) if args.today else datetime.now(ZoneInfo('Europe/Paris')).date()
    try:print(json.dumps(Builder(args.site_root,today).build(),ensure_ascii=False))
    except (ValueError,KeyError,TypeError) as exc:raise SystemExit('Publication interrompue : '+str(exc))
if __name__=='__main__':main()
