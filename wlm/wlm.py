#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011-2012 emijrp <emijrp@gmail.com>
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

import catlib
import pagegenerators
import datetime
import md5
import re
import wikipedia

#subida fácil: http://commons.wikimedia.org/w/index.php?title=Special:Upload&wpDestFile=BBBB.jpg&uploadformstyle=basic&wpUploadDescription=\ {{Information|Description=|Source=|Date=|Author=|Permission=|other_versions=}}

def isvalidimage(img):
    if img and not re.search(ur'(?im)(falta[_ ]imagen|\.svg|missing[\- ]monuments[\- ]image|Wiki[_ ]Loves[_ ]Monuments[_ ]Logo)', img):
        return True
    return False

def clean(t):
    t = re.sub(ur'(?i)([\[\]]|\|.*|\<ref.*)', ur'', t).strip() #quitamos enlaces, refs, etc
    t = re.sub(ur'(?im)<\s*/?\s*[^<>]+\s*/?\s*>', ur'-', t).strip() #fuera etiquetas HTML </br> <br/> (las refs las hemos quitado antes)
    return t

def removerefs(t):
    t = re.sub(ur"(?im)\{\{\s*(?!(fila (BIC|BIC 2)|BIC|filera (BIC|BCIN|BIC Val)))\s*\|[^{}]*?\}\}", ur"", t)
    t = re.sub(ur"(?im)<\s*ref[^<>]*?\s*>[^<>]*?<\s*/\s*ref\s*>", ur"", t) # <ref></ref> <ref name=""></ref>
    t = re.sub(ur"(?im)<\s*ref\s+name[^<>]+?\s*/\s*>", ur"", t) # <ref name="" />
    return t

def colors(percent):
    if percent < 25:
        return 'red'
    elif percent < 50:
        return 'pink'
    elif percent < 75:
        return 'yellow'
    elif percent < 100:
        return 'lightgreen'
    elif percent == 100:
        return 'lightblue'
    return 'white'

wmurls = { 'spain': 'http://www.wikimedia.org.es', 'chile': 'http://www.wikimediachile.cl', 'argentina': 'http://www.wikimedia.org.ar'}
wmlogourls = { 'spain': 'http://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Wikimedia-es-logo.svg/80px-Wikimedia-es-logo.svg.png', 'chile': 'http://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Wikimedia_Chile_logo.svg/80px-Wikimedia_Chile_logo.svg.png', 'argentina': 'http://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Wikimedia_Argentina_logo.svg/80px-Wikimedia_Argentina_logo.svg.png'}
wlmurls = { 'spain': 'http://www.wikilm.es', 'chile': 'http://www.wikilovesmonuments.cl', 'argentina': 'http://wikilovesmonuments.com.ar'}

uploadcats = { 'spain': 'Images from Wiki Loves Monuments 2012 in Spain', 'chile': 'Images from Wiki Loves Monuments 2012 in Chile', 'argentina': 'Images from Wiki Loves Monuments 2012 in Argentina'}

capital = { 'spain': 'madrid', 'chile': 'santiago', 'argentina': 'buenosaires' }

placenames = {

#spain
"alava": u"Álava", "alicante": u"Alicante",
"badajoz": u"Badajoz", "burgos": u"Burgos", "barcelona": u"Barcelona",
"coruna": u"A&nbsp;Coruña", "albacete": u"Albacete", "almeria": u"Almería", "asturias": u"Asturias", "avila": u"Ávila",
"cantabria": u"Cantabria", "castellon": u"Castellón", "catalunya": u"Catalunya", "ceuta": u"Ceuta", "ciudadreal": u"Ciudad&nbsp;Real", "cuenca": u"Cuenca", "caceres": u"Cáceres", "cadiz": u"Cádiz", "cordoba": u"Córdoba",
"girona": u"Girona", "granada": u"Granada", "guadalajara": u"Guadalajara", "guipuzcoa": u"Guipuzkoa",
"huelva": u"Huelva", "huesca": u"Huesca",
"baleares": u"Illes&nbsp;Balears",
"jaen": u"Jaén", 
"laspalmas": u"Las&nbsp;Palmas", "leon": u"León", "lleida": u"Lleida", "lugo": u"Lugo",
"madrid": u"Madrid", "melilla": u"Melilla", "murcia": u"Murcia", "malaga": u"Málaga", 
"navarra": u"Navarra",
"valencia": u"Valencia", "palencia": u"Palencia", "larioja": u"La&nbsp;Rioja", "ourense": u"Ourense", "pontevedra": u"Pontevedra",
"salamanca": u"Salamanca", "tenerife": u"Tenerife", "segovia": u"Segovia", "sevilla": u"Sevilla", "soria": u"Soria", 
"tarragona": u"Tarragona", "teruel": u"Teruel", "toledo": u"Toledo", "valladolid": u"Valladolid", "vizcaya": u"Vizcaya", 
"zamora": u"Zamora", "zaragoza": u"Zaragoza",

#argentina
'buenosaires': u"Buenos Aires",
'catamarca': u"Catamarca",
'chaco': u"Chaco",
'chubut': u"Chubut",
'corrientes': u"Corrientes",
'cordoba': u"Córdoba",
'entrerios': u"Entre Ríos",
'formosa': u"Formosa",
'jujuy': u"Jujuy",
'lapampa': u"La Pampa",
'larioja': u"La Rioja",
'mendoza': u"Mendoza",
'misiones': u"Misiones",
'neuquen': u"Neuquén",
'rionegro': u"Río Negro",
'salta': u"Salta",
'sanjuan': u"San Juan",
'sanluis': u"San Luis",
'santacruz': u"Santa Cruz",
'santafe': u"Santa Fe",
'santiagodelestero': u"Santiago del Estero",
'tierradelfuego': u"Tierra del Fuego",
'tucuman': u"Tucumán",

#chile
'antofagasta': u"Antofagasta",
'araucania': u"Araucania",
'aricayparinacota': u"Arica y Parinacota",
'atacama': u"Atacama",
'aysen': u"Aysen",
'biobio': u"Biobio",
'coquimbo': u"Coquimbo",
'libertador': u"Libertador",
'loslagos': u"Los lagos",
'losrios': u"Los Ríos",
'magallanes': u"Magallanes",
'maule': u"Maule",
'santiago': u"Santiago",
'tarapaca': u"Tarapaca",
'valparaiso': u"Valparaiso",

}

def placenamesconvert(p):
    if placenames.has_key(p):
        return placenames[p]
    else:
        return p[0].upper()+p[1:]

#mejor no mezclar varios anexos de varios idiomas para una misma provincia
anexos = {}
anexos['spain'] = {
'alava': [u'es:Anexo:Bienes de interés cultural de la provincia de Álava', ], 

'albacete': [u'es:Anexo:Bienes de interés cultural de la provincia de Albacete', ],
'almeria': [u'es:Anexo:Bienes de interés cultural de la provincia de Almería', ],
'asturias': [u'es:Anexo:Bienes de interés cultural de Asturias', ],
'avila': [u'es:Anexo:Bienes de interés cultural de la provincia de Ávila', ],
'badajoz': [u'es:Anexo:Bienes de interés cultural de la provincia de Badajoz', ],

'baleares': [u"ca:Llista de monuments d'Eivissa", u'ca:Llista de monuments de Formentera', 
    u"ca:Llista de monuments d'Alaior", u"ca:Llista de monuments des Castell", u"ca:Llista de monuments de Ciutadella", u"ca:Llista de monuments de Ferreries", u"ca:Llista de monuments de Maó", u"ca:Llista de monuments des Mercadal", u"ca:Llista de monuments des Migjorn Gran", u"ca:Llista de monuments de Sant Lluís",
    
    u"ca:Llista de monuments d'Alaró", u"ca:Llista de monuments d'Alcúdia", u"ca:Llista de monuments d'Algaida", u"ca:Llista de monuments d'Andratx", u"ca:Llista de monuments d'Ariany", u"ca:Llista de monuments d'Artà", u"ca:Llista de monuments de Banyalbufar", u"ca:Llista de monuments de Binissalem", u"ca:Llista de monuments de Búger", u"ca:Llista de monuments de Bunyola", u"ca:Llista de monuments de Calvià", u"ca:Llista de monuments de Campanet", u"ca:Llista de monuments de Campos", u"ca:Llista de monuments de Capdepera", u"ca:Llista de monuments de Consell", u"ca:Llista de monuments de Costitx", u"ca:Llista de monuments de Deià", u"ca:Llista de monuments d'Escorca", u"ca:Llista de monuments d'Esporles", u"ca:Llista de monuments d'Estellencs", u"ca:Llista de monuments de Felanitx", u"ca:Llista de monuments de Fornalutx", u"ca:Llista de monuments d'Inca", u"ca:Llista de monuments de Lloret de Vistalegre", u"ca:Llista de monuments de Lloseta", u"ca:Llista de monuments de Llubí", u"ca:Llista de monuments de Llucmajor", u"ca:Llista de monuments de Manacor", u"ca:Llista de monuments de Mancor de la Vall", u"ca:Llista de monuments de Maria de la Salut", u"ca:Llista de monuments de Marratxí",  u"ca:Llista de monuments de Montuïri",  u"ca:Llista de monuments de Muro",  u"ca:Llista de monuments de Palma",  u"ca:Llista de monuments de Petra",  u"ca:Llista de monuments de sa Pobla",  u"ca:Llista de monuments de Pollença",  u"ca:Llista de monuments de Porreres",  u"ca:Llista de monuments de Puigpunyent",  u"ca:Llista de monuments de ses Salines",  u"ca:Llista de monuments de Sant Joan",  u"ca:Llista de monuments de Sant Llorenç des Cardassar",  u"ca:Llista de monuments de Santa Eugènia",  u"ca:Llista de monuments de Santa Margalida",  u"ca:Llista de monuments de Santa Maria del Camí",  u"ca:Llista de monuments de Santanyí",  u"ca:Llista de monuments de Selva",  u"ca:Llista de monuments de Sencelles",  u"ca:Llista de monuments de Sineu",  u"ca:Llista de monuments de Sóller",  u"ca:Llista de monuments de Son Servera",  u"ca:Llista de monuments de Valldemossa",  u"ca:Llista de monuments de Vilafranca de Bonany",
    ],

'burgos': [u'es:Anexo:Bienes de interés cultural de la provincia de Burgos', ],
'cantabria': [u'es:Anexo:Bienes de interés cultural de Cantabria', ],

#catalunya
    'barcelona': [u"ca:Llista de monuments de l'Alt Penedès", u"ca:Llista de monuments de l'Anoia", u"ca:Llista de monuments del Bages", u"ca:Llista de monuments del Baix Llobregat", u"ca:Llista de monuments del Barcelonès", u"ca:Llista de monuments del Berguedà",  u"ca:Llista de monuments del Garraf", u"ca:Llista de monuments del Maresme", u"ca:Llista de monuments d'Osona", u"ca:Llista de monuments del Vallès Occidental", u"ca:Llista de monuments del Vallès Oriental", ],

    'girona': [u"ca:Llista de monuments de l'Alt Empordà", u"ca:Llista de monuments del Baix Empordà", u"ca:Llista de monuments de la Garrotxa", u"ca:Llista de monuments del Gironès", u"ca:Llista de monuments del Pla de l'Estany", u"ca:Llista de monuments del Ripollès", u"ca:Llista de monuments de la Selva", ],

    'lleida': [u"ca:Llista de monuments de l'Alt Urgell", u"ca:Llista de monuments de l'Alta Ribagorça", u"ca:Llista de monuments de la Baixa Cerdanya", u"ca:Llista de monuments de les Garrigues", u"ca:Llista de monuments de la Noguera", u"ca:Llista de monuments del Pallars Jussà", u"ca:Llista de monuments del Pallars Sobirà", u"ca:Llista de monuments del Pla d'Urgell", u"ca:Llista de monuments de la Segarra", u"ca:Llista de monuments del Segrià", u"ca:Llista de monuments del Solsonès", u"ca:Llista de monuments de l'Urgell", u"ca:Llista de monuments de la Vall d'Aran", ],

    'tarragona': [u"ca:Llista de monuments de l'Alt Camp", u"ca:Llista de monuments del Baix Camp", u"ca:Llista de monuments del Baix Ebre", u"ca:Llista de monuments del Baix Penedès", u"ca:Llista de monuments de la Conca de Barberà", u"ca:Llista de monuments del Montsià", u"ca:Llista de monuments del Priorat", u"ca:Llista de monuments de la Ribera d'Ebre", u"ca:Llista de monuments del Tarragonès", u"ca:Llista de monuments de la Terra Alta",  ],

'ceuta': [u'es:Anexo:Bienes de interés cultural de Ceuta', ],
'ciudadreal': [u'es:Anexo:Bienes de interés cultural de la provincia de Ciudad Real', ],
'coruna': [u'gl:Lista de monumentos da provincia da Coruña', ],
'cuenca': [u'es:Anexo:Bienes de interés cultural de la provincia de Cuenca', ],
'caceres': [u'es:Anexo:Bienes de interés cultural de la provincia de Cáceres', ],
'cadiz': [u'es:Anexo:Bienes de interés cultural de la provincia de Cádiz', ],
'cordoba': [u'es:Anexo:Bienes de interés cultural de la provincia de Córdoba', ],

'granada': [u'es:Anexo:Bienes de interés cultural de la provincia de Granada', ],

'guadalajara': [u'es:Anexo:Bienes de interés cultural de la provincia de Guadalajara', ],
'guipuzcoa': [u'es:Anexo:Bienes de interés cultural de la provincia de Guipúzcoa', ],

'huelva': [u'es:Anexo:Bienes de interés cultural de la provincia de Huelva', ],

'huesca': [u'es:Anexo:Bienes de interés cultural de la provincia de Huesca', ],
'jaen': [u'es:Anexo:Bienes de interés cultural de la provincia de Jaén', ],
'laspalmas': [u'es:Anexo:Bienes de interés cultural de la provincia de Las Palmas', ],
'leon': [u'es:Anexo:Bienes de interés cultural de la provincia de León', ],
'madrid': [u'es:Anexo:Bienes de interés cultural de la Comunidad de Madrid', ],
'melilla': [u'es:Anexo:Bienes de interés cultural de Melilla', ],
'murcia': [u'es:Anexo:Bienes de interés cultural de la Región de Murcia', ],
'malaga': [u'es:Anexo:Bienes de interés cultural de la provincia de Málaga', ],
'navarra': [u'es:Anexo:Bienes de interés cultural de Navarra', ],
'palencia': [u'es:Anexo:Bienes de interés cultural de la provincia de Palencia', ],
'larioja': [u'es:Anexo:Bienes de Interés Cultural de La Rioja (España)', ],
'lugo': [u'gl:Lista de monumentos da provincia de Lugo', ],
'ourense': [u'gl:Lista de monumentos da provincia de Ourense', ],
'pontevedra': [u'gl:Lista de monumentos da provincia de Pontevedra', ],
'salamanca': [u'es:Anexo:Bienes de interés cultural de la provincia de Salamanca', ],
'tenerife': [u'es:Anexo:Bienes de interés cultural de la provincia de Santa Cruz de Tenerife', ],
'segovia': [u'es:Anexo:Bienes de interés cultural de la provincia de Segovia', ],
'sevilla': [u'es:Anexo:Bienes de interés cultural de la provincia de Sevilla', ],
'soria': [u'es:Anexo:Bienes de interés cultural de la provincia de Soria', ],
'teruel': [u'es:Anexo:Bienes de Interés Cultural de la provincia de Teruel', ],
'toledo': [u'es:Anexo:Bienes de interés cultural de la provincia de Toledo', ],

#país valenciá
    'alicante': [u"ca:Llista de monuments de l'Alacantí", u"ca:Llista de monuments de l'Alcoià", u"ca:Llista de monuments de l'Alt Vinalopó", u"ca:Llista de monuments del Baix Segura", u"ca:Llista de monuments del Baix Vinalopó", u"ca:Llista de monuments del Comtat", u"ca:Llista de monuments de la Marina Alta", u"ca:Llista de monuments de la Marina Baixa", u"ca:Llista de monuments del Vinalopó Mitjà", ],
    
    'castellon': [u"ca:Llista de monuments de l'Alcalatén", u"ca:Llista de monuments de l'Alt Maestrat", u"ca:Llista de monuments de l'Alt Millars", u"ca:Llista de monuments de l'Alt Palància", u"ca:Llista de monuments del Baix Maestrat", u"ca:Llista de monuments dels Ports", u"ca:Llista de monuments de la Plana Alta", u"ca:Llista de monuments de la Plana Baixa", ],

    'valencia': [u"ca:Llista de monuments del Camp de Morvedre", u"ca:Llista de monuments del Camp de Túria", u"ca:Llista de monuments de la Canal de Navarrés", u"ca:Llista de monuments de la Costera", u"ca:Llista de monuments de la Foia de Bunyol", u"ca:Llista de monuments de l'Horta Nord", u"ca:Llista de monuments de l'Horta Oest", u"ca:Llista de monuments de l'Horta Sud",  u"ca:Llista de monuments de la Plana d'Utiel",  u"ca:Llista de monuments del Racó d'Ademús", u"ca:Llista de monuments de la Ribera Alta", u"ca:Llista de monuments de la Ribera Baixa", u"ca:Llista de monuments de la Safor", u"ca:Llista de monuments dels Serrans", u"ca:Llista de monuments de València", u"ca:Llista de monuments de la Vall d'Albaida", u"ca:Llista de monuments de la Vall de Cofrents", ],

'valladolid': [u'es:Anexo:Bienes de interés cultural de la provincia de Valladolid', ],
'vizcaya': [u'es:Anexo:Bienes de interés cultural de la provincia de Vizcaya', ],
'zamora': [u'es:Anexo:Bienes de interés cultural de la provincia de Zamora', ],
'zaragoza': [u'es:Anexo:Bienes de interés cultural de la provincia de Zaragoza', ],
}

anexos['chile'] = {
'antofagasta': [u'es:Anexo:Monumentos nacionales de la Región de Antofagasta', ],
'araucania': [u'es:Anexo:Monumentos nacionales de la Región de La Araucanía', ],
'aricayparinacota': [u'es:Anexo:Monumentos nacionales de la Región de Arica y Parinacota', ],
'atacama': [u'es:Anexo:Monumentos nacionales de la Región de Atacama', ],
'aysen': [u'es:Anexo:Monumentos nacionales de la Región de Aysén del General Carlos Ibáñez del Campo', ],
'biobio': [u'es:Anexo:Monumentos nacionales de la Región del Biobío', ],
'coquimbo': [u'es:Anexo:Monumentos nacionales de la Región de Coquimbo', ],
'libertador': [u"es:Anexo:Monumentos nacionales de la Región del Libertador General Bernardo O'Higgins", ],
'loslagos': [u'es:Anexo:Monumentos nacionales de la Región de Los Lagos', ],
'losrios': [u'es:Anexo:Monumentos nacionales de la Región de Los Ríos', ],
'magallanes': [u'es:Anexo:Monumentos nacionales de la Región de Magallanes y de la Antártica Chilena', ],
'maule': [u'es:Anexo:Monumentos nacionales de la Región del Maule', ],
'santiago': [u'es:Anexo:Monumentos nacionales de la Región Metropolitana de Santiago', ],
'tarapaca': [u'es:Anexo:Monumentos nacionales de la Región de Tarapacá', ],
'valparaiso': [u'es:Anexo:Monumentos nacionales de la Región de Valparaíso', ],

}

anexos['argentina'] = {
'buenosaires': [u'es:Anexo:Monumentos de la Ciudad de Buenos Aires', u'es:Anexo:Bienes de Interés Cultural de la Ciudad de Buenos Aires', u'es:Anexo:Monumentos de la Provincia de Buenos Aires', u'es:Anexo:Monumentos provinciales de la Provincia de Buenos Aires', u'es:Anexo:Monumentos locales de la Provincia de Buenos Aires', ],
'catamarca': [u'es:Anexo:Monumentos de la Provincia de Catamarca', ],
'chaco': [u'es:Anexo:Monumentos de la Provincia de Chaco', ],
'chubut': [u'es:Anexo:Monumentos de la Provincia del Chubut', ],
'corrientes': [u'es:Anexo:Monumentos de la Provincia de Corrientes', ],
'cordoba': [u'es:Anexo:Monumentos de la Provincia de Córdoba', ],
'entrerios': [u'es:Anexo:Monumentos de la Provincia de Entre Ríos', ],
'formosa': [u'es:Anexo:Monumentos de la Provincia de Formosa', ],
'jujuy': [u'es:Anexo:Monumentos de la Provincia de Jujuy', ],
'lapampa': [u'es:Anexo:Monumentos de la Provincia de La Pampa', ],
'larioja': [u'es:Anexo:Monumentos de la Provincia de La Rioja', ],
'mendoza': [u'es:Anexo:Monumentos de la Provincia de Mendoza', ],
'misiones': [u'es:Anexo:Monumentos de la Provincia de Misiones', ],
'neuquen': [u'es:Anexo:Monumentos de la Provincia del Neuquén', ],
'rionegro': [u'es:Anexo:Monumentos de la Provincia de Río Negro', ],
'salta': [u'es:Anexo:Monumentos de la Provincia de Salta', ],
'sanjuan': [u'es:Anexo:Monumentos de la Provincia de San Juan', ],
'sanluis': [u'es:Anexo:Monumentos de la Provincia de San Luis', ],
'santacruz': [u'es:Anexo:Monumentos de la Provincia de Santa Cruz', ],
'santafe': [u'es:Anexo:Monumentos de la Provincia de Santa Fe', ],
'santiagodelestero': [u'es:Anexo:Monumentos de la Provincia de Santiago del Estero', ],
'tierradelfuego': [u'es:Anexo:Monumentos de la Provincia de Tierra del Fuego, Antártida e Islas del Atlántico Sur', ],
'tucuman': [u'es:Anexo:Monumentos de la Provincia de Tucumán', ],

}

"""
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>CDATA example</name>
      <description>
        <![CDATA[
          <h1>CDATA Tags are useful!</h1>
          <p><font color="red">Text is <i>more readable</i> and 
          <b>easier to write</b> when you can avoid using entity 
          references.</font></p>
        ]]>
      </description>
      <Point>
        <coordinates>102.595626,14.996729</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>
"""

"""
{{fila BIC
 | nombre = [[Castillo de Matrera]]
 | nombrecoor = Castillo de Matrera
 | tipobic = M
 | tipo = 
 | municipio = [[Villamartín]]
 | lugar = 
 | lat = 36.807153 | lon = -5.565698
 | bic = RI-51-0007646
 | fecha = 22-06-1993
 | imagen = 
}}

{{Fila BIC 2
 | nombre = [[Archivo Histórico Provincial (Granada)|Archivo Histórico Provincial de Granada]]
 | nombrecoor = Archivo Histórico Provincial de Granada
 | tipobic = A
 | tipo = Archivo
 | municipio = [[Granada]]
 | lugar = C/ San Agapito, s/n
 | lat =  | lon = 
 | bic = R.I.-AR-0000056-00000
 | id_aut = 180870383
 | fecha = 25/06/1985<ref name="Patrimonio">http://www.boe.es/boe/dias/1985/06/29/pdfs/A20342-20352.pdf La Ley de Patrimonio del Estado califica como Bienes de Interés Cultural cuantos edificios estaban declarados con anterioridad como Monumento Nacional</ref>
 | imagen = 
}}
"""
regexp = { 'spain': {}, 'chile': {}, 'argentina': {} }
regexp['spain']['es'] = re.compile(ur"""(?im)\{\{\s*fila (BIC|BIC 2)\s*(\|\s*(nombre\s*=\s*(?P<nombre>[^=}]*?)|nombrecoor\s*=\s*(?P<nombrecoor>[^=}]*?)|tipobic\s*=\s*(?P<tipobic>[^=}]*?)|tipo\s*=\s*(?P<tipo>[^=}]*?)|municipio\s*=\s*(?P<municipio>[^=}]*?)|lugar\s*=(?P<lugar>[^=}]*?)|lat\s*=\s*(?P<lat>[0-9\.\-\+]*?)|lon\s*=\s*(?P<lon>[0-9\.\-\+]*?)|bic\s*=\s*(?P<bic>[^=}]*?)|id[_ ]aut\s*=\s*(?P<id_aut>[^=}]*?)|fecha\s*=\s*(?P<fecha>[^=}]*?)|imagen\s*=\s*(?P<imagen>[^=}]*?))\s*)+\s*\|*\s*\}\}""")

"""
{{BIC
| nomeoficial = Castelo da Peroxa
| outrosnomes = 
| paxina = 
| idurl = 
| concello =  [[A Peroxa]]
| lugar = 
| lat = 42.434208 | lon = -7.786825
| id =  RI-51-0008954
| data_declaracion = 17-11-1994
| imaxe = Castelo da Peroxa.JPG
}}
"""

#el campo idurl no aparece en algunas listas, lo ponemos opcional
regexp['spain']['gl'] = re.compile(ur"""(?im)\{\{\s*BIC\s*(\|\s*(nomeoficial\s*=\s*(?P<nombre>[^=}]*?)|\s*outrosnomes\s*=\s*(?P<nombrecoor>[^=}]*?)|\s*paxina\s*=\s*(?P<paxina>[^=}]*?)|idurl\s*=\s*(?P<idurl>[^=}]*?)|concello\s*=(?P<lugar>[^=}]*?)|lugar\s*=(?P<municipio>[^=}]*?)|lat\s*=\s*(?P<lat>[0-9\.\-\+]*?)|lon\s*=\s*(?P<lon>[0-9\.\-\+]*?)|id\s*=\s*(?P<bic>[^=}]*?)|data[_ ]declaracion\s*=\s*(?P<fecha>[^=}]*?)|imaxe\s*=\s*(?P<imagen>[^=}]*?))\s*)+\s*\|*\s*\}\}""")

"""
{{filera BIC
 | nom = [[Murades d'Eivissa|Antigues murades]] i Torre del Campanar
 | nomcoor = Antigues murades i Torre del Campanar (Eivissa)
 | tipus = Arquitectura militar
 | municipi = [[Eivissa (municipi)|Eivissa]]
 | lloc = Dalt Vila
 | lat = 38.908252 | lon = 1.436645
 | bic = RI-51-0001114
 | imatge = EIVISSA 03 (1590948910).jpg
}}

{{filera BCIN
 | nom = [[Palau dels Barons de Pinós|El Palau]] <br/>''Castell de Bagà''
 | nomcoor = El Palau (Bagà)
 | estil = Obra popular, barroc
 | època = XIII / XVIII
 | municipi = [[Bagà]]
 | lloc = Pujada del Palau, 7
 | lat = 42.253394 | lon = 1.861108
 | idurl = 576
 | prot = BCIN
 | bcin = 497-MH
 | bic = RI-51-0005193
 | imatge = 
}}
"""
regexp['spain']['ca'] = re.compile(ur"""(?im)\{\{\s*filera (BIC|BCIN|BIC Val)\s*(\|\s*(nom\s*=\s*(?P<nombre>[^=}]*?)|nomcoor\s*=\s*(?P<nombrecoor>[^=}]*?)|tipus\s*=\s*(?P<tipobic>[^=}]*?)|estil\s*=\s*([^=}]*?)|època\s*=\s*([^=}]*?)|municipi\s*=\s*(?P<municipio>[^=}]*?)|lloc\s*=(?P<lugar>[^=}]*?)|lat\s*=\s*(?P<lat>[0-9\.\-\+]*?)|lon\s*=\s*(?P<lon>[0-9\.\-\+]*?)|idurl\s*=\s*([^=}]*?)|prot\s*=\s*([^=}]*?)|bcin\s*=\s*([^=}]*?)|bic\s*=\s*(?P<bic>[^=}]*?)|fecha\s*=\s*(?P<fecha>[^=}]*?)|imatge\s*=\s*(?P<imagen>[^=}]*?)\s*)\s*)+\s*\|*\s*\}\}""")

#Chile http://commons.wikimedia.org/wiki/Commons:Lists_of_South_American_Monuments/Chile
"""
{{MonumentoChile| id               = 520
| monumento        = Aduana de Iquique
| monumento_desc   = 
| comuna           = 01101
| lat              = -20.211497
| long             = -70.152646
| dirección        = Aníbal Pinto s/n
| decreto          = D. S. 1559
| fecha            = 28-06-1971
| imagen           = Palacio Rímac.JPG
| tipo             = MH
}}
"""
regexp['chile']['commons'] = re.compile(ur"""(?im)\{\{\s*(MonumentoChile|WLM-Chile-monumento)\s*(\|\s*(monumento\s*=\s*(?P<nombre>[^=}]*?)|tipo\s*=\s*(?P<tipo>[^=}]*?)|comuna\s*=\s*(?P<municipio>[^=}]*?)|direcci[óo]n\s*=(?P<lugar>[^=}]*?)|lat\s*=\s*(?P<lat>[0-9\.\-\+]*?)|long?\s*=\s*(?P<lon>[0-9\.\-\+]*?)|id\s*=\s*(?P<bic>[^=}]*?)|fecha\s*=\s*(?P<fecha>[^=}]*?)|imagen\s*=\s*(?P<imagen>[^=}]*?)|monumento[_ ]desc\s*=\s*([^=}]*?)|monumento[_ ]enlace\s*=\s*([^=}]*?)|monumento[_ ]categoría\s*=\s*([^=}]*?)|decreto\s*=\s*([^=}]*?)\s*)\s*)+\s*\|*\s*\}\}""")

#Argentina http://wikilovesmonuments.com.ar/monumentos/
"""
{{MonumentoArgentina
| id               = 002
| monumento        = Algarrobo en las Barrancas de San Isidro
| monumento_enlace = Algarrobo en las Barrancas de San Isidro
| monumento_desc   = 
| municipio        = [[Partido de San Isidro|San Isidro]]
| localidad        = [[San Isidro (Buenos Aires)|San Isidro]]
| lat              = -34.4668633
| long             = -58.5068293
| dirección        = Barrancas de San Isidro
| imagen           = 
| tipo             = Árbol Histórico
}}
"""
regexp['argentina']['es'] = re.compile(ur"""(?im)\{\{\s*MonumentoArgentina\s*(\|\s*(monumento\s*=\s*(?P<nombre>[^=}]*?)|tipo\s*=\s*(?P<tipo>[^=}]*?)|localidad\s*=\s*([^=}]*?)|municipio\s*=\s*(?P<municipio>[^=}]*?)|direcci[óo]n\s*=(?P<lugar>[^=}]*?)|lat\s*=\s*(?P<lat>[0-9\.\-\+]*?)|long?\s*=\s*(?P<lon>[0-9\.\-\+]*?)|id\s*=\s*(?P<bic>[^=}]*?)|imagen\s*=\s*(?P<imagen>[^=}]*?)|monumento[_ ]desc\s*=\s*([^=}]*?)|monumento[_ ]enlace\s*=\s*([^=}]*?)|monumento[_ ]categoría\s*=\s*([^=}]*?)\s*)\s*)+\s*\|*\s*\}\}""")

for country in ['argentina', 'chile', 'spain']:
    missingcoordinates = 0
    missingimages = 0
    total = 0
    provincesstats = []
    errors = {}
    totalerrors = 0
    for anexoid, anexolist in anexos[country].items():
        bics = {}
        if not errors.has_key(anexoid):
            errors[anexoid] = u'&nbsp;'
        for anexo in anexolist:
            print anexo #da problemas cuando se ejecuta con cron
            lang = anexo.split(':')[0]
            s = wikipedia.Site(lang, lang == 'commons' and 'commons' or 'wikipedia')
            wtitle = ':'.join(anexo.split(':')[1:])
            p = wikipedia.Page(s, wtitle)
            if p.isRedirectPage():
                p = p.getRedirectTarget()
            wtext = p.get()
            wtext = removerefs(wtext)
            
            m = ''
            if lang in ['commons', 'es', 'gl', 'ca']:
                if lang not in ['commons', 'es']: #temporal skip while fix ca: lists or ca regexp...
                    continue
                m = regexp[country][lang].finditer(wtext)
            if m:
                for i in m:
                    #print 1
                    bic = '?'
                    try:
                        bic = i.group('bic').strip()
                        bics[bic] = {
                            'lang': lang,
                            'nombre': clean(i.group('nombre').strip()),
                            #'nombrecoor': i.group('nombrecoor').strip(),
                            #'tipobic': i.group('tipobic').strip(),
                            #'tipo': i.group('tipo').strip(),
                            'municipio': clean(i.group('municipio').strip()),
                            'lugar': clean(i.group('lugar').strip()),
                            'lat': i.group('lat').strip(),
                            'lon': i.group('lon').strip(),
                            'bic': bic.strip(),
                            'imagen': i.group('imagen').strip(),
                        }
                        try:
                            bics[bic]['fecha'] = i.group('fecha').strip() #no existe en ca: 
                        except:
                            pass
                    except:
                        totalerrors += 1
                        #print anexoid, wtitle, bic
                        errors[anexoid] += u'<a href="http://%s.%s.org/wiki/%s" target="_blank">%s</a>, \n' % (lang, lang == 'commons' and 'commons' or 'wikipedia', wtitle, bic)

        imageyesurl = u'http://maps.google.com/mapfiles/kml/paddle/red-stars.png'
        imagenourl = u'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png'
        output = u"""<?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2">
            <Document>
            <name>Wiki Loves Monuments</name>
            <description>A map with missing images by location</description>
            <Style id="imageyes">
              <IconStyle>
                <Icon>
                  <href>%s</href>
                </Icon>
              </IconStyle>
            </Style>
            <Style id="imageno">
              <IconStyle>
                <Icon>
                  <href>%s</href>
                </Icon>
              </IconStyle>
            </Style>
        """ % (imageyesurl, imagenourl)

        submissingcoordinates = 0
        submissingimages = 0
        subtotal = 0
        imagesize = '150px'
        for bic, props in bics.items():
            total += 1
            subtotal += 1
            thumburl = ''
            commonspage = ''
            if isvalidimage(props['imagen']):
                #http://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Toronto_-_ON_-_CN_Tower_bei_Nacht2.jpg/398px-Toronto_-_ON_-_CN_Tower_bei_Nacht2.jpg
                filename = re.sub(ur'(?im)([\[\]]|File:|Imagen?:|Archivo:|\|.*)', ur'', props['imagen'])
                filename = re.sub(' ', '_', filename)
                m5 = md5.new(filename.encode('utf-8')).hexdigest()
                thumburl = u'http://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/%s/%s-%s' % (m5[0], m5[:2], filename, imagesize, filename)
                commonspage = u'http://commons.wikimedia.org/wiki/File:%s' % (filename)
            else:
                missingimages += 1
                submissingimages += 1
            
            if not thumburl:
                thumburl = 'http://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Image-missing.svg/%s-Image-missing.svg.png' % (imagesize)
                commonspage = '#'
            
            articleurl = u'http://%s.wikipedia.org/wiki/%s' % (props['lang'], props['nombre'])
            articleurl = re.sub(u' ', u'_', articleurl)
            locatedin = props['municipio']
            if props['lat'] and props['lon']:
                #<a href="http://commons.wikimedia.org/w/index.php?title=Special:Upload&uploadformstyle=basic&wpDestFile=%s - %s - WLM.jpg&wpUploadDescription={{Information%%0D%%0A| Description = %s%%0D%%0A| Source = {{Own}}%%0D%%0A| Date = %%0D%%0A| Author = [[User:{{subst:REVISIONUSER}}|{{subst:REVISIONUSER}}]]%%0D%%0A| Permission = %%0D%%0A| other_versions = %%0D%%0A}}%%0D%%0A{{Selected for WLM 2012 ES|%s}}" target="_blank"><b>Upload</b></a>
                output += u"""
    <Placemark>
    <name>%s</name>
    <description>
    <![CDATA[
    <table border=0 cellspacing=3px cellpadding=3px>
    <tr><td align=right width=80px style="background-color: lightgreen;"><b>BIC:</b></td><td><a href="%s" target="_blank">%s</a></td><td rowspan=4><a href="%s" target="_blank"><img src="%s" width=%s/></a></td></tr>
    <tr><td align=right style="background-color: lightblue;"><b>Located in:</b></td><td>%s</td></tr>
    <tr><td align=right style="background-color: yellow;"><b>ID:</b></td><td>%s</td></tr>
    <tr><td align=center colspan=2><br/><b>This BIC has %s<br/>you can upload yours. Thanks!</b><br/><br/><span style="border: 2px solid black;background-color: pink;padding: 3px;"><a href="http://commons.wikimedia.org/w/index.php?title=Special:UploadWizard&campaign=wlm-es" target="_blank"><b>Upload</b></a></span></td></tr>
    </table>
    ]]>
    </description>
    <styleUrl>#%s</styleUrl>
    <Point>
    <coordinates>%s,%s</coordinates>
    </Point>
    </Placemark>""" % (props['nombre'], articleurl, props['nombre'], commonspage, thumburl, imagesize, locatedin, props['bic'], isvalidimage(props['imagen']) and 'images, but' or 'no images,', isvalidimage(props['imagen']) and 'imageyes' or 'imageno', props['lon'], props['lat'])
            else:
                missingcoordinates +=1
                submissingcoordinates +=1
        
        provincesstats.append([anexoid, subtotal, submissingcoordinates, submissingimages])
        
        output += u"""
        </Document>
    </kml>"""

        f = open('/home/emijrp/public_html/wlm/%s/wlm-%s.kml' % (country, anexoid), 'w')
        f.write(output.encode('utf-8'))
        f.close()
        
        

        
        #beta, enwp: article creator helper
        'nombre''municipio''lugar''lat''lon''bic''imagen'
        output = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html lang="en" dir="ltr" xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <title>enwp: article creator helper</title>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

        <script type="text/javascript">
        function SelectAll(id)
        {
            document.getElementById(id).focus();
            document.getElementById(id).select();
        }
        </script>

        <body>"""
        for bic, props in bics.items():
            if not props.has_key('imagen') or not props['imagen'] or \
               not props.has_key('lat') or not props['lat'] or \
               not props.has_key('lon') or not props['lon'] or \
               not props.has_key('fecha') or not props['fecha']:
                continue
            bic_ = bic
            bic_ = re.sub(ur"(?im)[\.\(\) ]", "", bic_)
            #if not re.search(ur'(?im)^RI-51-\d{7}$', bic_): este año ya valen todos
            name_ = props['nombre']
            name_ = re.sub(ur"(?im) +\(.*$", ur"", name_)
            fecha_ = props['fecha']
            if len(fecha_) == 10 and re.search('-', fecha_):
                fecha_ = fecha_.split('-')[2]
            municipio_ = props['municipio']
            if re.search(ur" \(", municipio_):
                municipio_ = u"%s|%s" % (municipio_, municipio_.split(' (')[0])
            output+=u"""<h4><a href="http://en.wikipedia.org/w/index.php?title=%s&action=edit" target="_blank">%s</a> (<a href="http://en.wikipedia.org/w/index.php?title=Talk:%s&action=edit" target="_blank">Talk</a>: <tt>{{WikiProject Spain|class=stub|importance=}}</tt>)</h4>
    <textarea id='%s-textarea' rows=5 cols=80 onClick="SelectAll('%s-textarea');">{{Infobox Historic Site
    | name = %s
    | native_name = %s
    | native_language = Spanish
    | image = %s
    | caption = 
    | locmapin = Spain
    | latitude = %s
    | longitude = %s
    | location = [[%s]], [[Spain]]
    | area = 
    | built = 
    | architect = 
    | architecture = 
    | governing_body = 
    | designation1 = Spain
    | designation1_offname = %s
    | designation1_type = Non-movable
    | designation1_criteria = Monument
    | designation1_date = %s<ref name="bic" />
    | designation1_number = %s
    }}

    The '''%s''' ([[Spanish language|Spanish]]: ''%s'') is a XYZ located in [[%s]], [[Spain]]. It was declared ''[[Bien de Interés Cultural]]'' in %s.<ref name="bic">{{Bien de Interés Cultural}}</ref>

    == References ==
    {{reflist}}

    {{Spain-struct-stub}}
    </textarea>
    """ % (props['nombre'], props['nombre'], props['nombre'], bic_, bic_, name_, name_, props['imagen'], props['lat'], props['lon'], municipio_, name_, fecha_, bic_, name_, name_, municipio_, fecha_)
        output += u"""</body></html>"""
        f = open('/home/emijrp/public_html/wlm/%s/helper-%s.html' % (country, anexoid), 'w')
        f.write(output.encode('utf-8'))
        f.close()
        #beta, end enwp: article creator helper



    #table bic stats
    tablestats = u'<table border=1px style="text-align: center;">\n'
    tablestats += u'<tr><th width=100px>Lugar</th><th width=60px>Monumentos</th><th width=140px>Con coordenadas</th><th width=100px>Con imágenes</th><th width=100px>Detalles</th><th width=100px>Errores</th></tr>\n'
    provincesstats.sort()
    for p, ptotal, pmissingcoordinates, pmissingimages in provincesstats:
        pcoordper = ptotal and (ptotal-pmissingcoordinates)/(ptotal/100.0) or 0
        pimageper = ptotal and (ptotal-pmissingimages)/(ptotal/100.0) or 0
        refs = u''
        c = 1
        for i in anexos[country][p]:
            refs += u'<a href="http://%s.wikipedia.org/wiki/%s" target="_blank">[%d]</a> ' % (i.split(':')[0], ':'.join(i.split(':')[1:]), c)
            c += 1
        refs = u"""[<a href="javascript:showHide('%s-refs')">Mostrar/Ocultar</a>]<div id="%s-refs" style="display: none;">%s</div>""" % (p, p, refs)
        errorstext = u"""[<a href="javascript:showHide('%s-errors')">Mostrar/Ocultar</a>]<div id="%s-errors" style="display: none;">%s</div>""" % (p, p, errors[p])
        tablestats += u'<tr><td><a href="index.php?place=%s">%s</a></td><td>%d</td><td bgcolor=%s>%d (%.1f%%)</td><td bgcolor=%s>%d (%.1f%%)</td><td>%s</td><td>%s</td></tr>\n' % (p, placenamesconvert(p), ptotal, colors(pcoordper),ptotal-pmissingcoordinates, pcoordper, colors(pimageper), ptotal-pmissingimages, pimageper, refs, errorstext)

    tablestats += u'<tr><td><b>Total</b></td><td><b>%d</b></td><td bgcolor=%s><b>%d (%.1f%%)</b></td><td bgcolor=%s><b>%d (%.1f%%)</b></td><td></td><td>%d</td></tr>\n' % (total, colors(total and (total-missingcoordinates)/(total/100.0) or 0), total-missingcoordinates, total and (total-missingcoordinates)/(total/100.0) or 0, colors(total and (total-missingimages)/(total/100.0) or 0), total-missingimages, total and (total-missingimages)/(total/100.0) or 0, totalerrors)
    tablestats += u'</table>\n'
    #end table stats

    #table user stats
    tableuserstats = u'<table border=1px style="text-align: center;">\n'
    tableuserstats += u'<tr><th width=100px>Usuario</th><th width=60px>Archivos</th><th width=60px>MBytes</th></tr>\n'
    cat = catlib.Category(wikipedia.Site("commons", "commons"), u"Category:%s" % uploadcats[country])
    gen = pagegenerators.CategorizedPageGenerator(cat, start="!")
    pre = pagegenerators.PreloadingGenerator(gen, pageNumber=250)
    usersranking = {}
    for image in pre:
        #(datetime, username, resolution, size, comment)
        date, username, resolution, size, comment = image.getFileVersionHistory()[-1]
        if usersranking.has_key(username):
            usersranking[username][0].append(image.title())
            usersranking[username][1] += size
        else:
            usersranking[username] = [[image.title()], size]
    usersranking_list = [[len(v[0]), k, v[1]] for k, v in usersranking.items()]
    usersranking_list.sort()
    usersranking_list.reverse()
    totalnumpics = 0
    totalnumbytes = 0
    for numpics, username, numbytes in usersranking_list:
        totalnumpics += numpics
        totalnumbytes += numbytes
        tableuserstats += u'<tr><td><a href="http://commons.wikimedia.org/wiki/User:%s" target="_blank">%s</a></td><td><a href="http://commons.wikimedia.org/w/index.php?title=Special:ListFiles&user=%s" target="_blank">%d</a></td><td>%.2f</td></tr>\n' % (username, username, username, numpics, float(numbytes)/(1024*1024))
    tableuserstats += u'<tr><td><b>Total</b></td><td><b><a href="http://commons.wikimedia.org/wiki/Category:Images_from_Wiki_Loves_Monuments_2012_in_Spain" target="_blank">%d</a></b></td><td><b>%.2f</b></td></tr>\n' % (totalnumpics, float(totalnumbytes)/(1024*1024))
    tableuserstats += u'</table>\n'
    #end table user stats


    anexoskeys = anexos[country].keys()
    anexoskeys.sort()

    output = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html lang="en" dir="ltr" xmlns="http://www.w3.org/1999/xhtml">
    <head>
    <title>Wiki Loves Monuments</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta http-equiv="Content-Style-Type" content="text/css" />

    <script language="javascript">
    function showHide(id){
        if (document.getElementById(id).style.display == 'none') {
            document.getElementById(id).style.display = 'block';
        }else{
            document.getElementById(id).style.display = 'none';
        }
    }

    </script>

    </head>

    <?php
    $places = array(%s );
    $place= "%s";
    if (isset($_GET['place']))
    {
        $temp = $_GET['place'];
        if (in_array($temp, $places))
            $place = $temp;
    }

    ?>

    <body style="background-color: lightblue;">
    <center>
    <table width=99%% style="text-align: center;">
    <tr>
    <td>
    <a href="%s" target="_blank"><img src="%s" /></a>
    </td>
    <td>
    <center>
    <big><big><big><b><a href="%s" target="_blank">Wiki <i>Loves</i> Monuments</a></b></big></big></big>
    <br/>
    <b>Del 1 al 30 de septiembre de 2012</b>
    <br/>
    <b>Monumentos:</b> %d [%d con coordenadas (%.1f%%) y %d con imágenes (%.1f%%)] | <b>Leyenda:</b> con imagen <img src="%s" width=20px title="con imagen" alt="con imagen"/>, sin imagen <img src="%s" width=20px title="sin imagen" alt="sin imagen"/>
    </center>
    </td>
    <td>
    <a href="%s" target="_blank"><img src="http://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/LUSITANA_WLM_2011_d.svg/80px-LUSITANA_WLM_2011_d.svg.png" /></a>
    </td>
    </tr>
    <tr>
    <td colspan=3>
    <b>Elige un lugar:</b> %s

    <iframe width="99%%" height="450" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="http://maps.google.com/maps?f=q&amp;source=s_q&amp;hl=es&amp;geocode=&amp;q=http:%%2F%%2Ftoolserver.org%%2F~emijrp%%2Fwlm%%2F%s%%2Fwlm-<?php echo $place; ?>.kml%%3Fusecache%%3D0&amp;output=embed"></iframe>
    <br/>
    <br/>
    <center>

    <!-- div show/hide -->
    <b>Otros mapas:</b> <a href="../argentina">Argentina</a> - <a href="../chile">Chile</a> - <a href="../spain">España</a> | [<a href="javascript:showHide('table-stats')">Mostrar/Ocultar estadísticas</a>]
    <div id="table-stats" style="display: none;">

    <table border=0>
    <tr><td valign=top>%s</td><td valign=top>%s</td></tr>
    </table>

    <!-- /div show/hide -->
    </div>

    </center>
    <i>Actualizado por última vez: %s (UTC). Desarrollado por <a href="http://toolserver.org/~emijrp/">emijrp</a>.</i>
    <br/>
    </td>
    </tr>
    </table>

    </center>
    </body>

    </html>
    """ % (', '.join(['"%s"' % (i) for i in anexoskeys]), capital[country], wmurls[country], wmlogourls[country], wlmurls[country], total, total-missingcoordinates, total and (total-missingcoordinates)/(total/100.0) or 0, total-missingimages, total and (total-missingimages)/(total/100.0) or 0, imageyesurl, imagenourl, wlmurls[country], ', '.join(['<a href="index.php?place=%s">%s</a>' % (i, placenamesconvert(i)) for i in anexoskeys]), country, tablestats, tableuserstats, datetime.datetime.now())

    f = open('/home/emijrp/public_html/wlm/%s/index.php' % (country), 'w')
    f.write(output.encode('utf-8'))
    f.close()

output = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html lang="en" dir="ltr" xmlns="http://www.w3.org/1999/xhtml">
    <head>
    <title>Wiki Loves Monuments</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta http-equiv="Content-Style-Type" content="text/css" />
</head>

<body style="background-color: lightblue;">
<center>
<big><big><big><b>Wiki <i>Loves</i> Monuments</b></big></big></big>
<br/>
<b>Del 1 al 30 de septiembre de 2012</b>
<br/>
<table border=0>
<tr>
<td><big><big><big><b><a href="argentina/">Argentina</a></b></big></big></big></td>
<td><big><big><big><b><a href="chile/">Chile</a></b></big></big></big></td>
<td><big><big><big><b><a href="spain/">España</a></b></big></big></big></td>
</tr>
</table>
</center>

</body>
</html>

"""
f = open('/home/emijrp/public_html/wlm/index.php', 'w')
f.write(output.encode('utf-8'))
f.close()
