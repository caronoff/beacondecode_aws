import xml.etree.ElementTree as ET
tree = ET.parse('contact_data.xml')
root = tree.getroot()
ibrdtree=ET.parse('ibrdcontact.xml')
root2=ibrdtree.getroot()


def contact(num):
    flds=['name','address','city','zipcode','telephone1','telephone2','ci_webpage_1','website_url']
    types = ['PLB', 'ELT','EPIRB']
    for mid in root2.findall('row'):
        if mid.get('mid') == num:
            id_no_plb=mid.find('PLB').text
            id_no_elt = mid.find('ELT').text
            id_no_epirb = mid.find('EPIRB').text

    contact={}
    for cont in root.findall('row'):
        for element in [('PLB',id_no_plb),('ELT',id_no_elt),('EPIRB',id_no_epirb)]:
            if cont.get('id') == element[1]:
                d={}
                for tag in flds :
                    d[tag]=cont.find(tag).text
                contact[element[0]]=d

    return contact