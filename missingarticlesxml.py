# -*- coding: utf-8 -*-

# Copyright (C) 2011 emijrp
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import md5
import os
import re
import sys
import unicodedata

import family
import wikipedia
import xmlreader

#TODO ranking de categorías sacadas de artículos que no tienen ningún interwiki

targetlang = 'en' #no cambiar a menos que quiera crear bios para otras wikipedias distintas a la inglesa
lang = 'es'
dumppath = ''
dumpfilename = ''
if len(sys.argv) >= 2:
    dumpfilename = sys.argv[1]
    lang = dumpfilename.split('wiki')[0]

cattranslations = {}

langisotolang = {
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'pl': 'Polish',
}

months = {
    'de': ['januar', 'februar', u'm[äa]rz', 'april', 'mai', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'dezember'],
    'es': ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'],
    'fr': ['janvier', u'f[ée]vrier', 'mars', 'avril', 'may', 'juin', 'juillet', u'ao[ûu]t', 'septembre', 'octobre', 'novembre', u'décembre'],
    'pl': ['stycznia', u'lutego', 'marca', 'kwietnia', 'maja', 'czerwca', 'lipca', u'sierpnia', u'wrze[śs]nia', u'pa[źz]dziernika', 'listopada', u'grudnia'],
    }

monthstoen = {
    #de
    'januar': 'January',
    'februar': 'February',
    u'märz': 'March',
    'marz': 'March',
    'april': 'April',
    'mai': 'May',
    'juni': 'June',
    'juli': 'July',
    'august': 'August',
    'september': 'September',
    'oktober': 'October',
    'november': 'November',
    'dezember': 'December',
    
    #es
    'enero': 'January',
    'febrero': 'February',
    'marzo': 'March',
    'abril': 'April',
    'mayo': 'May',
    'junio': 'June',
    'julio': 'July',
    'agosto': 'August',
    'septiembre': 'September',
    'octubre': 'October',
    'noviembre': 'November',
    'diciembre': 'December',
    
    #fr
    'janvier': 'January',
    u'février': 'February',
    'fevrier': 'February',
    'mars': 'March',
    'avril': 'April',
    'may': 'May',
    'juin': 'June',
    'juillet': 'July',
    u'août': 'August',
    'aout': 'August',
    'septembre': 'September',
    'octobre': 'October',
    'novembre': 'November',
    'décembre': 'December',
    
    #pl
    'stycznia': 'January',
    'lutego': 'February',
    'marca': 'March',
    'kwietnia': 'April',
    'maja': 'May',
    'czerwca': 'June',
    'lipca': 'July',
    'sierpnia': 'August',
    u'września': 'September',
    'wrzesnia': 'September',
    u'października': 'October',
    'pazdziernika': 'October',
    'listopada': 'November',
    'grudnia': 'December',
    }

nationalitytonation = {
    'Albanian': 'Albania',
    'American': 'United States',
    'Argentine': 'Argentina',
    'Austrian': 'Austria',
    'Belgian': 'Belgium',
    'Bolivian': 'Bolivia',
    'Brazilian': 'Brazil',
    'Chilean': 'Chile',
    'Chinese': 'China',
    'Colombian': 'Colombia',
    'Cuban': 'Cuba',
    'Dutch': 'Netherlands',
    'Ecuadorian': 'Ecuador',
    'French': 'France',
    'German': 'Germany',
    'Guatemalan': 'Guatemala',
    'Honduran': 'Honduras',
    'Hungarian': 'Hungry',
    'Italian': 'Italy',
    'Mexican': 'Mexico',
    'Panamanian': 'Panama',
    'Paraguayan': 'Paraguay',
    'Peruvian': 'Peru',
    'Portuguese': 'Portugal',
    'Russian': 'Russia',
    'Spanish': 'Spain',
    'Swiss': 'Switzerland',
    'Turkish': 'Turkey',
    'Uruguayan': 'Uruguay',
    'Venezuelan': 'Venezuela',
}

title_ex_r = re.compile(ur"(?im)[\:\(\)]") # : to exclude other namespaces, ( to disambiguation
red_r = re.compile(ur"(?im)^\#\s*redirec")
iws_r = re.compile(ur"(?im)\[\[\s*(?P<iwlang>[a-z]{2,3}(\-[a-z]{2,5})?)\s*:\s*(?P<iwtitle>[^\]\|]+)\s*\]\]")
iws_target_r = re.compile(ur"(?im)\[\[\s*%s\s*:\s*[^\]\|]+\s*\]\]" % (targetlang))
dis_r = re.compile(ur"(?im)\{\{\s*(disambiguation|disambig|desambiguaci[oó]n|desambig|desamb|homonymie)\s*[\|\}]") #pl: DisambigR, 
birth_r = re.compile(ur"(?im)\:\s*("
                     ur"Geboren[_ ]|" #de
                     ur"Nacidos[_ ]en|" #es
                     ur"Naissance[_ ]en|" #fr
                     ur"Urodzeni[_ ]w" #pl
                     ur")[_ ](?P<birthyear>\d{4})")
death_r = re.compile(ur"(?im)\:\s*("
                     ur"Gestorben[_ ]|" #de
                     ur"Fallecidos[_ ]en|" #es
                     ur"Décès[_ ]en|" #fr
                     ur"Zmarli[_ ]w" #pl
                     ur")[_ ](?P<deathyear>\d{4})")
bdtemplate_r = re.compile(ur"(?im)\{\{\s*(BD|NF)\s*\|\s*(?P<birthyear>\d{4})\s*\|\s*(?P<deathyear>\d{4})\s*(\s*\|\s*(?P<defaultsort>[^\}]{4,},[^\}]{4,})\s*)?\s*\}\}")

catsnm = { #lo uso en translatecat() también
    'de': 'Kategorie',
    'en': 'Category',
    'es': u'Categoría',
    'fr': u'Catégorie',
    'pl': 'Kategoria',
    }
cats_r = re.compile(ur"(?im)\[\[\s*(%s)\s*:\s*(?P<catname>[^\]\|]+)\s*[\]\|]" % ('|'.join(catsnm.values())))
dates_r = {
    'de': re.compile(ur"(?im)[^\(\)\d]*?\s*(\[?\[?(?P<birthday>\d+)[\s\|]*(?P<birthmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<birthyear>\d{4})\]?\]?\s*[^\n\r\d\)\[]{,15}\s*(\[?\[?(?P<deathday>\d+)[\s\|]*(?P<deathmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<deathyear>\d{4})\]?\]?" % ('|'.join(months[lang]), '|'.join(months[lang]))),
    'es': re.compile(ur"(?im)[^\(\)\d]*?\s*(\[?\[?(?P<birthday>\d+)\s*de\s*(?P<birthmonth>%s)\]?\]?\s*de)?\s*\[?\[?(?P<birthyear>\d{4})\]?\]?\s*[^\n\r\d\)\[]{,15}\s*[^\(\)\d]*?\s*(\[?\[?(?P<deathday>\d+)\s*de\s*(?P<deathmonth>%s)\]?\]?\s*de)?\s*\[?\[?(?P<deathyear>\d{4})\]?\]?" % ('|'.join(months[lang]), '|'.join(months[lang]))),
    'fr': re.compile(ur"(?im)[^\(\)\d]*?\s*(\[?\[?(?P<birthday>\d+)[\s\|]*(?P<birthmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<birthyear>\d{4})\]?\]?\s*[^\n\r\d\)\[]{,15}\s*(\[?\[?(?P<deathday>\d+)[\s\|]*(?P<deathmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<deathyear>\d{4})\]?\]?" % ('|'.join(months[lang]), '|'.join(months[lang]))),
    'pl': re.compile(ur"(?im)[^\(\)\d]*?\s*(\[?\[?(?P<birthday>\d+)[\s\|]*(?P<birthmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<birthyear>\d{4})\]?\]?\s*[^\n\r\d\)\[]{,15}\s*(\[?\[?(?P<deathday>\d+)[\s\|]*(?P<deathmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<deathyear>\d{4})\]?\]?" % ('|'.join(months[lang]), '|'.join(months[lang]))),
}
defaultsort_r = re.compile(ur"(?im)\{\{\s*("
                           ur"SORTIERUNG|" #de
                           ur"DEFAULTSORT|" #en, fr, pl
                           ur"ORDENAR" #es
                           ur")\s*:\s*(?P<defaultsort>[^\{\}]+?)\s*\}\}")

def quitaracentos(s):
    #http://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
    return ''.join((c for c in unicodedata.normalize('NFD', u'%s' % s) if unicodedata.category(c) != 'Mn'))
    """
    t = re.sub(ur'[ÁÀÄ]', ur'A', t)
    t = re.sub(ur'[ÉÈË]', ur'E', t)
    t = re.sub(ur'[ÍÌÏ]', ur'I', t)
    t = re.sub(ur'[ÓÒÖ]', ur'O', t)
    t = re.sub(ur'[ÚÙÜ]', ur'U', t)
    t = re.sub(ur'[áàä]', ur'a', t)
    t = re.sub(ur'[éèë]', ur'e', t)
    t = re.sub(ur'[íìï]', ur'i', t)
    t = re.sub(ur'[óòö]', ur'o', t)
    t = re.sub(ur'[úùü]', ur'u', t)
    return t"""

def linkstoiws(t, lang):
    t = re.sub(ur"\[\[([^\[\]\|]+)\|([^\[\]\|]+)\]\]", ur"[[:%s:\1|\2]]" % (lang), t)
    t = re.sub(ur"\[\[([^\[\]\|]+)\]\]", ur"[[:%s:\1|\1]]" % (lang), t)
    return t

def translatecat(cat, lang):
    if cattranslations.has_key(cat):
        return cattranslations[cat]
    else:
        catpage = wikipedia.Page(wikipedia.Site(lang, 'wikipedia'), "Category:%s" % (cat))
        if catpage.exists() and not catpage.isRedirectPage():
            cattext = catpage.get()
            m = re.compile(ur"(?im)\[\[\s*%s\s*:\s*(%s)\s*:\s*(?P<catiw>[^\[\]]+?)\s*\]\]" % (targetlang, '|'.join(catsnm.values()))).finditer(cattext)
            for i in m:
                cattranslations[cat] = i.group('catiw')
                return i.group('catiw')
    return ''

def main():
    """Missing articles"""
    xml = xmlreader.XmlDump('%s%s' % (dumppath and '%s/' % dumppath or '', dumpfilename), allrevisions=False)
    c = 0
    bios = 0
    for x in xml.parse(): #parsing the whole dump
        c+=1
        if re.search(title_ex_r, x.title) or \
           re.search(red_r, x.text) or \
           re.search(dis_r, x.text) or \
           len(x.text.splitlines()) < 3 or len(x.text) < 1024*2:
            continue
        #nombre con dos palabras largas al menos
        trozos = [] # no hacer la asignacion del bucle for directamente, sino almacena True y False en vez de los trozos
        [len(trozo) >= 4 and trozos.append(trozo) for trozo in x.title.split(' ')]
        if not len(trozos) >= 2:
            continue
        #metemos variantes sin acentos
        [(trozo != quitaracentos(trozo) and trozo not in trozos) and trozos.append(quitaracentos(trozo)) for trozo in trozos]
        
        #descartamos algunas bios
        if not re.search(birth_r, x.text) or not re.search(death_r, x.text): #sino ha fallecido, fuera
            continue
        if re.search(iws_target_r, x.text): #si tiene iws hacia targetlang, no nos interesa, ya existe la bio
            continue
        
        #buscando imágenes útiles para la bio
        images = re.findall(ur"(?im)[\s\/\:\|\=]+([^\/\:\|\=]+\.jpe?g)[\s\|]", x.text)
        image_cand = ''
        if images:
            continue #temp
            for image in images:
                if len(re.findall(ur"(%s)" % ('|'.join(trozos)), image)) >= 1:
                    image_cand = image
                    break
        #temp
        #if not image_cand:
        #    continue
        
        #description
        desc = re.findall(ur"(?im)^(\'{2,5}\s*%s[^\n\r]+)[\n\r]"  % (x.title.split(' ')[0]), x.text)
        if not desc:
            continue
        desc = desc[0]
        #print desc
        
        #birth and death dates
        birthdate = ''
        deathdate = ''
        m = birth_r.finditer(x.text)
        for i in m:
            birthdate = i.group('birthyear')
            break
        m = death_r.finditer(x.text)
        for i in m:
            deathdate = i.group('deathyear')
            break
        
        if not birthdate or not deathdate:
            m = dates_r[lang].finditer(desc)
            for i in m:
                birthmonth = ''
                if i.group('birthday') and i.group('birthmonth'):
                    if monthstoen.has_key(quitaracentos(i.group('birthmonth').lower())):
                        birthmonth = monthstoen[i.group('birthmonth').lower()]
                deathmonth = ''
                if i.group('deathday') and i.group('deathmonth'):
                    if monthstoen.has_key(quitaracentos(i.group('deathmonth').lower())):
                        deathmonth = monthstoen[i.group('deathmonth').lower()]
                if birthmonth:
                    #continue #temp
                    birthdate = u'%s %s, %s' % (birthmonth, i.group('birthday'), i.group('birthyear'))
                else:
                    birthdate = u'%s' % (i.group('birthyear'))
                if deathmonth:
                    #continue #temp
                    deathdate = u'%s %s, %s' % (deathmonth, i.group('deathday'), i.group('deathyear'))
                else:
                    deathdate = u'%s' % (i.group('deathyear'))
                break
        
        #special cases for es: {{BD|XXXX|YYYY|DEFAULTSORT}}
        if not birthdate and not deathdate:
            m = bdtemplate_r.finditer(x.text)
            for i in m:
                birthdate = u'%s' % (i.group('birthyear'))
                deathdate = u'%s' % (i.group('deathyear'))
                break
        #end birth and death dates
        
        #defaultsort
        m = defaultsort_r.finditer(x.text)
        defaultsort = ''
        for d in m:
            defaultsort = d.group("defaultsort")
            break
        if not defaultsort:
            m = bdtemplate_r.finditer(x.text)
            for i in m:
                defaultsort = u'%s' % (i.group('defaultsort'))
                break
        if not defaultsort: #create myself
            defaultsort = u'%s, %s' % (' '.join(quitaracentos(x.title).split(' ')[1:]), quitaracentos(x.title).split(' ')[0])
        
        #iws
        m = iws_r.finditer(x.text)
        iws = []
        for iw in m:
            if not iw.group('iwlang') in [targetlang, lang]:
                iws.append([iw.group('iwlang'), iw.group('iwtitle')])
        iws.append([lang, x.title])
        iws.sort()
        iws_plain = ''
        for iwlang, iwtitle in iws:
            iws_plain += u'[[%s:%s]]\n' % (iwlang, iwtitle)
        
        if desc and len(desc) < 1000 and birthdate and deathdate:
            #check if live version has interwiki or not
            sourcebio = wikipedia.Page(wikipedia.Site(lang, 'wikipedia'), x.title)
            if not sourcebio.exists() or sourcebio.isRedirectPage() or sourcebio.isDisambig() or len(re.findall(iws_target_r, sourcebio.get())) != 0:
                continue
            #cats, esto es lo más costoso en tiempo, entonces lo dejamos para este último if justo antes de generar el output
            m = cats_r.finditer(x.text)
            cats = []
            [translatecat(cat.group('catname'), lang) and translatecat(cat.group('catname'), lang) not in cats and cats.append(translatecat(cat.group('catname'), lang)) for cat in m]
            cats.sort()
            
            #nationality
            nationality = ''
            if cats:
                n = [cat.split(' ')[0] for cat in cats]
                for nn in n:
                    if nn in nationalitytonation.keys():
                        if nationality:
                            if nn != nationality: #conflict, several nationalities for this bio, blank nationality and exit
                                nationality = ''
                                break
                        else:
                            nationality = nn         
                    else:
                        f = open('missingarticlesxml.output.errors', 'a')
                        f.write((u'missing nationality = %s\n' % (nn)).encode('utf-8'))
                        f.close()
            
            #occupations (usando cats)
            occupations = []
            if nationality:
                for cat in cats:
                    t = cat.split(' ')
                    if (t[0] == nationality or t[0].split('-')[0] == nationality) and len(t) == 2: # [[Category:Spanish writers]] [[Category:Spanish-language writers]]
                        if t[1][-3:] == 'ies':
                            if not '%sy' % t[1].rstrip('ies') in occupations:
                                occupations.append('%sy' % t[1].rstrip('ies')) #remove final ies and add y
                        elif t[1][-1] == 's':
                            if not t[1].rstrip('s') in occupations:
                                occupations.append(t[1].rstrip('s')) #remove final s
                        elif t[1] == 'businesspeople':
                            if not 'businessman' in occupations:
                                occupations.append('businessman')
            
            if not occupations or not nationality:
                continue
            
            #la salida para esta bio
            output  = u"""\n<br clear="all"/>\n==== [[%s]] ([[:%s:%s|%s]]) ====""" % (x.title, lang, x.title, lang)
            output += u"""\n[[File:%s|thumb|right|120px|%s]]""" % (image_cand, x.title)
            output += u"""\n<small><nowiki>%s</nowiki></small>""" % (linkstoiws(desc, lang).strip())
            output += u"""\n<pre>"""
            output += u"""\n{{Expand %s|%s}}""" % (langisotolang[lang], x.title)
            if image_cand:
                output += u"""\n[[File:%s|thumb|right|%s]]""" % (image_cand, x.title)
            output += u"""\n\'\'\'%s\'\'\' (%s - %s) was %s %s %s.""" % (x.title, birthdate, deathdate, nationality and nationalitytonation[nationality][0] in ['A', 'E', 'I', 'O', 'U'] and 'an' or 'a', nationality and '[[%s|%s]]' % (nationalitytonation[nationality], nationality), occupations and (len(occupations) > 1 and '%s and %s' % (', '.join(occupations[:-1]), occupations[-1:][0]) or occupations[0]) or '...')
            output += u"""\n\n{{Persondata <!-- Metadata: see [[Wikipedia:Persondata]]. -->"""
            output += u"""\n| NAME              = %s """ % (defaultsort)
            output += u"""\n| ALTERNATIVE NAMES = """
            output += u"""\n| SHORT DESCRIPTION = """
            output += u"""\n| DATE OF BIRTH     = %s """ % (birthdate)
            output += u"""\n| PLACE OF BIRTH    = """
            output += u"""\n| DATE OF DEATH     = %s """ % (deathdate)
            output += u"""\n| PLACE OF DEATH    = """
            output += u"""\n}}"""
            output += u"""\n{{DEFAULTSORT:%s}}""" % (defaultsort)
            if cats:
                output += u"""\n"""
                for cat in cats:
                    output += u"""\n[[Category:%s]]""" % (cat)
            output += u"""\n\n%s""" % (iws_plain)
            output += u"""\n%s""" % (nationality and nationalitytonation[nationality] and '{{%s-bio-stub}}' % (nationalitytonation[nationality]) or '{{bio-stub}}')
            output += u"""\n</pre>"""
            
            print '#'*70
            print x.title, 'https://%s.wikipedia.org/wiki/%s' % (lang, x.title.replace(' ', '_'))
            print output
            bios += 1
            print 'Total pages analysed =', c, '| Bios =', bios
            f = open('missingarticlesxml.output.%s' % (lang), 'a')
            f.write(output.encode('utf-8'))
            f.close()

if __name__ == "__main__":
    main()