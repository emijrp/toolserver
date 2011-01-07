# -*- coding: utf-8 -*-

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
import MySQLdb
import os
import time
import re
import sys

def convert2unix(mwtimestamp):
    #2010-12-25T12:12:12Z
    [year, month, day] = [int(mwtimestamp[0:4]), int(mwtimestamp[5:7]), int(mwtimestamp[8:10])]
    [hour, minute, second] = [int(mwtimestamp[11:13]), int(mwtimestamp[14:16]), int(mwtimestamp[17:19])]
    d = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
    return int((time.mktime(d.timetuple())+1e-6*d.microsecond)*1000)

conn = MySQLdb.connect(host='sql-s1', db='toolserver', read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("SELECT lang, family, CONCAT('sql-s', server) AS dbserver, dbname FROM toolserver.wiki WHERE 1;")
result = cursor.fetchall()
families = ["wikibooks", "wikipedia", "wiktionary", "wikimedia", "wikiquote", "wikisource", "wikinews", "wikiversity", "commons", "wikispecies"]
queries = {
    "all": "SELECT CONCAT(YEAR(rc_timestamp),'-',LPAD(MONTH(rc_timestamp),2,'0'),'-',LPAD(DAY(rc_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(*) AS count FROM recentchanges WHERE rc_timestamp>=DATE_ADD(NOW(), INTERVAL -10 DAY) AND rc_type<=1 GROUP BY date ORDER BY date ASC",
    "bots": "SELECT CONCAT(YEAR(rc_timestamp),'-',LPAD(MONTH(rc_timestamp),2,'0'),'-',LPAD(DAY(rc_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(*) AS count FROM recentchanges WHERE rc_timestamp>=DATE_ADD(NOW(), INTERVAL -10 DAY) AND rc_type<=1 AND rc_bot=1 GROUP BY date ORDER BY date ASC",
    "nobots": "SELECT CONCAT(YEAR(rc_timestamp),'-',LPAD(MONTH(rc_timestamp),2,'0'),'-',LPAD(DAY(rc_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(*) AS count FROM recentchanges WHERE rc_timestamp>=DATE_ADD(NOW(), INTERVAL -10 DAY) AND rc_type<=1 AND rc_bot=0 GROUP BY date ORDER BY date ASC",
}
projects = {}
for row in result:
    time.sleep(0.1)
    #if checked > 10:
    #    break
    lang = row[0]
    family = row[1]
    if family not in families:
        continue
    dbserver = row[2]+"-fast"
    dbname = row[3]
    
    try:
        conn2 = MySQLdb.connect(host=dbserver, db=dbname, read_default_file='~/.my.cnf', use_unicode=True)
        cursor2 = conn2.cursor()
        print "OK:", dbserver, dbname
        #cursor2.execute("SELECT CONCAT(YEAR(rc_timestamp),'-',LPAD(MONTH(rc_timestamp),2,'0'),'-',LPAD(DAY(rc_timestamp),2,'0'),'T',LPAD(HOUR(rc_timestamp),2,'0'),':00:00Z') AS date, COUNT(*) AS count FROM recentchanges WHERE rc_timestamp>=DATE_ADD(NOW(), INTERVAL -10 DAY) AND rc_type<=1 GROUP BY date ORDER BY date ASC")
        projects[dbname] = {}
        for queryname, query in queries.items():
            projects[dbname][queryname] = []
            cursor2.execute(query)
            result2 = cursor2.fetchall()
            for row2 in result2:
                timestamp = convert2unix(row2[0])
                edits = int(row2[1])
                #print timestamp, edits
                projects[dbname][queryname].append([timestamp, edits])
            projects[dbname][queryname] = projects[dbname][queryname][1:] #trip first, it is incomplete
        cursor2.close()
        conn2.close()
    except:
        print "Error in", dbserver, dbname

path = '..'
outputfile = 'wmchart0001.html'
select = ''
var1 = []
var2 = []
var3 = []
c = 0
projects_list = [[k, v] for k, v in projects.items()] # order
projects_list.sort()
for project, values in projects_list:
    if project == 'enwiki_p':
        select += '<option value="%d" selected>%s</option>' % (c, project)
    else:
        select += '<option value="%d">%s</option>' % (c, project)
    var1.append(values["all"])
    var2.append(values["bots"])
    var3.append(values["nobots"])
    c += 1

output = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
 <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>wmcharts - Recent changes edit rate</title>
    <link href="layout.css" rel="stylesheet" type="text/css"></link>
    <!--[if IE]><script language="javascript" type="text/javascript" src="lib/flot/excanvas.min.js"></script><![endif]-->
    <script language="javascript" type="text/javascript" src="lib/flot/jquery.js"></script>
    <script language="javascript" type="text/javascript" src="lib/flot/jquery.flot.js"></script>
 </head>
    <body>
    <h1>Recent changes edit rate</h1>

    <p>&lt;&lt; <a href="index.html">Back</a></p>
    
    <div id="placeholder" style="width:600px;height:300px;"></div>

    <p>This chart shows the recent changes edit rate in the last days.</p>
    
    <p>Choose a project: <select id="projects" onChange="p()">%s</select></p>

<script id="source">
function p() {
    var d1 = %s;
    var d2 = %s;
    var d3 = %s;
    var placeholder = $("#placeholder");
    var selected = document.getElementById('projects').selectedIndex;
    var data = [{ data: d1[selected], label: "All"}, { data: d2[selected], label: "Bots"}, { data: d3[selected], label: "No bots"}];
    var options = { xaxis: { mode: "time" }, lines: {show: true}, points: {show: true}, legend: {noColumns: 3}, };
    $.plot(placeholder, data, options);
}
p();
</script>

 </body>
</html>
""" % (select, str(var1), str(var2), str(var3))

f = open('%s/%s' % (path, outputfile), 'w')
f.write(output)
f.close()
