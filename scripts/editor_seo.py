"""Generate search metadata from the published Horizon content.

This prepares crawlable pages; it does not submit them to a search engine or
make any promise about indexing or ranking. The origin belongs to the centre.
"""
from pathlib import Path
from urllib.parse import urljoin
import json
from lxml import etree

ORIGIN = 'https://centresocial-horizon.github.io'
SITE_NAME = 'Centre social Horizon'
HOME_TITLE = 'Centre social Horizon à Cholet | Activités et actualités'
HOME_DESCRIPTION = ('Le Centre social et socioculturel Horizon à Cholet : actualités, '
                    'activités jeunesse, familles et seniors, programmes, équipe, '
                    'horaires et location de salles.')


def absolute(path):
    return urljoin(ORIGIN + '/', str(path))


def page_route(path):
    path = Path(path)
    if path.name == 'index.html':
        parent = path.parent.as_posix()
        return '/' if parent == '.' else '/' + parent.strip('/') + '/'
    return '/' + path.as_posix().lstrip('/')


def meta(head, key, value, *, prop=False):
    attr = 'property' if prop else 'name'
    previous = head.xpath('./meta[@' + attr + '="' + key + '"]')
    if previous:
        node = previous[0]
        for duplicate in previous[1:]:
            head.remove(duplicate)
    else:
        node = etree.SubElement(head, 'meta', **{attr: key})
    node.set('content', str(value))


def apply_seo(builder):
    """Update the builder's in-memory documents and pending XML/text outputs."""
    items = list(builder.items.values())
    by_route = {item['url']: item for item in items}
    aliases = {}
    for item in items:
        identifier = str(item['id'])
        if identifier.isdigit():
            aliases['/contenus/' + identifier + '/'] = item['url']
    for record in builder.records:
        for alias in record.get('aliases') or []:
            aliases[alias] = record['route']

    paths = {p.relative_to(builder.root) for p in builder.root.rglob('*.html')}
    paths.update(builder.documents)
    for path in sorted(paths):
        if {'edition', 'admin'}.intersection(path.parts):
            # Existing administration pages explicitly use noindex. Keep their
            # configuration and login flow separate from public page metadata.
            continue
        tree = builder.doc(path)
        head = tree.xpath('//head')[0]
        current = page_route(path)
        canonical = aliases.get(current, current)
        item = by_route.get(canonical)
        canonical_nodes = head.xpath('./link[@rel="canonical"]')
        if canonical_nodes:
            canonical_nodes[0].set('href', absolute(canonical))
            for duplicate in canonical_nodes[1:]:
                head.remove(duplicate)
        else:
            etree.SubElement(head, 'link', rel='canonical', href=absolute(canonical))

        title = tree.xpath('string(//title)').strip()
        description = tree.xpath('string(//meta[@name="description"]/@content)').strip()
        if current == '/':
            title = HOME_TITLE
            description = HOME_DESCRIPTION
            title_nodes = head.xpath('./title')
            if title_nodes:
                title_nodes[0].text = title
            else:
                etree.SubElement(head, 'title').text = title
        elif not description:
            description = str((item or {}).get('excerpt') or '')
        if not description:
            description = 'Informations, activités et actualités du Centre social Horizon à Cholet.'
        description = ' '.join(description.split())[:200]
        meta(head, 'description', description)
        if item and item.get('retired'):
            meta(head, 'robots', 'noindex,follow')
        image = absolute('/assets/horizon-logo.jpg')
        for key, value in {
            'og:title': title, 'og:description': description,
            'og:url': absolute(canonical), 'og:site_name': SITE_NAME,
            'og:type': 'article' if item and item.get('kind') == 'post' else 'website',
            'og:locale': 'fr_FR', 'og:image': image,
            'og:image:alt': 'Logo du Centre social et socioculturel Horizon',
        }.items():
            meta(head, key, value, prop=True)
        for key, value in {
            'twitter:card': 'summary', 'twitter:title': title,
            'twitter:description': description, 'twitter:image': image,
            'twitter:image:alt': 'Logo du Centre social et socioculturel Horizon',
        }.items():
            meta(head, key, value)

    home = builder.doc('index.html')
    head = home.xpath('//head')[0]
    for old in head.xpath('./script[@id="horizon-structured-data"]'):
        head.remove(old)
    settings = builder.hours
    address_lines = [line.strip() for line in settings['address'].splitlines() if line.strip()]
    # These established address components are confirmed in the centre's
    # published contact information; the editable first line remains the street.
    postal_line = address_lines[-1] if address_lines else ''
    postal_parts = postal_line.split(' ', 1)
    address = {
        '@type': 'PostalAddress',
        'streetAddress': ', '.join(address_lines[:-1]) if len(address_lines) > 1 else settings['address'],
        'addressCountry': 'FR',
    }
    if len(postal_parts) == 2 and postal_parts[0].isdigit():
        address['postalCode'], address['addressLocality'] = postal_parts
    organisation = {
        '@type': 'Organization', '@id': ORIGIN + '/#organisation',
        'name': 'Centre social et socioculturel Horizon',
        'alternateName': SITE_NAME, 'url': ORIGIN + '/',
        'logo': absolute('/assets/horizon-logo.jpg'),
        'telephone': settings['phone'], 'email': settings['email'], 'address': address,
        'sameAs': [entry['url'] for entry in builder.read('reseaux.json').get('links', [])],
    }
    website = {
        '@type': 'WebSite', '@id': ORIGIN + '/#site', 'url': ORIGIN + '/',
        'name': SITE_NAME,
        'alternateName': ['Centre social et socioculturel Horizon', 'Horizon Cholet'],
        'inLanguage': 'fr-FR', 'publisher': {'@id': organisation['@id']},
    }
    node = etree.SubElement(head, 'script', type='application/ld+json', id='horizon-structured-data')
    node.text = json.dumps({'@context': 'https://schema.org', '@graph': [organisation, website]}, ensure_ascii=False).replace('<', '\\u003c')

    locations = {'/', '/tout-horizon/'}
    for item in items:
        if item.get('retired'):
            continue
        canonical = aliases.get(item['url'], item['url'])
        path = Path(canonical.lstrip('/')) / 'index.html'
        tree = builder.documents.get(path)
        if tree is not None and tree.xpath('//meta[@name="robots" and contains(@content,"noindex")]'):
            continue
        if tree is not None or (builder.root / path).is_file():
            locations.add(canonical)
    namespace = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    sitemap = etree.Element('{'+namespace+'}urlset', nsmap={None: namespace})
    for location in sorted(locations):
        entry = etree.SubElement(sitemap, '{'+namespace+'}url')
        etree.SubElement(entry, '{'+namespace+'}loc').text = absolute(location)
    builder.output[Path('sitemap.xml')] = etree.tostring(sitemap, encoding='unicode', pretty_print=True)
    builder.output[Path('robots.txt')] = ('User-agent: *\nAllow: /\nDisallow: /admin/\n'
                                         'Disallow: /edition/\n\nSitemap: '+ORIGIN+'/sitemap.xml\n')
