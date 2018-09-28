import xml.etree.ElementTree as ET
tree = ET.parse('joomla3_cospas_sarsat_tac_beacons.xml')
root = tree.getroot()
def tac(num,flds):
    for child in root:
        d={}
        for row in child:
            for t in row.iter('column'):
                if t.get('name') == 'tac_number':
                    if t.text==str(num):
                        for x in row:
                            for f in flds:
                                if f==x.get('name'):
                                    d[f]=x.text
    return d
if __name__ == "__main__" :
    print(tac(30654,['battery','tested_life','ddd']))
