#!/usr/bin/env python
import ROOT,os,getopt,sys

certJSON = None
minBiasXsec = 69000.
year = "16"

try:
    opts, args = getopt.getopt(sys.argv[1:],"hl:c:y:",["lumiMask",'minBiasXsec','year'])
except getopt.GetoptError:
    print 'Usage : getPileUpData.py -l <lumiMask>'
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print 'Usage : getPileUpData.py -l <lumiMask>'
        sys.exit()
    elif opt in ("-l", "--lumiMask"):
        certJSON = arg
    elif opt in ("-c", "--minBiasXsec"):
        minBiasXsec = eval(arg)
    elif opt in ("-y", "--year"):
        year = arg

certURL = "https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions%s/13TeV" % year
from urllib import urlretrieve
if not os.path.exists(certJSON):
    print "Downloading Lumi JSON file..."
    print "  "+certURL+"/"+certJSON
    urlretrieve(certURL+"/"+certJSON, certJSON)

if not os.path.exists("pileup_latest.txt"):
    print "Downloading Pileup JSON file..."
    print "  "+certURL+"/PileUp/pileup_latest.txt"
    urlretrieve(certURL+"/PileUp/pileup_latest.txt", 'pileup_latest.txt')

puname = certJSON[certJSON.find('Cert_'):-4]
print puname

outfile = open('pileup.py', 'w')
outfile.write('import FWCore.ParameterSet.Config as cms\n')
outfile.write('pileupMap = {\n')
syst = ['', '_Up', '_Dn']
for i, f in enumerate(syst):
    PileUpData = 'PileUpData%s.root'%(f)
    if i == 1: minBiasXsec = minBiasXsec*1.05
    if i == 2: minBiasXsec = minBiasXsec*0.95
    print "!!!!!!", certJSON, minBiasXsec, PileUpData
    command = 'pileupCalc.py -i %s --inputLumiJSON pileup_latest.txt --calcMode true --minBiasXsec %i --maxPileupBin 50 --numPileupBins 50 %s'%(certJSON,minBiasXsec,PileUpData)
    os.system(command)
    tt = ROOT.TFile(PileUpData)
    histo = tt.Get("pileup")
    outfile.write('#%s \n'%command)
    outfile.write('"%s%s":cms.vdouble(\n'%(puname,f))
    for b in range(1, histo.GetNbinsX()+1):
        outfile.write("%e,"%histo.GetBinContent(b))
        if b%5 == 0:
            outfile.write('\n')
    outfile.write('),\n')      
outfile.write('}\n')
