import datetime
import numpy


def obrada(config, kanali, sps='ADS1256_3750SPS'):
    st = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S:%f')

    zeff = config.get('adc').get('sps_and_zeff').get(sps)
    r_ntc_25 = config.get('resistor').get('resistance')
    r_ntc_tolerance = config.get('resistor').get('tolerance')
    r_ntc_betta = config.get('resistor').get('betta')
    r_ntc_betta_tolerance = config.get('resistor').get('bettaTolerance')

    r_shunt = config.get('shunt').get('resistance')
    r_shunt_tolerance = config.get('shunt').get('tolerance')

    r = numpy.divide(kanali[0], kanali[1])
    r_mean = numpy.mean(r, dtype=numpy.float64)
    r_std = numpy.std(r, dtype=numpy.float64, ddof=1)

    #R_ntc=
    #{-Rs*Zeff*r/(Rs*r - Rs - Zeff)} r=Un/Us
    #proracun u dropboxu, proracun temperature html
    r_ntc = -r_shunt * r_mean * zeff / (r_shunt * (r_mean - 1) - zeff)

    #utjecaj shunta i omjera napona na std od ntc
    #-Rs*Zeff*r*(1 - r)/(Rs*r - Rs - Zeff)**2 - Zeff*r/(Rs*r - Rs - Zeff)
    r_ntc_std_rs            = - r_shunt * zeff *r_mean *(1-r_mean) /                          \
                            ((r_shunt-1)*r_mean - zeff)**2 - zeff*r_mean/((r_mean-1)*r_shunt-zeff)

    #Rs**2*Zeff*r/(Rs*r - Rs - Zeff)**2 - Rs*Zeff/(Rs*r - Rs - Zeff)
    r_ntc_std_r             = r_shunt**2*zeff*r_mean/                         \
                                ((r_shunt-1)*r_mean - zeff)**2 - \
                                zeff*r_shunt/((r_mean-1)*r_shunt-zeff)

    uncertanty_shunt_tolerance = r_shunt * r_shunt_tolerance * 0.01  #devijacija otpora shunta prema specifikaciji proizvodjaca
    uncertanty_betta_tolerance = r_ntc_betta * r_ntc_betta_tolerance * 0.01

    r_ntc_std                       =\
                numpy.sqrt((r_ntc_std_rs*uncertanty_shunt_tolerance)**2 +\
                           (r_ntc_std_r**r_std) **2) #standardna devijacija ntc-a

    #aproksimacija temperature exp jednadzbom
    #temperatura=(numpy.log(r_ntc/r_ntc_25)/r_ntc_betta + 1/(25+273.15))**(-1)-273.15
    A1 = 3.354016e-3
    B1 = 2.744032e-4
    C1 = 3.666944e-6
    D1 = 1.375492e-7

    temperatura =                                             \
                (A1                              + 
                B1*numpy.log(r_ntc/r_ntc_25)    + 
                C1*numpy.log(r_ntc/r_ntc_25)**2 + 
                D1*numpy.log(r_ntc/r_ntc_25)**3   
                )**-1 - 273.15

    U_ntc_mean = numpy.mean(kanali[0], dtype=numpy.float64)
    U_ntc_std = numpy.std(kanali[0], dtype=numpy.float64, ddof=1)
    U_shunt_mean = numpy.mean(kanali[1], dtype=numpy.float64)
    U_shunt_std = numpy.std(kanali[1], dtype=numpy.float64, ddof=1)
    U_ntc_m_v, U_ntc_s_v, U_shunt_m_v, U_shunt_s_v = \
        map(lambda x: x * 5 /(0x7fffff), [U_ntc_mean, U_ntc_std, U_shunt_mean, U_shunt_std])
    log = {
        "timestamp": st,
        #"U_ntc_raw":kanali[0],
        "U_ntc_mean": U_ntc_mean,
        "U_ntc_m_v": U_ntc_m_v,
        " U_ntc_s_v": U_ntc_s_v,
        "U_shunt_m_v": U_shunt_m_v,
        "U_shunt_s_v": U_shunt_s_v,
        "U_ntc_std": U_ntc_std,
        #"U_shunt_raw":kanali[1],
        "U_shunt_mean": U_shunt_mean,
        "U_shunt_std": U_shunt_std,
        "otpor_ntc": r_ntc,
        "std_NTC": r_ntc_std,
        "utjecaj_shunta_us": uncertanty_shunt_tolerance,
        "utjecaj_omjera_napona_r": r_std,
        "omjer_namona_r_mean": r_mean,
        "temperatura": temperatura
    }

    # print("%s\n" % log)

    return (log)


if __name__ == "__main__":
    obrada()
