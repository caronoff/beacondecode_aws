import xml.etree.ElementTree as ET
tree = ET.parse('contact_data.xml')
root = tree.getroot()
ibrdtree=ET.parse('ibrdcontact.xml')
root2=ibrdtree.getroot()


def contacttype(num,type):
    for mid in root2.findall('row'):
        if mid.get('mid') == num:
            cont_id=mid.find(type).text
    return cont_id



def contact(num,flds):

    for mid in root2.findall('row'):
        if mid.get('mid') == num:
            id_no_plb=mid.find('PLB').text
            id_no_elt = mid.find('ELT').text
            id_no_epirb = mid.find('EPIRB').text

    contact={}
    for cont in root.findall('row'):
        for element in ['PLB','ELT','EPIRB']:
            if cont.get('id') == contacttype(num,element) :  #element[1]:
                d={}
                for tag in flds :
                    d[tag]=cont.find(tag).text
                contact[element]=d

    return contact