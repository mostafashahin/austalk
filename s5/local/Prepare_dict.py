import sys, os
import re

OneChPhones = ('p','b','t','d','k','g','f','v','T','D','s','z','S','Z','h','m','n','N','l','w','j','W','I','e','{','6','O','U','@')
TwoChPhones = ('tS','dZ','r\\','6:','i:','3:','o:','}:','{I','Ae','oI','@}','{O','I@','e:','U@')

PhoneMap = dict((('p' , 'AA'), 
                 ('b' , 'AB'), 
                 ('t' , 'AC'), 
                 ('d' , 'AD'), 
                 ('k' , 'AF'), 
                 ('g' , 'AG'), 
                 ('tS' , 'AH'), 
                 ('dZ' , 'AI'), 
                 ('f' , 'AJ'), 
                 ('v' , 'AK'), 
                 ('T' , 'AL'), 
                 ('D' , 'AM'), 
                 ('s' , 'AN'), 
                 ('z' , 'AO'), 
                 ('S' , 'AP'), 
                 ('Z' , 'AQ'), 
                 ('h' , 'AR'), 
                 ('m' , 'AS'), 
                 ('n' , 'AT'), 
                 ('N' , 'AU'), 
                 ('l' , 'AV'), 
                 ('r\\' , 'AW'), 
                 ('w' , 'AX'), 
                 ('j' , 'AY'), 
                 ('W' , 'AZ'), 
                 ('6:' , 'BA'), 
                 ('i:' , 'BB'),
                 ('I' , 'BC'), 
                 ('e' , 'BD'), 
                 ('3:' , 'BE'), 
                 ('{' , 'BF'), 
                 ('6' , 'BG'), 
                 ('O' , 'BH'), 
                 ('o:' , 'BI'), 
                 ('U' , 'BJ'), 
                 ('}:' , 'BK'), 
                 ('@' , 'BL'), 
                 ('{I' , 'BM'), 
                 ('Ae' , 'BN'), 
                 ('oI' , 'BO'), 
                 ('@}' , 'BP'), 
                 ('{O' , 'BQ'), 
                 ('I@' , 'BR'), 
                 ('e:' , 'BS')))


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
                trans = addPhoneBoundry(trans)
                trans = ' '.join([PhoneMap[p] for p in trans.split()])
                print(wrd.upper())
                print(wrd.upper(),trans,file= fout)
            

if __name__ == '__main__':
    fin, fout = sys.argv[1:3]
    d = mergeDuplicates(fin)
    writeLexicon(d, fout)

