import sys, os
import re

OneChPhones = ('p','b','t','d','k','g','f','v','T','D','s','z','S','Z','h','m','n','N','l','w','j','W','I','e','{','6','O','U','@')
TwoChPhones = ('tS','dZ','r\\','6:','i:','3:','o:','}:','{I','Ae','oI','@}','{O','I@','e:','U@')

pMultiSpaces = re.compile('[\s]{2,}')

def addPhoneBoundry(trans):
    i = 0
    print('1-', trans)
    while i <len(trans): 
        if trans[i:i+2] in TwoChPhones: 
            trans = trans[:i] +' '+trans[i:i+2]+' '+trans[i+2:] 
            i += 4
        elif trans[i] in OneChPhones: 
            trans = trans[:i] +' '+trans[i:i+1]+' '+trans[i+1:] 
            i += 3
        else:
            print('unkown symbole %s' % trans[i])
            trans = trans[:i] +' '+trans[i:i+1]+' '+trans[i+1:]
            i += 3
    print('2-', trans)
    trans = pMultiSpaces.sub(' ',trans)
    print('3-', trans)
    return trans

def mergeDuplicates(f):
    d = {}
    with open(f,'r') as fin:
        for line in fin:
            aLine = line.split()
            wrd,trans = aLine[0], aLine[1:]
            if wrd not in d:
                d[wrd] = set(trans)
            else:
                d[wrd].union(trans)
    return d

def writeLexicon(d, f):
    with open(f,'w') as fout:
        for wrd in d:
            for trans in d[wrd]:
                print(wrd.upper())
                print(wrd.upper(),addPhoneBoundry(trans),file= fout)
            

if __name__ == '__main__':
    fin, fout = sys.argv[1:3]
    d = mergeDuplicates(fin)
    writeLexicon(d, fout)

