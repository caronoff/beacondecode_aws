import xml.etree.ElementTree as ET
tree = ET.parse('joomla3_cospas_sarsat_tac_beacons.xml')
root = tree.getroot()
man = ET.parse('joomla3_cospas_sarsat_tac_beacon_manufacturers.xml').getroot()


def manufacturer(num,flds):
    #print(man.tag, man.attrib)
    d = {}
    for c in man:
        for row in c:
            for i in row.iter('column'):
                if i.get('name') == 'id':
                    if i.text == str(num):
                        for x in row:
                            for f in flds:
                                if f == x.get('name'):
                                    d[f] = x.text
    return d








def tac(num,flds):
    for child in root:
        d={}
        i=[]
        c=0
        manufacturer_id=''
        for row in child:
            for t in row.iter('column'):
                if t.get('name') == 'tac_number':
                    if t.text==str(num):
                        c+=1
                        d={}
                        for x in row:
                            for f in flds:
                                if isinstance(f, (dict,)):

                                    man = manufacturer(manufacturer_id,f[next(iter(f))] )
                                    strman=''
                                    for k in man:
                                        strman=strman+man[k]+'<br>'

                                    d[next(iter(f))] = strman
                                elif x.get('name')=='manufacturer_id':
                                    manufacturer_id=x.text

                                elif f==x.get('name'):
                                    d[f]=x.text
                        i.append(d)
    return i
if __name__ == "__main__" :
    models=tac(194,['id','name','battery','model_add_names','tested_life',{'manufacturer_id':['name','short_name']}])

    for d in models:
        for k in d:
            print(k,d[k])
    print(models)

    man=manufacturer(109,['id','name','short_name'])
    #print(man)