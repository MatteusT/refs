from trainPlay import refsecSearch
import os

#str_inp = True
ref_dir = os.path.join('C:\\','Users','Matteus','various papers')
labeled_data ={"article":[], "ref_sec":[]} 
str_inp = ['dftb3.pdf','ZernerPertubation1.pdf','ZernerPertubation2.pdf']
outfile = os.path.join(ref_dir,'labeled_data')
all_labels = []
for istr in str_inp:
#    while str_inp:
#    str_inp = raw_input('input dir for paper: ')
    ref_section = []
    dref = refsecSearch(os.path.join(ref_dir,istr))
    nrows = len(dref.rows)
    print 'There are a total of '+str(nrows)+' rows'
    dref.findrefSection()
    print 'the clusters found are the following'
    print dref.clust
    while True:
        start_val = int(raw_input('from what row do you want to start? '))
        end_val = int(raw_input('until what row? '))
        if start_val != 0:
            try:
                print dref.rows[start_val-1]
            except:
                print dref.rows[start_val-1].encode('utf-8')
            print '_____________________________________'
        for row in dref.rows[start_val:end_val]:
            try:            
                print row
            except:
                print row.encode('utf-8')
        if end_val < nrows-1:
            print '_____________________________________'   
            try:
                print dref.rows[end_val+1]
            except:
                print dref.rows[end_val+1].encode('utf-8')
        verdict = raw_input('Is this the entire ref section? (y/n) ')
        if verdict == 'y':
            ref_section.append([start_val,end_val])
            cont = raw_input('stored... want to search more? (y/n) ')
            if cont == 'y':
                continue
            elif cont == 'n':
                break
        elif verdict == 'n':
            continue
    labeled_data['article'] = os.path.join(ref_dir,istr)
    labeled_data['ref_sec'] = ref_section
    all_labels.append(labeled_data)    
    
import pickle
with open(outfile,'w') as wfile:
    pickle.dump(all_labels, outfile)