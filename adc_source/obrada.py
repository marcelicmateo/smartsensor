import datetime 
import numpy
#from matplotlib import pyplot
import json
import math

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
    
    


    
    
kanal1=obrada_kanala('/home/pi/smartsensor/adc_source/kanal1')
kanal2=obrada_kanala('/home/pi/smartsensor/adc_source/kanal2')

rs=10000
srs=rs*0.01         #devijacija otpora shunta
surs=kanal2[2]      #devijacija napona shunta
suntc=kanal1[2]     #devijacija napona ntca

rntc=kanal1[1]/kanal2[1] * rs  #otpor ntca


Untc=rs*suntc/kanal1[1]
Ushunt=kanal1[1]*rs*surs/kanal2[1]**2
Urshunt=kanal1[1]*srs/kanal2[1]

s=math.sqrt(Untc**2+Urshunt**2+Ushunt**2)       #devijacija otpora ntca

temperatura=(math.log(rntc/22000)/3740 + 1/(25+273.15))**(-1)-273.15

#print(temperatura) 



f=open("data_log.txt","a+")
log={"timestamp": st,
     "U_ntc_raw":kanal1[0],
     "U_ntc_mean":kanal1[1],
     "U_ntc_std":kanal1[2],
     "U_shunt_raw":kanal2[0],
     "U_ntc_mean":kanal2[1],
     "U_ntc_std":kanal2[2],
     "otpor_ntc":rntc,
     "devijacija_ntc":s,
     "temperatura":temperatura
     }

y=json.dumps(log)   #log in to file
#print("%s\n" % y)
f.write("%s\n" % y)
f.close()

f=open("/home/pi/mqtt_out","w+")
f.write("%s\n" %y)
f.close





