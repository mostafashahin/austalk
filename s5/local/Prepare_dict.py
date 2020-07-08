#!/usr/bin/env python3

import sys, os
import re
#TODO add comment to show how this works
#TODO use argparser and logging

pNorm = re.compile('['+re.escape(';\/?!:,"-*')+']')
sStrsCh = "`" #Indicating the stressed syllable
sHyphen = "-"
sPeriod = "."
sSemi = ";"

OneChPhones = ('p','b','t','d','k','g','f','v','T','D','s','z','S','Z','h','m','n','N','l','w','j','W','I','e','{','6','O','U','@','A','E','r','a')
TwoChPhones = ('tS','dZ','r\\','6:','i:','3:','o:','}:','{I','Ae','oI','@}','{O','I@','e:','U@','@U','u:','a:','@:')

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
                 ('r' , 'AW'), 
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
                 ('e:' , 'BS'),
                 ('U@' , 'BT'),
                 ('@U' , 'BU'),
                 ('A' , 'BV'),
                 ('E' , 'BX'),
                 ('r\\' , 'BW'),
                 ('u:' , 'BY'),
                 ('a' , 'BZ'),
                 ('a:' , 'CA'),
                 ('@:' , 'CB')))


pMultiSpaces = re.compile('[\s]{2,}')

def addPhoneBoundry(trans):
    i = 0
    trans = trans.replace(sStrsCh,'')
    trans = trans.replace(sHyphen,'')
    trans = trans.replace(sPeriod,'')
    trans = trans.replace(sSemi,'')
    trans = trans.replace('%','')

    #print('1-', trans)
    while i <len(trans): 
        if trans[i:i+2] in TwoChPhones: 
            trans = trans[:i] +' '+trans[i:i+2]+' '+trans[i+2:] 
            i += 4
        elif trans[i] in OneChPhones: 
            trans = trans[:i] +' '+trans[i:i+1]+' '+trans[i+1:] 
            i += 3
        else:
            #print('unkown symbole %s' % trans[i])
            trans = trans[:i] +' '+trans[i:i+1]+' '+trans[i+1:]
            i += 3
    #print('2-', trans)
    trans = pMultiSpaces.sub(' ',trans)
    #print('3-', trans)
    return trans

def mergeDuplicates(f):
    d = {}
    with open(f,'r') as fin:
        for line in fin:
            aLine = line.split()
            wrd,trans = pNorm.sub('',aLine[0]), aLine[1:]
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
                #print(wrd.upper())
                print(wrd.upper(),trans,file= fout)
            

if __name__ == '__main__':
    fin, fout = sys.argv[1:3]
    d = mergeDuplicates(fin)
    writeLexicon(d, fout)

