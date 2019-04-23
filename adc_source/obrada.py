import datetime 
import numpy
from matplotlib import pyplot
import json

st = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S:%f')
num_of_char_to_read=8*100+100



def obrada_kanala(fname):
    f=open(fname,"r")
    s=f.read(num_of_char_to_read)
    f.close()
    
    kanal=s.split(';')
    kanal.pop() #izbacivanje zadnjeg prazng karactera
    
    
        
    k=[]  
    #prebacivanje stringa u integer
    for x in kanal:
        k.append(int(x))
        
    k_mean=numpy.mean(k)
    k_std=numpy.std(k)
    
    
    
    return([k, k_mean, k_std])
    
    


    
    
kanal1=obrada_kanala('kanal1')
kanal2=obrada_kanala('kanal2')


f=open("data_log.txt","ab")
log={"timestamp": st,
     "kanal1":kanal1[0],
     "kanal1_mean":kanal1[1],
     "kanal1_std":kanal1[2],
     "kanal2":kanal2[0],
     "kanal2_mean":kanal2[1],
     "kanal2_std":kanal2[2],
     }




