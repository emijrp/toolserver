# -*- coding: utf-8 -*-

import wikipedia, gzip, os, re, datetime, sys
import urllib
import time
import pagegenerators

import tareas

limite=100
if len(sys.argv)>1:
	limite=int(sys.argv[1])

langs=['es']
exitpages={
'es': u'Plantilla:Artículos populares',
}


index='/home/emijrp/temporal/tmpweb.html'
os.system('wget http://dammit.lt/wikistats/ -O %s' % index)
f=open(index, 'r')
wget=f.read()
f.close()
hoy=datetime.date.today()
hoyano=str(hoy.year)
hoymes=str(hoy.month)
if len(hoymes)==1:
	hoymes='0%s' % hoymes
hoydia=str(hoy.day)
if len(hoydia)==1:
	hoydia='0%s' % hoydia
m=re.compile(ur'(?i)\"(pagecounts\-%s%s%s\-\d{6}\.gz)\"' % (hoyano, hoymes, hoydia)).finditer(wget)
#m=re.compile(ur'(?i)\"(pagecounts\-20081201\-\d{6}\.gz)\"').finditer(wget)
gzs=[]
for i in m:
	print i.group(1)
	gzs.append(i.group(1))
gzs=gzs[len(gzs)-1:len(gzs)] #nos quedamos con el ultimo que es el mas reciente
wikipedia.output("Elegidos %d fichero(s)..." % len(gzs))

pagesdic={}
namespaceslists={}
exceptions={}
for lang in langs:
	namespaceslists[lang]=tareas.getNamespacesList(wikipedia.Site(lang, 'wikipedia'))
	exceptions[lang]={}
	exceptions[lang]['raw']='|'.join(namespaceslists[lang])
	exceptions[lang]['compiled']=re.compile(r'(?i)(%s)\:' % exceptions[lang]['raw'])

wikipedia.output("Se van a analizar los idiomas: %s" % ', '.join(langs))
for lang in langs:
	wikipedia.output("Excepciones de %s: %s" % (lang, exceptions[lang]['raw']))

for gz in gzs:
	print gz
	try:
		f=gzip.open('/mnt/user-store/stats/%s' % gz, 'r')
	except:
		#os.system('wget http://dammit.lt/wikistats/%s -O /mnt/user-store/stats/%s' % (gz, gz))
		#f=gzip.open('/mnt/user-store/stats/%s' % gz, 'r')
		sys.exit()
	
	#regex=re.compile(ur'(?im)^([a-z]{2}) (.*?) (\d{1,}) (\d{1,})$') #evitamos aa.b
	regex=re.compile(r'(?im)^(?P<pagelang>%s) (?P<page>.+) (?P<times>\d{1,}) (?P<other>\d{1,})$' % '|'.join(langs)) #evitamos aa.b
	
	c=analized=errores=0
	for line in f:
		line=line[:len(line)-1]
		try:
			line=line.encode('utf-8')
			line=urllib.unquote(line)
		except:
			try:
				line=urllib.unquote(line)
			except:
				wikipedia.output(line)
				errores+=1
				continue
		c+=1
		if c % 250000 == 0:
			print "Leidas %d lineas (%d analizadas, %d errores)" % (c, analized, errores)
			print "%d idiomas" % len(pagesdic.items())
			cc=0
			for proj, projpages in pagesdic.items():
				cc+=1
				if cc<=10:
					print "  %d) %s.wikipedia.org" % (cc, proj)
				else:
					print "    Y algunos mas..."
					break
		
		m=regex.finditer(line)
		for i in m:
			pagelang=i.group('pagelang')
			page=re.sub('_', ' ', i.group('page'))
			
			if re.search(exceptions[pagelang]['compiled'], page):
				continue
			
			times=int(i.group('times'))
			other=int(i.group('other'))
			
			#lang
			if not pagesdic.has_key(pagelang):
				pagesdic[pagelang]={}
			
			#page
			if pagesdic[pagelang].has_key(page):
				pagesdic[pagelang][page]+=times
			else:
				pagesdic[pagelang][page]=times
				analized+=1
	break
	f.close()

#ordenamos de mas visitas a menos, cada idioma
pageslist={}
cc=0
for lang, pages in pagesdic.items():
	cc+=1
	print "Ordenando %s.wikipedia.org [%d/%d]" % (lang, cc, len(pagesdic.items()))
	pageslist[lang] = [(visits, page) for page, visits in pages.items()]
	pageslist[lang].sort()
	pageslist[lang].reverse()
	pageslist[lang] = [(page, visits) for visits, page in pageslist[lang]]

totalvisits={}
for lang, pages in pageslist.items():
	if not totalvisits.has_key(lang):
		totalvisits[lang]=0
	for page, visits in pages:
		totalvisits[lang]+=visits

pageselection={}
for lang, pages in pageslist.items():
	c=0
	pageselection[lang]=[]
	for page, visits in pages:
		if re.search(ur'(?im)(Special\:|sort_down\.gif|sort_up\.gif|sort_none\.gif|\&limit\=)', page): #ampliar con otros idiomas
			continue
		
		c+=1
		if c<=limite*2: #margen de error, pueden no existir las paginas, aunque seria raro
			pageselection[lang].append([urllib.quote(page), visits])
		else:
			break

for lang, list in pageselection.items():
	exitpage=u""
	if exitpages.has_key(lang):
		exitpage=exitpages[lang]
	else:
		exitpage=u'Template:Popular articles'
	
	projsite=wikipedia.Site(lang, 'wikipedia')
	salida=u"<noinclude>{{%s/begin|{{subst:CURRENTHOUR}}}}</noinclude>\n{| class=\"wikitable sortable\" style=\"text-align: center;\" width=350px \n|+ [[Plantilla:Artículos populares|Artículos populares]] en la última hora \n! # !! Artículo !! Visitas " % exitpage
	
	list2=[]
	for quotedpage, visits in list:
		quotedpage=re.sub("%20", " ", quotedpage).strip()
		if quotedpage:
			list2.append(quotedpage)
	gen=pagegenerators.PagesFromTitlesGenerator(list2, projsite)
	pre=pagegenerators.PreloadingGenerator(gen, pageNumber=limite, lookahead=10)
	c=d=0
	sum=0
	ind=-1
	for page in pre:
		detalles=u''
		ind+=1
		if page.exists():
			wtitle=page.title()
			
			if page.isRedirectPage():
				detalles+=u'(#REDIRECT [[%s]]) ' % (page.getRedirectTarget().title())
			elif page.isDisambig():
				detalles+=u'(Desambiguación) '
			else:
				pass
				"""tmpget=page.get()
				if re.search(ur'(?i)\{\{ *Artículo bueno', tmpget):
					detalles+='[[Image:Artículo bueno.svg|14px|Artículo bueno]]'
				if re.search(ur'(?i)\{\{ *(Artículo destacado|Zvezdica)', tmpget):
					detalles+='[[Image:Cscr-featured.svg|14px|Featured article]]'
				if re.search(ur'(?i)\{\{ *(Semiprotegida2?|Semiprotegido|Pp-semi-template)', tmpget):
					detalles+='[[Image:Padlock-silver-medium.svg|20px|Semiprotegida]]'
				if re.search(ur'(?i)\{\{ *(Protegida|Protegido|Pp-template)', tmpget):
					detalles+='[[Image:Padlock.svg|20px|Protegida]]'"""
			
			wikipedia.output('%s - %d - %s' % (wtitle, visits, detalles))
			#continue
			
			if page.namespace() in [6, 14]:
				wtitle=u':%s' % wtitle
			c+=1
			if c-1 in [3,5,10,15,20]:
				salida+=u"\n{{#ifexpr:{{{top|15}}} > %d|" % (c-1)
				d+=1
			salida+=u"\n{{!}}-\n{{!}} %d {{!}}{{!}} [[%s]]{{#if:{{{novistas|}}}||{{!}}{{!}} %s}} " % (c, wtitle, list[ind][1])
			
			sum+=int(list[ind][1])
			
			if c>=limite:
				break
			#except:
			#	wikipedia.output(u'Error al generar item en lista de %s:' % lang)
	
	iws=u''
	for iw in langs:
		if iw!=lang:
			iws+=u'[[%s:%s]]\n' % (iw, exitpage)
	#salida+="\n{{/end}}\n%s" % (iws)
	salida+=u"\n%s\n{{%s/end|%d|%d|top={{{top|15}}}|fecha={{subst:CURRENTTIME}} ([[UTC]]) del {{subst:CURRENTDAY2}}/{{subst:CURRENTMONTH}}/{{subst:CURRENTYEAR}}}}\n|}\n<noinclude>{{documentación de plantilla}}\n%s</noinclude>" % ("}} "*d, exitpage, sum, totalvisits[lang], iws)
	wikipedia.output(salida)
	wiii=wikipedia.Page(projsite, exitpage)
	wiii.put(salida, u'BOT - Updating list')
