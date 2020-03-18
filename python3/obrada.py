import datetime
import numpy
from yaml import safe_load
from time import process_time
from pandas import DataFrame as df
from os.path import exists

LOG_DIR = 'log_mjerenja.csv'


def obrada(config, kanali, zeff):
    start_all=process_time()
    st = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=+1))).strftime('%Y-%m-%d %H:%M:%S:%f')

    r_ntc_25 = config.get('resistor').get('resistance')
    r_ntc_tolerance = config.get('resistor').get('tolerance')
    r_ntc_betta = config.get('resistor').get('betta')
    r_ntc_betta_tolerance = config.get('resistor').get('bettaTolerance')

    r_shunt = config.get('shunt').get('resistance')
    r_shunt_tolerance = config.get('shunt').get('tolerance')
    temperatura_25=25+273.15

    r = numpy.divide(kanali[0], kanali[1])
    r_mean = numpy.mean(r, dtype=numpy.float64)
    r_std = numpy.std(r, dtype=numpy.float64, ddof=1)

    #r_ntc=
    #{-Rs*Zeff*r/(Rs*r - Rs - Zeff)} r=Un/Us
    r_ntc = -r_shunt * r_mean * zeff / (r_shunt * (r_mean - 1) - zeff)

    #utjecaj shunta i omjera napona na std od ntc
    #-Rs*Zeff*r*(1 - r)/(Rs*r - Rs - Zeff)**2 - Zeff*r/(Rs*r - Rs - Zeff)
    r_ntc_std_rs            = - r_shunt * zeff *r_mean *(1-r_mean) /                          \
                            ((r_shunt-1)*r_mean - zeff)**2 - zeff*r_mean/((r_mean-1)*r_shunt-zeff)

    #Rs**2*Zeff*r/(Rs*r - Rs - Zeff)**2 - Rs*Zeff/(Rs*r - Rs - Zeff)
    r_ntc_std_r             = r_shunt**2*zeff*r_mean/                         \
                                ((r_shunt-1)*r_mean - zeff)**2 - \
                                zeff*r_shunt/((r_mean-1)*r_shunt-zeff)

    uncertanty_shunt_tolerance = numpy.divide(r_shunt * r_shunt_tolerance * 0.01, numpy.sqrt(3))             #devijacija otpora shunta prema specifikaciji proizvodjaca
    uncertanty_betta_tolerance = numpy.divide(r_ntc_betta * r_ntc_betta_tolerance * 0.01, numpy.sqrt(3))
    uncertanty_r_ntc_25 = numpy.divide(r_ntc_25 * r_ntc_tolerance * 0.01, numpy.sqrt(3))
    #standardna devijacija ntc-a
    r_ntc_std                       =\
                numpy.sqrt((r_ntc_std_rs*uncertanty_shunt_tolerance)**2 +\
                           (r_ntc_std_r**r_std) **2) #standardna devijacija ntc-a

    #aproksimacija temperature exp jednadzbom
    start=process_time()
    temperatura_e=(numpy.log(r_ntc/r_ntc_25)/r_ntc_betta + 1/(25+273.15))**(-1)-273.15
    end=process_time()
    print("temperatura Exp = {}".format(end-start))
    start=process_time()
    temperatura_e_std=temperatura_25**2*numpy.sqrt(r_ntc_betta**2*r_ntc_25**2*r_ntc_std**2 + r_ntc_betta**2*r_ntc**2*uncertanty_r_ntc_25**2 + r_ntc_25**2*r_ntc**2*uncertanty_betta_tolerance**2*numpy.log(r_ntc/r_ntc_25)**2)/(r_ntc_25*r_ntc*(r_ntc_betta + numpy.log((r_ntc/r_ntc_25)**temperatura_25))**2)
    end=process_time()
    print("temperatura Exp std = {}".format(end-start))
    #aproksimacija temperature polinomom 3 reda
    A1 = 3.354016e-3
    B1 = 2.744032e-4
    C1 = 3.666944e-6
    D1 = 1.375492e-7
    start=process_time()
    temperatura_polinom =   \
                (A1                             + 
                B1*numpy.log(r_ntc/r_ntc_25)    + 
                C1*numpy.log(r_ntc/r_ntc_25)**2 + 
                D1*numpy.log(r_ntc/r_ntc_25)**3   
                )**-1 - 273.15
    end=process_time()
    print("temperatura polinom= {}".format(end-start))           
    start=process_time()
    temperatura_polinom_std=numpy.sqrt(r_ntc_25**2*r_ntc_std **2 + r_ntc**2*uncertanty_r_ntc_25**2)*numpy.abs(B1 + 3*D1*numpy.log(r_ntc/r_ntc_25)**2 + numpy.log((r_ntc/r_ntc_25)**(2*C1)))/ \
            (r_ntc_25*r_ntc*(A1 + C1*numpy.log(r_ntc/r_ntc_25)**2 + D1*numpy.log(r_ntc/r_ntc_25)**3 + numpy.log((r_ntc/r_ntc_25)**B1))**2)
    end=process_time()
    print("temperatura polinom std = {}".format(end-start))
    U_ntc_mean = numpy.mean(kanali[0], dtype=numpy.float64)
    U_ntc_std = numpy.std(kanali[0], dtype=numpy.float64, ddof=1)
    U_shunt_mean = numpy.mean(kanali[1], dtype=numpy.float64)
    U_shunt_std = numpy.std(kanali[1], dtype=numpy.float64, ddof=1)
    U_ntc_m_v, U_ntc_s_v, U_shunt_m_v, U_shunt_s_v = \
        map(lambda x: x * 5 /(0x7fffff), [U_ntc_mean, U_ntc_std, U_shunt_mean, U_shunt_std])

    end_all=process_time() -start_all

    log = {
        "Timestamp": st,
        #"U_ntc_raw":kanali[0],
        "Napon NTC": U_ntc_mean,
        "std NTC": U_ntc_std,
        "Napon SHUNT": U_shunt_mean,
        "std SHUNT": U_shunt_std,
        "Omjer napona sr. vr.": r_mean,
        "std Omjera ntc/shunt": r_std,
        "Napon NTC [V]": U_ntc_m_v,
        "std NTC[V]": U_ntc_s_v,
        "Napon SHUNT[V]": U_shunt_m_v,
        "std SHUNT [V]": U_shunt_s_v,
        #"U_shunt_raw":kanali[1],
        "Otpor": r_ntc,
        "std NTC": r_ntc_std,
        "Utjecaj tolerancije shunta": uncertanty_shunt_tolerance,
        "Temperatura izracunata polinomom": temperatura_polinom,
        'STD Temperature polinomom' : temperatura_polinom_std,
        "Temperatura izracunata exp." : temperatura_e,
        'STD temperature Exp.':temperatura_e_std,
        'Vrijeme obrade' : end_all
    }

    l=df([log])
    #print(l)
    l.to_csv(LOG_DIR, mode='a', sep=';', index= False, header=(not exists(LOG_DIR)))
    return (log)

def open_config(name):
    with open(name, 'r') as f:
        c=safe_load(f)
    return c


if __name__ == "__main__":
    print(obrada(open_config('config.yaml'),[[1,4],[2,6]], 10**6))
