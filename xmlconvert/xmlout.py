import xml.etree.ElementTree as ET
tree = ET.parse('myData.xml')
root = tree.getroot()
for contact in root.findall('row'):
    if contact.get('id')=='5620':
        print(contact.find('name').text)

