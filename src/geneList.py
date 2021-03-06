from pyCSV import *
import geneVerifier as geneDB
import geneUtils
import os

__DEBUG=0

def loadEvolutionaryGenes(filename, __ENABLE_GENE_VERIFICATION=0,
        __ENABLE_GENE_UPDATES=0, __CROSS_MATCH_LEVEL = 1, include_studies = [1,2,3,4,5]):
    global __DEBUG
    
    genesTSV = pyCSV()
    genesTSV.load(filename, "\t")
    
    bustamante = []
    vamathevan_human = []
    kosiol_human = []

    if 1 in include_studies:
        bustamante          = [item.lower() for item in geneUtils.columnToList(genesTSV, 1, 2)]
    if 2 in include_studies:
        vamathevan_human    = [item.lower() for item in geneUtils.columnToList(genesTSV, 3, 2)]
    if 3 in include_studies:
        kosiol_human        = [item.lower() for item in geneUtils.columnToList(genesTSV, 8, 2)]
    
    conflicts = []
    
    bakewell = []
    nielsen = []
    
    if 4 in include_studies:
        bakewell, c         = geneUtils.mergeColumns(genesTSV, 12, 13, 2)
        bakewell = [item.lower() for item in bakewell]
        conflicts.extend(c)

    if 5 in include_studies:
        nielsen, c          = geneUtils.mergeColumns(genesTSV, 17, 18, 2)
        nielsen = [item.lower() for item in nielsen]
        conflicts.extend(c)
    
    # verify gene symbols
    
    duplicates = 0
    
    geneCounts = {}
    geneUtils.geneFrequency(geneCounts, bustamante)
    geneUtils.geneFrequency(geneCounts, vamathevan_human)
    geneUtils.geneFrequency(geneCounts, kosiol_human)
    geneUtils.geneFrequency(geneCounts, bakewell)
    geneUtils.geneFrequency(geneCounts, nielsen)
    
    
    
    #duplicates+=geneUtils.addAll(geneSet, bustamante)
    #duplicates+=geneUtils.addAll(geneSet, vamathevan_human)
    #duplicates+=geneUtils.addAll(geneSet, kosiol_human)
    #duplicates+=geneUtils.addAll(geneSet, bakewell)
    #duplicates+=geneUtils.addAll(geneSet, nielsen)
    
    
    
    if __ENABLE_GENE_VERIFICATION:
        for pair in conflicts:
            g1 = pair[0].lower()
            g2 = pair[1].lower()
            
            if __ENABLE_GENE_UPDATES:
                g1parent = geneDB.findUpdatedSymbol(g1)
                g2parent = geneDB.findUpdatedSymbol(g2)
                
                if g1parent != None:
                    g1 = g1parent
                if g2parent != None:
                    g2 = g2parent
            
            if geneDB.isApproved(g1):
                if __DEBUG>1:
                    print "Gene", g2, "not approved, but",g1,"is fine"
                try:
                    geneCounts[g1]+=1
                except KeyError:
                    geneCounts[g1] = 1
                    
            elif geneDB.isApproved(g2):
                if __DEBUG>1:
                    print "Gene", g1, "not approved, but",g2,"is fine"
                try:
                    geneCounts[g2]+=1
                except KeyError:
                    geneCounts[g2] = 1
                    
            else:
                if __DEBUG>1:
                    print "Neither",g1,"nor",g2,"are valid"
        
    
    else:
        for pair in conflicts:
            g1 = pair[0].lower()
            g2 = pair[1].lower()
            
            try:
                geneCounts[g2]+=1
            except KeyError:
                geneCounts[g2] = 1
            
    duplicates, geneSet = geneUtils.addFilterFrequency(geneCounts, __CROSS_MATCH_LEVEL)
    ofile = open(os.sep.join(["results","log","geneSetDuplicateFrequency.txt"]),'w')
    
    glist = []
    
    for gene in geneCounts:
        glist.append((gene, geneCounts[gene]))
        
    for item in sorted(glist, key=lambda item: -item[1]):
        ofile.write("%-20s%d\n" % item)
    
    ofile.close()
    
    geneSet = set([geneUtils.formatGeneSymbol(geneSym) for geneSym in geneSet])
            
    if __ENABLE_GENE_UPDATES:
        geneUtils.updateGeneSet(geneSet)
    
    if __ENABLE_GENE_VERIFICATION:        
        geneUtils.removeInvalidGenes(geneSet)
    
    if __DEBUG>0:
        print "\n-----------------------------"
        print "Total Duplicates:      ", duplicates
        print "Total Name Conflicts:  ", len(conflicts)
        print "Total Genes Remaining: ", len(geneSet)
        print "-----------------------------\n"
        
    log_file = open(os.sep.join(["results","log","loaded_genelist.txt"]),'w')
    for gene in geneSet:
        log_file.write(gene+"\n")
    log_file.close()
    return geneSet
