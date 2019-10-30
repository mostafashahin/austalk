#!/usr/bin/env python3

#The main directory of the AusTalk data should contains speakers directory
#items.csv & speakers.csv should be in the main dir
import logging as log
import pandas as pd
import numpy as np
from scipy import stats
import glob, sys
from os.path import join, isdir, isfile, splitext, basename, normpath
import argparse
import re

#Set Logging Config
log.basicConfig(filename='gen_text_utt2spkr.debug',filemode='a',level=log.DEBUG)
logger = log.getLogger('')
logFile = log.FileHandler('gen_text_utt2spkr.log','a')
logFile.setLevel(log.INFO)
console = log.StreamHandler()
console.setLevel(log.DEBUG)
logger.addHandler(logFile)
logger.addHandler(console)

#Normalization regex
pNorm = re.compile('['+re.escape(';\/?!:,"-*')+']')
re.DOTALL
comp2dir = dict((('words-1','words'),
                ('words-1-2','words'),
                ('words-2','words'),
                ('words-2-2','words'),
                ('words-3','words'),
                ('words-3-2','words'),
                ('sentences','sentences'),
                ('sentences-e','sentences'),
                ('story','story'),
                ('digits','digits')))
lAgeRange = range(0,100) #Select all ages
lComponentsName = ['sentences','sentences-e','story','words-1','words-1-2','words-2','words-2-2','words-3','words-3-2'] #Select all read components except digits as we still dont have the Australian pronunciation dictionary of it

def apply_re_on_files(lFiles,lRe,isUpper=False):
    lTrans = []
    for sFile in lFiles:
        with open(sFile,'r') as f:
            sContent = ' '.join(f.read().splitlines()) # some files has more than one line, merge them so one string returned for each file
        for ptrn,repl in lRe:
            sContent = ptrn.sub(repl,sContent)
        if isUpper:
            sContent = sContent.upper()
        lTrans.append(sContent)
    return lTrans

def process_data(sAusDir, fTxt, fUtt2Spk, fWavScp, sSpkrList = '', sPrmptList = '', lCompnt = lComponentsName, lAge=lAgeRange, bExcOutlr = False):
    

    sDataDir = join(sAusDir,'speakers')
    sSpeakersMeta = join(sAusDir,'speakers.csv')
    sItemsMeta = join(sAusDir,'items.csv')
    if bExcOutlr:
        sFileDur = join(sAusDir,'fileDur.csv')
        if not isfile(sFileDur):
            log.warning('%s file not exist, Exclude outlier disabled' % sFileDur)
            bExcOutlr = False

    #Check if speakers folder, speaker metadata file, items metadata file are exist
    if not isdir(sDataDir):
        log.error('%s directory not exist' % sDataDir)
        return
    if not isfile(sSpeakersMeta):
        log.error('%s file not exist' % sSpeakersMeta)
        return
    if not isfile(sItemsMeta):
        log.error('%s file not exist' % sItemsMeta)
        return

    #Load metadata
    dItems = pd.read_csv(sItemsMeta)
    dSpeakers = pd.read_csv(sSpeakersMeta)

    #Load Speaker list file if any
    #print(sSpkrList)
    if isfile(sSpkrList):#Load list of selected speakers 
        with open(sSpkrList) as fSpkrList:
            lSelectSpkrs = fSpkrList.read().splitlines()
        log.info('Number of required speakers %d' % len(lSelectSpkrs))
    else:
        lSelectSpkrs = None
    
    #Load Prompts list file if any
    if isfile(sPrmptList): 
        with open(sPrmptList) as fPrmptList:
            lSelectPrompts = fPrmptList.read().splitlines()
        log.info('Number of required prompts: %d' % len(lSelectPrompts))
    else:
        lSelectPrompts = None 

    dSelected = dItems
    if lSelectSpkrs != None:
    #TODO: Add one for age filtering
        dSelected = dSelected[dSelected.speaker.isin(lSelectSpkrs)]
    
    if lCompnt:
        dSelected = dSelected[dSelected.componentName.isin(lCompnt)]
    
    if lSelectPrompts != None:
        dSelected = dSelected[dSelected.prompt.isin(lSelectPrompts)]
#TODO make sure this is working correctly and remove all 0 dur files     
    #Exclude outliers
    if bExcOutlr:
        dFileDur = pd.read_csv(sFileDur)
        dSelected = pd.merge(dSelected,dFileDur,left_on='media',right_on='file') 
        indxs = []
        dSelected = dSelected[dSelected.duration > 0.0]
        for p in dSelected.prompt.unique():
            log.debug('Check prompt %s' % p)
            d = dSelected[dSelected.prompt == p]['duration']
            log.debug('%d items Found' % d.shape[0])
            x = d[np.abs(stats.zscore(d)) < 3]
            log.debug('%d items selected' % x.index.shape[0])
            indxs.extend(x.index)
        dSelected = dSelected.loc[indxs]
    

    nFiles = dSelected.shape[0]
    nSpeakers = dSelected.speaker.unique().shape[0]
    nPrompts = dSelected.prompt.unique().shape[0]
    lCompnts = dSelected.componentName.unique()
    log.info('Total number of selected files: %d' % nFiles)
    log.info('Total number of selected speakers: %d' % nSpeakers)
    log.info('Total number of unique prompts: %d' % nPrompts)
    log.info('List of Components: %s' % ' '.join(lCompnts))
    
    nNotFound = 0
    
    for indx, row in dSelected.iterrows():
        sSpkId = row['speaker']
        sTrans = pNorm.sub('',row['prompt'])
        sComp = row['componentName']
        sWav = row['media']
        sUttId = sWav.replace('-ch6-speaker16.wav','') #the Utt ID taken from the file name instead of item as there is some items linked to multiple files
        sWavPath = join(sDataDir,sSpkId,comp2dir[sComp],sWav)
        log.debug('Procesing file: %s' % sWavPath)
        if isfile(sWavPath):
            print(sSpkId+'-'+sUttId, sTrans.upper(), file=fTxt)
            print(sSpkId+'-'+sUttId, sSpkId, file=fUtt2Spk)
            print(sSpkId+'-'+sUttId, sWavPath, file=fWavScp)
        else:
            nNotFound += 1
            log.warning('%d File: %s Not Exist' % (nNotFound, sWavPath))
    return

class str2list(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(str2list, self).__init__(option_strings, dest, **kwargs)
    def parse_str(self,text):
        r = []
        for p in text.split(','):
            if '-' in p and p.split('-')[0].isnumeric():
                s, e = [int(i) for i in p.split('-')]
                r.extend(range(s,e+1))
            else:
                r.append(int(p) if p.isnumeric() else p)
        return r
    def __call__(self, parser, namespace, values, option_string=None):
        #print('%r %r %r' % (namespace, values, option_string))
        setattr(namespace, self.dest, self.parse_str(values))

def ArgParser():
    parser = argparse.ArgumentParser(description='This code for creating Kaldi files for OGI Kids dataset', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('AusTalk_Dir',  help='The path to the main directory of AusTalk data', type=str)
    parser.add_argument('Text_File',  help='The path to the text file with <UttID> <Trans>', type=str)
    parser.add_argument('Utterance_to_Speakers_File',  help='The path to the Utterance to Speaker mapping file', type=str)
    parser.add_argument('Wav_Scp_File',  help='The path to the file should contain list of wav files <RecID> <wavfile>', type=str)
    parser.add_argument('-l', '--spkrl', help='The file contains list of selected speakers', dest='spkrl', type=str, default='')
    parser.add_argument('-p', '--prompt', help='The file contains list of selected prompts', dest='prmptl', type=str, default='')
    parser.add_argument('-c', '--compnt', help='The list of components to be used', dest='cmpt', action=str2list, default=['sentences','sentences-e','story','words-1','words-1-2','words-2','words-2-2','words-3','words-3-2'])
    parser.add_argument('-a', '--age', dest='age', help='The list of ages to be included', action=str2list, default=list(range(0,100)))
    parser.add_argument('-x','--excld', help='Use this option to exclude outliers files based on duration, file fileDur.csv should be exist in AusTalk Dir', dest='exc_outlr', action='store_true',default=False)
    return parser.parse_args()

if __name__ == '__main__':
    args = ArgParser()
    sAusDir, sTxt, sUtt2Spk, sWavScp = args.AusTalk_Dir, args.Text_File, args.Utterance_to_Speakers_File, args.Wav_Scp_File
    sSpkrList = args.spkrl
    sPrmptList = args.prmptl
    lCompnt = args.cmpt
    lAge = args.age
    bExcOutlr = args.exc_outlr
    with open(sTxt,'a') as fTxt, open(sUtt2Spk,'a') as fUtt2Spk, open(sWavScp,'a') as fWavScp:
        process_data(sAusDir, fTxt, fUtt2Spk, fWavScp, sSpkrList=sSpkrList, sPrmptList = sPrmptList, lCompnt = lCompnt, lAge = lAge, bExcOutlr = bExcOutlr)




    



