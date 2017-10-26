from bs4 import BeautifulSoup
import requests
import re
import gc


# DO NOT USE THIS TO SPAM THE NCBI SITE!!!
# NCBI is very nice with their API support and requests you make no more than
# 3 requests a second and 200 requests in a session. If you have many requests
# please run them during off times (weekend, 3AM, etc)
def spliterFunction(x):
    lineArray = x.split('\n')
    if len(lineArray) > 1:
        return True
    else:
        return False


def batch(iterable, n=1):  # thank you stack
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

print("Parsing accession numbers...")

inFile = open("ugdh.seq", "r")
seq = inFile.read().split('>')[1:]  # skip the first blank one
splitSeq = list(filter((lambda x: spliterFunction(x)), seq))
seqIDs = list(map((lambda x: x.split('|')[3]), splitSeq))  # the index here depends on your seq format
batchList = []
batchSize = 100
for x in batch(seqIDs, batchSize):
    batchList.append(','.join(x))
batchNum = len(batchList)
print(len(seqIDs))
#  lists for writing
lineage_list = ">"

#  make http POST request from ncbi entrez api
print("Sending ncbi requests...")
url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
for index, values in enumerate(batchList):
    print("Retreiving batch " + str(index + 1) + " of " + str(batchNum))
    data = dict(db='protein', id=values, retmax='100000')
    LineageFile = open("tax_list", "a")
    webIn = requests.post(url, data=data, allow_redirects=True)
    soup = BeautifulSoup(webIn.content, 'html.parser')
    entries = list(str(soup.contents).split("Seq-entry")[1:])
    lineage = list(filter(lambda x: "lineage" in x, str(soup.contents).split(',')))
    lineage_filtered = [''.join(re.findall(r'"([^"]*)"', x)) for x in lineage]
    output = zip(values.split(','), lineage_filtered)
    lineage_list = '>'.join([str(x[0] + '\n' + x[1] + '\n') for x in output])
    LineageFile.write(lineage_list)
    # These shouldn't be necessary but they fix a memory issue
    soup.decompose()
    gc.collect()

print("Complete!")