# csv2xml.py
# FB - 201010107
# First row of the csv file must be header!

# example CSV file: myData.csv
# id,code name,value
# 36,abc,7.6
# 40,def,3.6
# 9,ghi,6.3
# 76,def,99

import csv

csvFile = 'joomla3_cospas_sarsat_contact_details.csv'
xmlFile = 'myData.xml'

csvData = csv.reader(open(csvFile))
xmlData = open(xmlFile, 'w')
xmlData.write('<?xml version="1.0"?>' + "\n")
# there must be only one top-level tag
xmlData.write('<csv_data>' + "\n")

rowNum = 0
for row in csvData:
    if rowNum == 0:
        tags = row
        # replace spaces w/ underscores in tag names
        for i in range(1,len(tags)):
            tags[i] = tags[i].replace(' ', '_')
    else:
        xmlData.write('<row {}={} >'.format(tags[0],row[0]) + "\n")
        for i in range(1,len(tags)):
            xmlData.write('    ' + '<' + tags[i] + '>' \
                          + row[i] + '</' + tags[i] + '>' + "\n")
        xmlData.write('</row>' + "\n")

    rowNum += 1

xmlData.write('</csv_data>' + "\n")
xmlData.close()