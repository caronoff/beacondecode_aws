import xml.etree.ElementTree as ET
tree = ET.parse('joomla3_cospas_sarsat_tac_beacons.xml')
root = tree.getroot()

def tac(num,flds):
    for child in root:
        d={}
        i=[]
        c=0
        for row in child:
            for t in row.iter('column'):
                if t.get('name') == 'tac_number':

                    if t.text==str(num):
                        print(t.text)
                        c+=1
                        d={}
                        for x in row:
                            for f in flds:
                                if f==x.get('name'):
                                    d[f]=x.text
                        i.append(d)

    return i
if __name__ == "__main__" :
    models=tac(194,['id','name','battery','model_add_names','tested_life','ddd'])

    for d in models:
        for k in d:
            pass #print(k,d[k])
    print(models)
