# -*- coding: utf-8 -*-

# Copyright (C) 2009 emijrp
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

#todo:
# no contabiliza enlaces con \' en el dump pagelinks? mejorar regexp
# 

import _mysql
import gzip
import re
import os
import sets
import sys
import time

import wikipedia

def percent(c, d=1000):
    if c % d == 0: wikipedia.output(u'Llevamos %d' % c)

def loadProjects(site):
    wikipedia.output(u'Loading projects names')
    projects, projectsall = [], []
    wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/Wikiproyectos')
    if wii.exists() and not wii.isRedirectPage():
        for trozo in wii.get().splitlines():
            trozo=re.sub(ur'(?i) *(Wikiproyecto|Wikiproject) *: *', ur'', trozo.strip())
            trozo=re.sub('_', ' ', trozo).strip()
            projectsall.append(trozo)
            if trozo[0]=='#': continue
            if projects.count(trozo)==0:
                wikipedia.output(u'PR:%s' % trozo)
                projects.append(trozo)
        projectsall.sort()
        wii.put('\n'.join(projectsall), u'BOT - Ordenado lista de wikiproyectos y quitando repeticiones si las hay')
    return projects

def parsePRCAT(site):
    #WhatLinksHere to PRCAT
    
    #parse parameters
    
    #update lists
    
    return None

def loadCategories(site, project):
    categories = []
    wikipedia.output(u'Loading categories for %s project' % project)
    wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Categorías' % project)
    if wii.exists() and not wii.isRedirectPage():
        trozos=wii.get().splitlines()
        for trozo in trozos:
            trozo=re.sub(ur'(?i) *(Categoría|Category) *: *', ur'', trozo.strip())
            trozo=re.sub('_', ' ', trozo)
            if len(trozo)<1 or trozo[0]=='#': continue
            if categories.count(trozo)==0:
                categories.append(trozo)
        categories.sort()
        wii.put('\n'.join(categories), u'BOT - Ordenado lista de categorías y quitando repeticiones si las hay')
    return categories

def loadNewPages(site, limitenuevos):
    nuevos_dic, nuevos_list = {}, []
    newpagesgen=site.newpages(number=limitenuevos)

    for newpage in newpagesgen:
        newpagetitle=newpage[0].title()
        newpagedate=newpage[1]
        newpageuser=re.sub(ur'( \(aún no redactado\)|(Contribuciones|Contributions)\/|\" class\=\"mw\-userlink)', ur'', newpage[4])
        if not nuevos_dic.has_key(newpagetitle):
            nuevos_dic[newpagetitle]={'date':newpagedate,'user':newpageuser}
            nuevos_list.append(newpagetitle) #para conservar orden cronologico usando el indice de la list[]
    
    return nuevos_dic, nuevos_list

def loadTemplates(conn):
    #cargamos page_id y page_title para plantillas
    templates={} #nos va a hacer falta luego para las imagenes inservibles
    conn.query("SELECT page_id, page_title from page where page_namespace=10;")
    c=0
    r=conn.use_result()
    row=r.fetch_row(maxrows=1, how=1)
    while row:
        if len(row)==1:
            page_id=int(row[0]['page_id'])
            page_title=re.sub("_", " ", unicode(row[0]['page_title'], 'utf-8'))
            c+=1;percent(c, 10000)
            templates[page_id]=page_title
        row=r.fetch_row(maxrows=1, how=1)
    wikipedia.output(u"Cargadas %d plantillas de eswiki" % (c))
    return templates

def loadBadImages(conn, templates):
    #generamos lista de imagenes inservibles
    badimages=sets.Set()
    conn.query("SELECT il_from, il_to from imagelinks;")
    c=0;cc=0
    r=conn.use_result()
    row=r.fetch_row(maxrows=1, how=1)
    while row:
        if len(row)==1:
            c+=1;percent(c, 100000)
            il_from=int(row[0]['il_from'])
            try:
                il_to=re.sub('_', ' ', unicode(row[0]['il_to'], "utf-8"))
            except:
                wikipedia.output(row[0]['il_to'])
            if templates.has_key(il_from):
                badimages.add(il_to)
                cc+=1
        row=r.fetch_row(maxrows=1, how=1)
    wikipedia.output(u"%d enlaces a imágenes, %d imágenes inservibles" % (c, cc))
    return badimages

def main():
    lang="es"
    if len(sys.argv)>1:
        lang=sys.argv[1]
    
    #os.system('rm /mnt/user-store/%swiki-latest-pagelinks.sql.gz' % lang) #borramos para descargar luego la versión más nueva
    
    clasificacion={0:u'·',1:u'Destacado',2:u'Bueno',3:u'Esbozo',4:u'Miniesbozo',5:u'Desambiguación'}
    #calidad={0:u'·',1:u'Bueno ([[Imagen:Artículo bueno.svg|14px|Artículo bueno]])',2:u'Destacado ([[Imagen:Cscr-featured.svg|14px|Artículo destacado]])'}
    importancia={0:u'·',1:u'Clase-A',2:u'Clase-B',3:u'Clase-C',4:u'Clase-D'}
    namespaces={104:u'Anexo'}
    namespaces_={104:u'Anexo:'}
    limitenuevos=2000
    avisotoolserver=u'<noinclude>{{aviso|Esta página se actualiza automáticamente. No hagas cambios aquí.}}</noinclude>\n'
    nohay=u':No hay contenido con estas características.'
    
    conn = _mysql.connect(host='sql-s7-rr', db='%swiki_p' % lang, read_default_file='~/.my.cnf')
    site=wikipedia.Site(lang, "wikipedia")
    projects=loadProjects(site)
    [nuevos_dic, nuevos_list]=loadNewPages(site, limitenuevos)
    templates=loadTemplates(conn)
    badimages=loadBadImages(conn, templates)
    
    for project in projects:
        pr=project
        wikipedia.output(u"PR:%s" % project)
        parsePRCAT(site)
        categories=loadCategories(site, project)
        
        for category in categories:
            wikipedia.output(u"  CAT:%s" % category)
        
        #Recorremos CategoryLinks buscando las categorías de este wikiproyecto y capturamos los cl_from
        conn.query("SELECT cl_from, cl_to from categorylinks;")
        r=conn.use_result()
        row=r.fetch_row(maxrows=1, how=1)
        projectpages=sets.Set()
        wikipedia.output(u"Buscando páginas que pertenezcan a este wikiproyecto")
        c=0
        while row:
            if len(row)==1:
                cl_from=int(row[0]['cl_from'])
                cl_to=re.sub("_", " ", unicode(row[0]['cl_to'], 'utf-8'))
                if cl_to in categories and cl_from not in projectpages: # Revisamos todas las categorías de este wikiproyecto
                    projectpages.add(cl_from)
                    c+=1;percent(c)
            row=r.fetch_row(maxrows=1, how=1)
        wikipedia.output(u"A este wikiproyecto pertenecen %d páginas (todos los espacios de nombres, incluso categorías)" % len(projectpages))
        
        #Inicializamos diccionario para las páginas de este wikiproyecto
        conn.query("SELECT page_id, page_title, page_len, page_namespace, page_is_redirect from page where (page_namespace=0 or page_namespace=104);")# and page_is_redirect=0;")
        r=conn.use_result()
        row=r.fetch_row(maxrows=1, how=1)
        c=0
        wikipedia.output(u"Cargando páginas del wikiproyecto %s" % (project))
        pages={}
        pagetitle2pageid={}
        allpageidsnm0=sets.Set()
        allpagetitlesnm0=sets.Set()
        while row:
            if len(row)==1:
                page_id=int(row[0]['page_id'])
                page_title=re.sub('_', ' ', unicode(row[0]['page_title'], 'utf-8'))
                page_len=int(row[0]['page_len'])
                page_nm=int(row[0]['page_namespace'])
                page_is_redirect=int(row[0]['page_is_redirect'])
                page_new=False
                #hace falta para contar enlaces entrantes provenientes del nm=0
                allpageidsnm0.add(page_id) #meter redirecciones también? sí, para que no salgan enlaces rojos de más
                allpagetitlesnm0.add(page_title) #meter redirecciones también? sí, para que no salgan enlaces rojos de más
                if page_is_redirect == 0: #no creamos perfil de página para las redirecciones
                    if nuevos_dic.has_key(page_title):
                        page_new=True
                    if page_id in projectpages:
                        c+=1;percent(c)
                        pagetitle2pageid[page_title]=page_id
                        pages[page_id]={'t':page_title, 'l':page_len, 'nm':page_nm, 'i':0, 'c':0, 'cat':0, 'iws':0, 'im':0, 'en':0, 'f':False, 'con':False, 'rel':False, 'wik':False, 'edit':False, 'ref':False, 'obras':False, 'neutral':False, 'trad':False, 'discutido':False, 'nuevo':page_new}
            row=r.fetch_row(maxrows=1, how=1)
        wikipedia.output(u"Cargadas %d páginas para analizar, solo nm=0 y nm=104, no redirecciones" % (c))
        
        """#Ranking de usuarios
        conn.query("SELECT rc_cur_id, rc_user_text from recentchanges where (rc_namespace=0 or rc_namespace=104);") #rc no muestra si es redirect, pero la filtramos con pages.has_key
        r=conn.use_result()
        row=r.fetch_row(maxrows=1, how=1)
        c=0
        wikipedia.output(u"Cargando cambios recientes a páginas del wikiproyecto %s" % (project))
        users={}
        while row:
            if len(row)==1:
                rc_cur_id=int(row[0]['rc_cur_id'])
                rc_user_text=re.sub('_', ' ', unicode(row[0]['rc_user_text'], 'utf-8'))
                if pages.has_key(rc_cur_id):
                    if users.has_key(rc_user_text):
                        users[rc_user_text]+=1
                    else:
                        users[rc_user_text]=1
                    c+=1;percent(c, 100)
            row=r.fetch_row(maxrows=1, how=1)
        wikipedia.output(u"Se han contado %d cambios recientes a páginas de este wikiproyecto" % (c))
        u=[]
        for k, v in users.items():
            u.append([v, k])
        u.sort()
        u.reverse()
        print u[:15]
        """
        #Recorremos CategoryLinks sumando categorías para los artículos
        conn.query("SELECT cl_from, cl_to from categorylinks;")
        r=conn.use_result()
        row=r.fetch_row(maxrows=1, how=1)
        c=0
        while row:
            if len(row)==1:
                cl_from=int(row[0]['cl_from'])
                cl_to=re.sub("_", " ", unicode(row[0]['cl_to'], 'utf-8'))
                                
                if pages.has_key(cl_from):
                    pages[cl_from]['cat']+=1
                    c+=1;percent(c)
            row=r.fetch_row(maxrows=1, how=1)
        wikipedia.output(u"Las páginas de este wikiproyecto están categorizadas %d veces" % (c))
        
        #Plantillas de mantenimiento
        miniesbozo_pattern=re.compile(ur'(?im)^mini ?esbozo')
        esbozo_pattern=re.compile(ur'(?im)^esbozo')
        desamb_pattern=re.compile(ur'(?im)^(Des|D[ei]sambig|Desambiguaci[oó]n)$')
        destacado_pattern=re.compile(ur'(?im)^Artículo destacado$')
        bueno_pattern=re.compile(ur'(?im)^Artículo bueno$')
        fusionar_pattern=re.compile(ur'(?im)^Fusionar$')
        contextualizar_pattern=re.compile(ur'(?im)^Contextualizar$')
        sinrelevancia_pattern=re.compile(ur'(?im)^Sin ?relevancia$')
        wikificar_pattern=re.compile(ur'(?im)^Wikificar$')
        copyedit_pattern=re.compile(ur'(?im)^Copyedit$')
        sinreferencias_pattern=re.compile(ur'(?im)^(Referencias|Artículo sin fuentes|Unreferenced)$')
        enobras_pattern=re.compile(ur'(?im)^(En ?obras|En ?desarrollo)$')
        noneutral_pattern=re.compile(ur'(?im)^(NN|No ?neutral|NPOV|No ?neutralidad)$')
        traduccion_pattern=re.compile(ur'(?im)^Traducción$')
        discutido_pattern=re.compile(ur'(?im)^Discutido$')
        
        wikipedia.output(u"Cargando enlaces a plantillas")
        conn.query("SELECT tl_from, tl_title from templatelinks where tl_namespace=10;")
        r=conn.use_result()
        row=r.fetch_row(maxrows=1, how=1)
        c=0
        while row:
            if len(row)==1:
                tl_from=int(row[0]['tl_from'])
                try:
                    tl_title=re.sub("_", " ", unicode(row[0]['tl_title'], "utf-8"))
                except:
                    wikipedia.output(row[0]['tl_title'])
                if pages.has_key(tl_from):
                    c+=1;percent(c, 10000)
                    if re.search(destacado_pattern, tl_title): pages[tl_from]['c']=1
                    elif re.search(bueno_pattern, tl_title): pages[tl_from]['c']=2
                    elif re.search(esbozo_pattern, tl_title): pages[tl_from]['c']=3
                    elif re.search(miniesbozo_pattern, tl_title): pages[tl_from]['c']=4
                    elif re.search(desamb_pattern, tl_title): pages[tl_from]['c']=5
                    #sino es ninguna de las 5 cosas, se queda el 0 que significa desconocida
                    
                    if re.search(fusionar_pattern, tl_title): pages[tl_from]['f']=True
                    if re.search(contextualizar_pattern, tl_title): pages[tl_from]['con']=True
                    if re.search(sinrelevancia_pattern, tl_title): pages[tl_from]['rel']=True
                    if re.search(wikificar_pattern, tl_title): pages[tl_from]['wik']=True
                    if re.search(copyedit_pattern, tl_title): pages[tl_from]['edit']=True
                    if re.search(sinreferencias_pattern, tl_title): pages[tl_from]['ref']=True
                    if re.search(enobras_pattern, tl_title): pages[tl_from]['obras']=True
                    if re.search(noneutral_pattern, tl_title): pages[tl_from]['neutral']=True
                    if re.search(traduccion_pattern, tl_title): pages[tl_from]['trad']=True
                    if re.search(discutido_pattern, tl_title): pages[tl_from]['discutido']=True
            row=r.fetch_row(maxrows=1, how=1)
        wikipedia.output(u"%d plantillas de mantenimiento en las páginas de este wikiproyecto" % (c))
        
        #Conteo de imágenes (obviando las inservibles)
        conn.query("SELECT il_from, il_to from imagelinks;")
        r=conn.use_result()
        row=r.fetch_row(maxrows=1, how=1)
        c=0
        while row:
            if len(row)==1:
                il_from=int(row[0]['il_from'])
                try:
                    il_to=re.sub('_', ' ', unicode(row[0]['il_to'], 'utf-8'))
                except:
                    wikipedia.output(row[0]['il_to'])
                if pages.has_key(il_from) and il_to not in badimages:
                    pages[il_from]['i']+=1
                    c+=1;percent(c, 100000)
            row=r.fetch_row(maxrows=1, how=1)
        wikipedia.output(u"%d enlaces a imágenes" % (c))
        
        #Contar interwikis
        conn.query("SELECT ll_from, ll_lang from langlinks;")
        r=conn.use_result()
        row=r.fetch_row(maxrows=1, how=1)
        c=0
        while row:
            if len(row)==1:
                ll_from=int(row[0]['ll_from'])
                try:
                    ll_lang=re.sub('_', ' ', unicode(row[0]['ll_lang'], 'utf-8'))
                except:
                    wikipedia.output(row[0]['ll_lang'])
                if pages.has_key(ll_from):
                    pages[ll_from]['iws']+=1
                    c+=1;percent(c, 500000)
            row=r.fetch_row(maxrows=1, how=1)
        wikipedia.output(u"%d interwikis tienen las páginas de este wikiproyecto" % (c))
        
        #Contar enlaces entrantes
        try:
            f=gzip.open('/mnt/user-store/%swiki-latest-pagelinks.sql.gz' % lang, 'r')
        except:
            os.system('wget http://download.wikimedia.org/%swiki/latest/%swiki-latest-pagelinks.sql.gz -O /mnt/user-store/%swiki-latest-pagelinks.sql.gz' % (lang, lang, lang)) #entorno a 150MB
            f=gzip.open('/mnt/user-store/%swiki-latest-pagelinks.sql.gz' % lang, 'r')
        c=0
        pagelinks_pattern=re.compile(ur'(?i)\((\d+)\,(0|104)\,\'([^\']*?)\'\)[\,\;]') #104 anexo:
        redlinks = {}
        for line in f:
            line=line[:len(line)-1] #evitamos \n
            m=re.findall(pagelinks_pattern, line)
            for i in m:
                c+=1;percent(c, 1000000)
                pl_from=int(i[0])
                pl_nm=int(i[1])
                pl_title=None
                try:
                    pl_title=re.sub('_', ' ', unicode(i[2], 'utf-8'))
                    pl_title=re.sub(ur"\\", ur"", pl_title) #evitamos \ en títulos que tienen comillas protegidas \" en el dump
                except:
                    pl_title=None
                
                if not pl_title:
                    continue
                
                if pl_nm!=0 and pl_nm!=104: #solo nos interesan los enlaces desde nm=0 y hacia nm=0
                    continue
                
                if pl_title not in allpagetitlesnm0: #el enlace va a un artículo que no existe
                    if pages.has_key(pl_from): #si el enlace surge de un artículo de este wikiproyecto (no vamos a coger todos los rojos)
                        if redlinks.has_key(pl_title): #deberíamos almacenar una lista con los ids, para evitar que multiples enlaces desde un mismo artículo sumen como varios, pero bueno...
                            redlinks[pl_title] += 1
                        else:
                            redlinks[pl_title] = 1
                else: #el enlace va a un artículo que sí existe
                    if pagetitle2pageid.has_key(pl_title): #el enlace va a un artículo de este wikiproyecto?
                        pl_to=pagetitle2pageid[pl_title] #ya tenemos en pl_to hacia qué artículo se dirige el enlace
                        if pages.has_key(pl_to): #no debería decir false nunca
                            pages[pl_to]['en'] += 1 #+1 entrante, im es importancia
        wikipedia.output(u"%d enlaces entre páginas" % (c))
        f.close()
        
        #Resto
        #empezamos el analisis propiamente dicho
        limpag=500
        limcabecera=50
        limkblist=5
        cabeceratabla=u'\n|-\n! # !! Artículo !! Disc !! Tamaño !! Clasificación !! Importancia !! Ent !! Cat !! Img !! Iw !! Otros '
        
        wikipedia.output(u'Generando análisis para %s' % project)
        inicio=u'{{Wikipedia:Contenido por wikiproyecto/Inicio|%s}}\n\n== Índice ==\n{{Wikipedia:Contenido por wikiproyecto/%s/Índice}}\n\n== Artículos ==\n\'\'Actualizado por última vez a las {{subst:CURRENTTIME}} ([[UTC]]) del {{subst:CURRENTDAY}} de {{subst:CURRENTMONTHNAME}} de {{subst:CURRENTYEAR}}.\'\'\n<center>\n<span style="clear:left;float:left;">{{#ifexpr:{{SUBPAGENAME}}>1|← [[Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}-1}}|Anterior]]|← Esta es la primera}}</span><span style="clear:right;float:right;">{{#ifexist:Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}+1}}|[[Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}+1}}|Siguiente]] →|Esta es la última →}}</span><span id="arriba">↓ [[#abajo|Ir al final]] ↓</span>\n{| class="wikitable sortable" style="text-align: center;"%s' % (project, project, project, project, project, cabeceratabla)
        fin=u'\n|}\n<span style="clear:left;float:left;">{{#ifexpr:{{SUBPAGENAME}}>1|← [[Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}-1}}|Anterior]]|← Esta es la primera}}</span><span style="clear:right;float:right;">{{#ifexist:Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}+1}}|[[Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}+1}}|Siguiente]] →|Esta es la última →}}</span><span id="abajo">↑ [[#arriba|Ir al principio]] ↑</span>\n</center>\n\n{{Wikipedia:Contenido por wikiproyecto/Fin|%s}}' % (project, project, project, project)
        salida=inicio
        c=0
        resumen={'desconocida':0,'bueno':0,'destacado':0,'esbozo':0,'miniesbozo':0,'desambig':0,'>10':0,'>5':0,'>2':0,'>1':0,'<1':0,'<2':0}
        artstitles, artstitles2 = [], []
        for projectpage in projectpages:
            if pages.has_key(projectpage):
                artstitles.append([pages[projectpage]['t'], projectpage])
                artstitles2.append([pages[projectpage]['en'], pages[projectpage]['t'], projectpage])
        
        #ordenamos alfabeticamente
        artstitles.sort()
        #ordenamos por entrantes
        artstitles2.sort();artstitles2.reverse()
        
        lenartstitles=len(artstitles)
        qclasea=lenartstitles/100*2
        qclaseb=lenartstitles/100*5-qclasea
        qclasec=lenartstitles/100*20-qclaseb
        qclased=lenartstitles-qclasec
        listqclasea, listqclaseb = [], []
        
        #calculamos importancias
        i=0
        for artentrantes, arttitle, artid in artstitles2:
            if i<qclasea:
                pages[artid]['im']=1
                listqclasea.append([artentrantes, arttitle])
            elif i<qclasea+qclaseb:
                pages[artid]['im']=2
                listqclaseb.append([artentrantes, arttitle])
            elif i<qclasea+qclaseb+qclasec:
                pages[artid]['im']=3
            else:
                pages[artid]['im']=4
            i+=1
        
        #ordenamos listas de importancia
        listqclasea.sort();listqclasea.reverse()
        listqclaseb.sort();listqclaseb.reverse()
        
        #generamos salida de listas de importancia
        #A
        listqclaseaplana=u''
        for artentrantes, arttitle in listqclasea:
            if pagetitle2pageid.has_key(arttitle):
                artnm_=u''
                pageid=pagetitle2pageid[arttitle]
                if pages.has_key(pageid):
                    if pages[pageid]['nm']!=0:
                        artnm_=namespaces_[pages[pageid]['nm']]
                    listqclaseaplana+=u'# [[%s%s]] (%d enlaces entrantes)\n' % (artnm_, arttitle, artentrantes)
        #B
        listqclasebplana=u''
        for artentrantes, arttitle in listqclaseb:
            if pagetitle2pageid.has_key(arttitle):
                artnm_=u''
                pageid=pagetitle2pageid[arttitle]
                if pages.has_key(pageid):
                    if pages[pageid]['nm']!=0:
                        artnm_=namespaces_[pages[pageid]['nm']]
                    listqclasebplana+=u'# [[%s%s]] (%d enlaces entrantes)\n' % (artnm_, arttitle, artentrantes)
        #fin listas importancia
        
        #recorremos los articulos del wikiproyecto
        qfusionar=0;qcontextualizar=0;qsinrelevancia=0;qwikificar=0
        qcopyedit=0;qsinreferencias=0;qenobras=0;qnoneutral=0;
        qentraduccion=0;qveracidaddiscutida=0
        relatedchanges=u''
        for arttitle, pageid in artstitles:
            #resumen tamanios
            if pages[pageid]['l']>=10*1024: resumen['>10']+=1
            if pages[pageid]['l']>=5*1024: resumen['>5']+=1
            if pages[pageid]['l']>=2*1024: resumen['>2']+=1
            if pages[pageid]['l']>=1*1024: resumen['>1']+=1
            if pages[pageid]['l']<1*1024: resumen['<1']+=1
            if pages[pageid]['l']<2*1024: resumen['<2']+=1
            
            #resumen calidad
            if pages[pageid]['c']==1: resumen['destacado']+=1
            elif pages[pageid]['c']==2: resumen['bueno']+=1
            elif pages[pageid]['c']==3: resumen['esbozo']+=1
            elif pages[pageid]['c']==4: resumen['miniesbozo']+=1
            elif pages[pageid]['c']==5: resumen['desambig']+=1
            else: resumen['desconocida']+=1
            
            #columna otros
            c+=1
            otros=[]
            if pages[pageid]['f']: qfusionar+=1;otros.append(u'[[Wikipedia:Contenido por wikiproyecto/%s#Fusionar|fusionar]]' % pr)
            if pages[pageid]['con']: qcontextualizar+=1;otros.append(u'[[Wikipedia:Contenido por wikiproyecto/%s#Contextualizar|contextualizar]]' % pr)
            if pages[pageid]['rel']: qsinrelevancia+=1;otros.append(u'[[Wikipedia:Contenido por wikiproyecto/%s#Sin_relevancia|sin relevancia]]' % pr)
            if pages[pageid]['wik']: qwikificar+=1;otros.append(u'[[Wikipedia:Contenido por wikiproyecto/%s#Wikificar|wikificar]]' % pr)
            if pages[pageid]['edit']: qcopyedit+=1;otros.append(u'[[Wikipedia:Contenido por wikiproyecto/%s#Copyedit|copyedit]]' % pr)
            if pages[pageid]['ref']: qsinreferencias+=1;otros.append(u'[[Wikipedia:Contenido por wikiproyecto/%s#Sin_referencias|sin referencias]]' % pr)
            if pages[pageid]['obras']: qenobras+=1;otros.append(u'[[Wikipedia:Contenido por wikiproyecto/%s#En_obras|en obras]]' % pr)
            if pages[pageid]['neutral']: qnoneutral+=1;otros.append(u'[[Wikipedia:Contenido por wikiproyecto/%s#No_neutral|no neutral]]' % pr)
            if pages[pageid]['trad']: qentraduccion+=1;otros.append(u'[[Wikipedia:Contenido por wikiproyecto/%s#En_traducción|en traducción]]' % pr)
            if pages[pageid]['discutido']: qveracidaddiscutida+=1;otros.append(u'[[Wikipedia:Contenido por wikiproyecto/%s#Veracidad_discutida|discutido]]' % pr)
            if pages[pageid]['nuevo']: otros.append(u'[[Wikipedia:Contenido por wikiproyecto/%s#Nuevos|nuevo]]' % pr)
            otros=', '.join(otros)
            
            clasificacionplana=u'' #1 destacado, 2 es bueno, resto: esbozo, miniesbozo, desambig, ·
            if pages[pageid]['c']==1: clasificacionplana=u'[[Wikipedia:Contenido por wikiproyecto/%s#Artículos_destacados|Destacado]]' % pr
            elif pages[pageid]['c']==2: clasificacionplana=u'[[Wikipedia:Contenido por wikiproyecto/%s#Artículos_buenos|Bueno]]' % pr
            else: clasificacionplana=clasificacion[pages[pageid]['c']]
            
            importanciaplana=u''
            if pages[pageid]['im']==1: importanciaplana=u'[[Wikipedia:Contenido por wikiproyecto/%s#Importancia_Clase-A|Clase-A]]' % pr
            elif pages[pageid]['im']==2: importanciaplana=u'[[Wikipedia:Contenido por wikiproyecto/%s#Importancia_Clase-B|Clase-B]]' % pr
            else: importanciaplana=importancia[pages[pageid]['im']]
            
            artnm=u'';artnm_=u''
            if pages[pageid]['nm']!=0:
                artnm=namespaces[pages[pageid]['nm']];artnm+=u' ' # http://es.wikipedia.org/w/index.php?curid=1996845&diff=21475084&oldid=21403165
                artnm_=namespaces_[pages[pageid]['nm']]
            
            salida+=u'\n|-\n| %d || [[%s%s]] || [[%sDiscusión:%s|Disc]] || %d || %s || %s || %d || %d || %d || %d || %s ' % (c, artnm_, arttitle, artnm, arttitle, pages[pageid]['l'], clasificacionplana, importanciaplana, pages[pageid]['en'], pages[pageid]['cat'], pages[pageid]['i'], pages[pageid]['iws'], otros)
            relatedchanges+=u'# [[%s%s]]\n' % (artnm_, arttitle) #pagina 0
            #if c % limcabecera == 0:
            #    salida+=cabeceratabla
            if c % limpag == 0:
                salida+=fin
                wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/%d' % (pr, c/limpag)) #numeracion
                wii.put(salida, u'BOT - Actualizando lista para [[Wikiproyecto:%s]]' % pr)
                salida=inicio
        if salida!=inicio:
            salida+=fin
            wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/%d' % (pr, c/limpag+1)) #numeracion
            wii.put(salida, u'BOT - Actualizando lista para [[Wikiproyecto:%s]]' % pr)
        
        #pagina 0 para hacer relatedchanges
        if len(relatedchanges)<=10: #no existe el wikiproyecto o no tiene páginas asignadas?
            wikipedia.output(u"No existe tal wikiproyecto o no tiene páginas asignadas")
            continue #siguiente wikiproyecto
        if len(relatedchanges)<=1024*500: #limite de KBs #con 1 MB da error el servidor
            try:
                wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/0' % (pr))
                wii.put(relatedchanges, u'BOT - Actualizando lista para [[Wikiproyecto:%s]]' % pr)
            except:
                wikipedia.output(u"Error: No se pudo guardar la página 0 ¿demasiado grande?")
        #fin pagina 0
        
        salida=u''
        for i in range(1, c/limpag+2):
            if salida: salida+=u' – [[Wikipedia:Contenido por wikiproyecto/%s/%d|Página %d]]' % (pr, i, i)
            else: salida+=u'[[Wikipedia:Contenido por wikiproyecto/%s|Resumen]]: [[Wikipedia:Contenido por wikiproyecto/%s/%d|Página %d]]' % (pr, pr, i, i)
        wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Índice' % pr) #index
        wii.put(salida, u'BOT - Actualizando índice para [[Wikiproyecto:%s]]' % pr)
        
        #resumen global
        
        #tabla de clasificacion
        tablaclasificacion=avisotoolserver
        tablaclasificacion+=u'<onlyinclude>{| class="wikitable" style="text-align: center;clear: {{{1|}}};float: {{{1|}}};"\n'
        tablaclasificacion+=u'! colspan=4 | Clasificación !! rowspan=2 | Total '
        tablaclasificacion+=u'\n|-\n! [[Wikipedia:Artículos destacados|Destacado]] [[Imagen:Cscr-featured.svg|14px|Artículo destacado]] !! [[Wikipedia:Artículos buenos|Bueno]] [[Imagen:Artículo bueno.svg|14px|Artículo bueno]] !! [[Wikipedia:Página de desambiguación|Desambiguación]] !! Desconocido'
        tablaclasificacion+=u'\n|-\n| [[Wikipedia:Contenido por wikiproyecto/%s#Artículos destacados|%d]] || [[Wikipedia:Contenido por wikiproyecto/%s#Artículos buenos|%d]] || %d || %d || %d ' % (pr, resumen['destacado'], pr, resumen['bueno'], resumen['desambig'], resumen['desconocida'], lenartstitles)
        tablaclasificacion+=u'\n|-\n| %.1f%% || %.1f%% || %.1f%% || %.1f%% || 100%%' % ((resumen['destacado']/(lenartstitles/100.0)), (resumen['bueno']/(lenartstitles/100.0)), (resumen['desambig']/(lenartstitles/100.0)), (resumen['desconocida']/(lenartstitles/100.0)))
        tablaclasificacion+=u'\n|}</onlyinclude>\n'
        
        wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Resumen/Clasificación' % pr) #resumen
        wii.put(tablaclasificacion, u'BOT - Actualizando tabla de clasificación para [[Wikiproyecto:%s]]' % pr)
        
        #tabla de tamanios
        tablatamanos=avisotoolserver
        tablatamanos+=u'<onlyinclude>{| class="wikitable" style="text-align: center;clear: {{{1|}}};float: {{{1|}}};"\n'
        tablatamanos+=u'! colspan=6 | Tamaño !! rowspan=2 | Total '
        tablatamanos+=u'\n|-\n! > 10 KB !! > 5 KB !! > 2 KB !! > 1 KB !! < 1 KB !! < 2 KB '
        tablatamanos+=u'\n|-\n| %d || %d || %d || %d || %d || %d || %d ' % (resumen['>10'], resumen['>5'], resumen['>2'], resumen['>1'], resumen['<1'], resumen['<2'], lenartstitles)
        tablatamanos+=u'\n|-\n| %.1f%% || %.1f%% || %.1f%% || %.1f%% || %.1f%% || %.1f%% || 100%%' % ((resumen['>10']/(lenartstitles/100.0)), (resumen['>5']/(lenartstitles/100.0)), (resumen['>2']/(lenartstitles/100.0)), (resumen['>1']/(lenartstitles/100.0)), (resumen['<1']/(lenartstitles/100.0)), (resumen['<2']/(lenartstitles/100.0)))
        tablatamanos+=u'\n|}</onlyinclude>\n'
        
        wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Resumen/Tamaños' % pr) #resumen
        wii.put(tablatamanos, u'BOT - Actualizando tabla de tamaños para [[Wikiproyecto:%s]]' % pr)
        
        #tabla de clases (importancia)
        tablaimportancia=avisotoolserver
        tablaimportancia+=u'<onlyinclude>{| class="wikitable" style="text-align: center;clear: {{{1|}}};float: {{{1|}}};"\n'
        tablaimportancia+=u'! colspan=4 | Importancia !! rowspan=2 | Total '
        tablaimportancia+=u'\n|-\n! Clase-A ↑↑ !! Clase-B ↑ !! Clase-C ↓ !! Clase-D ↓↓'
        tablaimportancia+=u'\n|-\n| [[Wikipedia:Contenido por wikiproyecto/%s#Importancia_Clase-A|%d]] || [[Wikipedia:Contenido por wikiproyecto/%s#Importancia_Clase-B|%d]] || %d || %d || %d ' % (pr, qclasea, pr, qclaseb, qclasec, qclased, lenartstitles)
        tablaimportancia+=u'\n|-\n| 1–2%s || 3–5%s || 6–10%s || 11–100%s || 100%s ' % (u'%', u'%', u'%', u'%', u'%')
        tablaimportancia+=u'\n|}</onlyinclude>\n'
        
        wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Resumen/Importancia' % pr) #resumen
        wii.put(tablaimportancia, u'BOT - Actualizando tabla de importancia para [[Wikiproyecto:%s]]' % pr)
        
        #tabla de mantenimiento
        qmantenimiento=qfusionar+qcontextualizar+qsinrelevancia+qwikificar+qcopyedit+qsinreferencias+qenobras+qnoneutral+qentraduccion+qveracidaddiscutida
        tablamantenimiento=avisotoolserver
        tablamantenimiento+=u'<onlyinclude>{| class="wikitable" style="text-align: center;clear: {{{1|}}};float: {{{1|}}};"\n'
        tablamantenimiento+=u'! colspan=3 | Mantenimiento '
        tablamantenimiento+=u'\n|-\n! Fusionar \n| [[Wikipedia:Contenido por wikiproyecto/%s#Fusionar|%d]] \n| %.1f%% ' % (pr, qfusionar, (qfusionar/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! Contextualizar \n| [[Wikipedia:Contenido por wikiproyecto/%s#Contextualizar|%d]] \n| %.1f%% ' % (pr, qcontextualizar, (qcontextualizar/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! Sin relevancia \n| [[Wikipedia:Contenido por wikiproyecto/%s#Sin_relevancia|%d]] \n| %.1f%% ' % (pr, qsinrelevancia, (qsinrelevancia/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! Wikificar \n| [[Wikipedia:Contenido por wikiproyecto/%s#Wikificar|%d]] \n| %.1f%% ' % (pr, qwikificar, (qwikificar/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! Copyedit \n| [[Wikipedia:Contenido por wikiproyecto/%s#Copyedit|%d]] \n| %.1f%% ' % (pr, qcopyedit, (qcopyedit/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! Sin referencias \n| [[Wikipedia:Contenido por wikiproyecto/%s#Sin_referencias|%d]] \n| %.1f%% ' % (pr, qsinreferencias, (qsinreferencias/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! En obras \n| [[Wikipedia:Contenido por wikiproyecto/%s#En_obras|%d]] \n| %.1f%% ' % (pr, qenobras, (qenobras/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! No neutral \n| [[Wikipedia:Contenido por wikiproyecto/%s#No_neutral|%d]] \n| %.1f%% ' % (pr, qnoneutral, (qnoneutral/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! En traducción \n| [[Wikipedia:Contenido por wikiproyecto/%s#En_traducción|%d]] \n| %.1f%% ' % (pr, qentraduccion, (qentraduccion/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! Veracidad discutida \n| [[Wikipedia:Contenido por wikiproyecto/%s#Veracidad_discutida|%d]] \n| %.1f%% ' % (pr, qveracidaddiscutida, (qveracidaddiscutida/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n| Total \n| %d \n| 100%% ' % (qmantenimiento)
        tablamantenimiento+=u'\n|}</onlyinclude>\n'
        
        wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Resumen/Mantenimiento' % pr) #resumen
        wii.put(tablamantenimiento, u'BOT - Actualizando tabla de mantenimiento para [[Wikiproyecto:%s]]' % pr)
        
        #tabla con categorias y numero de articulos que contienen, en desuso
        """categoriasanalizadas=u'{| class="wikitable sortable" style="text-align: center;"\n! #\n! Categoría\n! Artículos'
        categoriasordenadas=[]
        for cat, arts in categories[pr].items():
            categoriasordenadas.append([cat, arts])
        categoriasordenadas.sort()
        cont=1
        for cat, arts in categoriasordenadas:
            categoriasanalizadas+=u'\n|-\n| %d || [[:Categoría:%s|%s]] || %d ' %  (cont, cat, cat, len(arts))
            cont+=1
        categoriasanalizadas+=u'\n|}'"""

        #pagina de resumen con hijas
        resumen=u'\'\'Actualizado por última vez a las {{subst:CURRENTTIME}} ([[UTC]]) del {{subst:CURRENTDAY}} de {{subst:CURRENTMONTHNAME}} de {{subst:CURRENTYEAR}}.\'\'\n'
        resumen+=u'{| style="background-color: transparent"\n| valign=top |\n'
        resumen+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Resumen/Clasificación}}\n' % pr
        resumen+=u'<small>\'\'Esta tabla proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Resumen/Clasificación]]<nowiki>}}</nowiki>\'\'.</small>\n' % pr
        resumen+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Resumen/Tamaños}}\n' % pr
        resumen+=u'<small>\'\'Esta tabla proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Resumen/Tamaños]]<nowiki>}}</nowiki>\'\'.</small>\n' % pr
        resumen+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Resumen/Importancia}}\n' % pr
        resumen+=u'<small>\'\'Esta tabla proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Resumen/Importancia]]<nowiki>}}</nowiki>\'\'.</small>\n' % pr
        resumen+=u'\nEn total han sido analizadas [[Wikipedia:Contenido por wikiproyecto/%s/Categorías|%d categorías]].\n' % (pr, len(categories))
        resumen+=u'| valign=top |\n{{Wikipedia:Contenido por wikiproyecto/%s/Resumen/Mantenimiento}}\n' % pr
        resumen+=u'<small>\'\'Esta tabla proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Resumen/Mantenimiento]]<nowiki>}}</nowiki>\'\'.</small>\n' % pr
        resumen+=u'|}'
        
        #algunos detalles globales más para el resumen
        #todo: enlaces entrantes (resto de propiedades del dic pages?)
        algunaimagen=0.0;algunacategoria=0.0;alguninterwiki=0.0
        totalimagenes=0.0;totalcategorias=0.0;totalinterwikis=0.0
        for page, pagevalues in pages.items():
            if pagevalues['i']>0: algunaimagen+=1.0;totalimagenes+=pagevalues['i']
            if pagevalues['cat']>0: algunacategoria+=1.0;totalcategorias+=pagevalues['cat']
            if pagevalues['iws']>0: alguninterwiki+=1.0;totalinterwikis+=pagevalues['iws']
        
        resumen+=u'Algunos detalles más sobre las %d páginas analizadas:\n' % lenartstitles
        resumen+=u'* %d tienen alguna imagen (%.1f%%) y [[Wikipedia:Contenido por wikiproyecto/%s/Sin imágenes|%d no tienen ninguna]] (%.1f%%). La media de imágenes por página es de %.1f.\n' % (algunaimagen, algunaimagen/(lenartstitles/100.0), pr, lenartstitles-algunaimagen, 100.0-(algunaimagen/(lenartstitles/100.0)), totalimagenes/lenartstitles)
        resumen+=u'* %d tienen alguna categoría (%.1f%%) y %d no tienen ninguna (%.1f%%). La media de categorías por página es de %.1f.\n' % (algunacategoria, algunacategoria/(lenartstitles/100.0), lenartstitles-algunacategoria, 100.0-(algunacategoria/(lenartstitles/100.0)), totalcategorias/lenartstitles)
        resumen+=u'* %d tienen algún interwiki (%.1f%%) y %d no tienen ninguno (%.1f%%). La media de interwikis por página es de %.1f.\n' % (alguninterwiki, alguninterwiki/(lenartstitles/100.0), lenartstitles-alguninterwiki, 100.0-(alguninterwiki/(lenartstitles/100.0)), totalinterwikis/lenartstitles)
        #fin detalles
        
        wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Resumen' % pr) #resumen
        wii.put(resumen, u'BOT - Actualizando resumen para [[Wikiproyecto:%s]]' % pr)
        
        #seccion importancia, mantenimiento
        clasea=avisotoolserver+listqclaseaplana
        claseb=avisotoolserver+listqclasebplana
        
        buenos=avisotoolserver;destacados=avisotoolserver
        fusionar=avisotoolserver;contextualizar=avisotoolserver
        sinrelevancia=avisotoolserver;wikificar=avisotoolserver
        copyedit=avisotoolserver;sinreferencias=avisotoolserver
        enobras=avisotoolserver;noneutral=avisotoolserver
        traduccion=avisotoolserver;discutido=avisotoolserver
        nuevos=avisotoolserver
        enlacesrojos=avisotoolserver
        sinimagenes=avisotoolserver
        nuevos_temp=[]
        
        for arttitle, pageid in artstitles:
            artnm=u'';artnm_=u''
            if pages[pageid]['nm']!=0:
                artnm, artnm_ = namespaces[pages[pageid]['nm']], namespaces_[pages[pageid]['nm']]
            if pages[pageid]['c']==1: destacados+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if pages[pageid]['c']==2: buenos+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if pages[pageid]['f']: fusionar+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if pages[pageid]['con']: contextualizar+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if pages[pageid]['rel']: sinrelevancia+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if pages[pageid]['wik']: wikificar+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if pages[pageid]['edit']: copyedit+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if pages[pageid]['ref']: sinreferencias+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if pages[pageid]['obras']: enobras+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if pages[pageid]['neutral']: noneutral+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if pages[pageid]['trad']: traduccion+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if pages[pageid]['discutido']: discutido+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if pages[pageid]['nuevo']: nuevos_temp.append(arttitle) #los almacenamos para despues ordenarlos cronologicamente
        
        #Nuevos
        for arttitle in nuevos_list:
            if nuevos_temp.count(arttitle)!=0:
                nuevos+=u'# [[%s%s]] (Creado el %s por [[Usuario:%s|%s]])\n' % (artnm_, arttitle, re.sub(ur'\d\d\:\d\d ', ur'', nuevos_dic[arttitle]['date']), nuevos_dic[arttitle]['user'], nuevos_dic[arttitle]['user'])
        
        #Enlaces rojos
        redlinks_temp=[]
        for redlink, count in redlinks.items():
            redlinks_temp.append([count, redlink])
        redlinks_temp.sort()
        redlinks_temp.reverse()
        for count, redlink in redlinks_temp[:500]:
            if count>=5:
                enlacesrojos+=u'# [[%s]] (%d)\n' % (redlink, count)
        
        #Sin imágenes
        sinimagenes_temp=[]
        for pageid, v in pages.items():
            if v['i'] == 0:
                pagetitle=v['t']
                if v['nm']!=0:
                    pagetitle=u"%s%s" % (namespaces_[v['nm']], pagetitle)
                sinimagenes_temp.append(pagetitle)
        sinimagenes_temp.sort()
        c=0
        for sinimagen in sinimagenes_temp:
            c+=1
            if c<=500:
                sinimagenes+=u'# [[%s]]\n' % (sinimagen)
        
        salida=u'== Calidad ==\n'
        subpages=[
            [destacados, u'Artículos destacados', u'[[Imagen:Cscr-featured.svg|14px|Artículo destacado]]'],
            [buenos, u'Artículos buenos', u'[[Imagen:Artículo bueno.svg|14px|Artículo bueno]]'],
            [clasea, u'Importancia Clase-A', u''],
            [claseb, u'Importancia Clase-B', u''],
            [fusionar, u'Fusionar', u''],
            [contextualizar, u'Contextualizar', u''],
            [sinrelevancia, u'Sin relevancia', u''],
            [wikificar, u'Wikificar', u''],
            [copyedit, u'Copyedit', u''],
            [sinreferencias, u'Sin referencias', u''],
            [enobras, u'En obras', u''],
            [noneutral, u'No neutral', u''],
            [traduccion, u'En traducción', u''],
            [discutido, u'Veracidad discutida', u''],
            [nuevos, u'Nuevos', u''],
            [enlacesrojos, u'Enlaces rojos', u''],
            [sinimagenes, u'Sin imágenes', u''],
        ]
        c=0
        for output, subpage, image in subpages:
            if output:
                if output==avisotoolserver:
                    output+=nohay
                wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/%s' % (pr, subpage))
                wii.put(output, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
                salida+=u'=== %s %s ===\n' % (subpage, image)
                salida+=u'{{#ifexpr:{{PAGESIZE:Wikipedia:Contenido por wikiproyecto/%s/%s|R}}<=%d*1024\n' % (pr, subpage, limkblist)
                salida+=u'|:\'\'Esta lista proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/%s]]<nowiki>}}</nowiki>\'\'.\n' % (pr, subpage)
                salida+=u'{{Wikipedia:Contenido por wikiproyecto/%s/%s}}\n' % (pr, subpage)
                salida+=u'|:\'\'Esta lista excede los %d KB y no se mostrará. Se puede consultar directamente en <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/%s]]<nowiki>}}</nowiki>\'\'.\n' % (limkblist, pr, subpage)
                salida+=u'}}\n\n'
            if c==1:
                salida+=u'== Importancia ==\n'
            elif c==3:
                salida+=u'== Mantenimiento ==\n'
            elif c==13:
                salida+=u'== Miscelánea ==\n'
            c+=1
        
        wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Detalles' % pr) #detalles
        wii.put(salida, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
        
        #pagina principal del pr
        salida=u'{{Wikipedia:Contenido por wikiproyecto/Iconos|%s}}\nEsta página muestra el análisis del contenido de Wikipedia en español relacionado con el [[Wikiproyecto:%s]]. Para añadir páginas debes modificar la <span class="plainlinks">[http://es.wikipedia.org/w/index.php?title=Wikipedia:Contenido_por_wikiproyecto/%s/Categorías&action=edit lista de categorías]</span>.\n\n== Índice ==\n{{Wikipedia:Contenido por wikiproyecto/%s/Índice}}\n\n== Resumen ==\n{{Wikipedia:Contenido por wikiproyecto/%s/Resumen}}\n\n{{Wikipedia:Contenido por wikiproyecto/%s/Detalles}}\n\n[[Categoría:Wikipedia:Contenido por wikiproyecto|%s]]\n[[Categoría:Wikipedia:Contenido por wikiproyecto/%s| ]]' % (pr, pr, re.sub(u' ', u'_', pr), pr, pr, pr, pr, pr)
        wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s' % pr) #principal
        wii.put(salida, u'BOT - Actualizando página de [[Wikiproyecto:%s]]' % pr)

    conn.close()

if __name__ == "__main__":
    main()
