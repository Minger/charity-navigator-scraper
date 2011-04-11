
import urllib2
import lxml.etree
import lxml.html
import csv

appid = 99487923783
rec = 1

data = urllib2.urlopen("http://www.charitynavigator.org/feeds/search4/?appid=%d&fromrec=%d" % (appid, rec))
doc = lxml.etree.parse(data)
data.close()

maxrec = int(doc.getroot().get('total'))

results = []

for rec in range(1, maxrec, 25):
    print "Downloading dataset %d out of %d" % ((1+rec/25),maxrec/25)
    data = urllib2.urlopen("http://www.charitynavigator.org/feeds/search4/?appid=%d&fromrec=%d" % (appid, rec)) 
    doc = lxml.etree.parse(data)
    for charity in doc.findall('charity'):
        try:
            results.append(dict((item.tag, item.text.encode('utf-8')) for item in charity.iterchildren()))
        except:
            print "Exception (probably utf-8 encoder)"
            results.append(dict((item.tag, item.text) for item in charity.iterchildren()))
    # with open('xml/%05d.xml' % rec,'wb') as f:
    #       f.write(data.read()) # save a copy, just in case
    data.close()

for charity in results:
    print "Downloading efficiency for organization " + charity['orgid']
    doc = lxml.html.parse(urllib2.urlopen(charity['url'],timeout=600))
    for element in doc.xpath('//div/table/tr/td/a'):
        if element.text=='Fundraising Efficiency':
            try:
                rating = element.getparent().getnext().text.encode('utf-8')
            except:
                print "Exception (probably utf-8 encoder)"
                rating = element.getparent().getnext().text
    charity['efficiency'] = rating
    # with open('html/$05d.html' % charity['orgid'], 'wb') as f:
    #     f.write(data.read())
    data.close()

with open('output.csv','wb') as f:
    fn = "orgid charity_name category efficiency".split()
    writer=csv.DictWriter(f, fieldnames=fn, extrasaction='ignore')
    headers={}
    for n in fn:
        headers[n]=n
    writer.writerow(headers)
    for charity in results:
        writer.writerow(charity)
