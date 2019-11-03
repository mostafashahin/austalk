#!/usr/bin/env python3
import sys, argparse,glob
import numpy as np
from collections import defaultdict
from os.path import join, isdir
from os import makedirs
import re

#This script to convert the ctm file to praat TextGrid file
#Inputs: 1- dir with all ctm files *.ctm, 2- phones.txt, 3- lexicon.txt file needed if word tier, 4- additional mapping (if phonemes need to be mapped to other symbols)
#Outputs: TextGrid file for each speech file with: one or two tiers (phone tiers and optionaly word tier)


def loadCMT(sCmtFile, dAlign):
    aCmt = np.loadtxt(sCmtFile,dtype={'names':('uttId','channel','start','dur','sym'),'formats':('S21','i4','f4','f4','i4')})
    if dAlign is None:
        dAlign = defaultdict(list)
    for item in aCmt:
        sUttId, iCh, fSTime, fDur, iSym = item
        dAlign[sUttId.decode('ascii')].append((iCh, fSTime, fDur, iSym))
    return dAlign


def Generate_TxtGrid(sDir, dAlign, dMapper=None, cSpkrIdDil='', sSuffix = '',bWordTier = False):
    for uttId in dAlign:
        iDilIndx = uttId.find(cSpkrIdDil)
        if iDilIndx > 0 :
            sSaveDir = join(sDir,uttId[:iDilIndx])
            sTxtGridFile = join(sSaveDir,uttId[iDilIndx+1:]+sSuffix+'.TextGrid')
        else:
            sSaveDir = sDir
            sTxtGridFile = join(sSaveDir,uttId+sSuffix+'.TextGrid')

        if not isdir(sSaveDir):
            makedirs(sSaveDir) #Check if success
        lUtt = dAlign[uttId]
        fXmin = lUtt[0][1] #Start time of first phoneme
        fXmax = lUtt[-1][1] + lUtt[-1][2] #Start time of last phoneme + its duration
        nTiers = 1
        nIntervals = len(lUtt)
        #Write file header
        with open(sTxtGridFile,'w') as fTxtGrid:
            print('File type = "ooTextFile"\nObject class = "TextGrid"\n\nxmin = %f\nxmax = %f\ntiers? <exists>\nsize = %d\nitem []:\n\titem [1]:\n\t\tclass = "IntervalTier"\n\t\tname = "Phones"\n\t\txmin = %f\n\t\txmax = %f\n\t\tintervals: size = %d' % (fXmin,fXmax,nTiers,fXmin,fXmax,nIntervals), file=fTxtGrid)
            for i in range(nIntervals):
                iCh, fSTime, fDur, iSym = lUtt[i]
                fETime = fSTime + fDur
                sText = str(iSym) if not dMapper else dMapper[str(iSym)]
                print('\t\tintervals [%d]:\n\t\t\txmin = %f\n\t\t\txmax = %f\n\t\t\ttext = "%s"' % (i+1,fSTime,fETime,sText), file=fTxtGrid)
    return

def prepare_mapper(lMapFiles):
     #The values of the first map file should match the symbols in cmt files usually phones.txt
     #All Map files should be in <symb> <symb> format
     #The value of each additional map file should contains all the keys of the previous file as they sorted in the lMapFiles list
     dMapper = dict(np.loadtxt(lMapFiles[0][0],dtype=str))
     dMasterPtrn = lMapFiles[0][1] #This regx pattern if exist used to rempve any part of the cmt phone symbol to match the mapper
     dMapper = {v:k for k,v in dMapper.items()}
     for sMapFile,ptrn in lMapFiles[1:]:
         d = dict(np.loadtxt(sMapFile,dtype=str))
         d = {v:k for k,v in d.items()}
         for k in dMapper:
             v = ptrn.sub('',dMapper[k]) if ptrn is not None else dMapper[k] 
             if v not in d:
                 print('%s not key in map file %s' % (v,sMapFile))
             dMapper[k] = d[v] if v in d else dMapper[k]
     return dMapper,dMasterPtrn

def ArgParser():
    parser = argparse.ArgumentParser(description='This code for converting ctm alignment file to praat TextGrid file', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('ctm_dir',  help='The path to the directory contains ctm files', type=str)
    parser.add_argument('phones',  help='The path to the phones file that mapping between int to symbol', type=str)
    parser.add_argument('out_dir', help='The path to store TextGrid files', type=str)
    parser.add_argument('-l', '--lexicon', help='The lexicon file mapping between words tp phoneme sequence', dest='lexicon', type=str, default='')
    parser.add_argument('-m', '--phMap', help='Mapping phoneme symbols to other symbols (i.e samba to ipa)', dest='phMap', type=str, default='')
    return parser.parse_args()


if __name__ == '__main__':
    args = ArgParser()
    sCtmDir, sPhonesFile, sOutDir = args.ctm_dir, args.phones, args.out_dir
    sPhoneMapFile = args.phMap
    #Regular expression to remove the position suffix from the key of dictionary
    ptrn_pos = re.compile('_[BIES]')
    dMapper,rPtrn = prepare_mapper(((sPhonesFile,None),(sPhoneMapFile,ptrn_pos)))
    lCmtFiles = glob.glob(join(sCtmDir,'*.cmt'))
    dAlign = defaultdict(list)
    for fCmt in lCmtFiles:
        loadCMT(fCmt,dAlign)
    Generate_TxtGrid(sOutDir, dAlign, dMapper=dMapper, cSpkrIdDil='-', sSuffix = '',bWordTier = False)
