import xml.etree.ElementTree as ET
tree = ET.parse('contact_data.xml')
root = tree.getroot()
ibrdtree=ET.parse('ibrdcontact.xml')
root2=ibrdtree.getroot()


def contacttype(num,type):
    cont_id='?'
    for mid in root2.findall('row'):
        if mid.get('mid') == num:
            cont_id=mid.find(type).text
    if cont_id=='?':
        cont_id='unknown'
    return cont_id



def contact(num,flds,types):
    contact={}
    for cont in root.findall('row'):
        for element in types:
            if contacttype(num,element) == 'unknown':
                contact[element]={}
            elif cont.get('id') == contacttype(num,element) :
                d={}
                for tag in flds :
                    d[tag]=cont.find(tag).text
                contact[element]=d

    return contact