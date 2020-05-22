import datetime
import numpy
from yaml import safe_load
from time import process_time


def obrada(config, kanali, zeff):
    start_all = process_time()
    st = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=+1))
    ).strftime("%Y-%m-%d %H:%M:%S")

    r_ntc_25 = config.get("ntcresistance")
    r_ntc_tolerance = config.get("ntctolerance")
    r_ntc_betta = config.get("betta")
    r_ntc_betta_tolerance = config.get("bettatolerance")

    r_shunt = config.get("shuntresistance")
    r_shunt_tolerance = config.get("shunttolerance")
    temperatura_25 = 25 + 273.15

    r = numpy.divide(kanali[0], kanali[1])
    r_mean = numpy.mean(r, dtype=numpy.float64)
    r_std = numpy.std(r, dtype=numpy.float64, ddof=1)

    # r_ntc=
    # R_shunt*Zeff*r/(-R_shunt*r + R_shunt + Zeff)

    r_ntc = r_mean * zeff *r_shunt / (r_shunt - r_mean * r_shunt + zeff)
    #print(zeff, r_shunt, r_mean )

    # utjecaj shunta i omjera napona na std od ntc
    #utjecaj omjera napona 
    # R_shunt*Zeff*(R_shunt + Zeff)/(-R_shunt*r + R_shunt + Zeff)**2
    r_ntc_std_rs = zeff*r_shunt * (r_shunt + zeff) / (r_shunt + zeff -r_mean *r_shunt )**2

    #utjecaj shunta 
    # Zeff**2*r/(-R_shunt*r + R_shunt + Zeff)**2

    r_ntc_std_r = -zeff **2 * r_mean / (r_shunt + zeff -r_mean *r_shunt)**2
    #print( r_ntc_std_r)

    uncertanty_shunt_tolerance = numpy.divide(
        r_shunt * r_shunt_tolerance * 0.01, numpy.sqrt(3)
    )  # devijacija otpora shunta prema specifikaciji proizvodjaca
    uncertanty_betta_tolerance = numpy.divide(
        r_ntc_betta * r_ntc_betta_tolerance * 0.01, numpy.sqrt(3)
    )
    uncertanty_r_ntc_25 = numpy.divide(r_ntc_25 * r_ntc_tolerance * 0.01, numpy.sqrt(3))
    # standardna devijacija ntc-a
    r_ntc_std = numpy.sqrt(
        (r_ntc_std_rs * uncertanty_shunt_tolerance) ** 2 + (r_ntc_std_r ** r_std) ** 2
    )  # standardna devijacija ntc-a

    # aproksimacija temperature exp jednadzbom
    start = process_time()
    temperatura_e = (numpy.log(r_ntc / r_ntc_25) / r_ntc_betta + 1 / (25 + 273.15)) ** (
        -1
    ) - 273.15
    end = process_time()
    # print("temperatura Exp = {}".format(end - start))
    start = process_time()
    temperatura_e_std = (
        temperatura_25 ** 2
        * numpy.sqrt(
            r_ntc_betta ** 2 * r_ntc_25 ** 2 * r_ntc_std ** 2
            + r_ntc_betta ** 2 * r_ntc ** 2 * uncertanty_r_ntc_25 ** 2
            + r_ntc_25 ** 2
            * r_ntc ** 2
            * uncertanty_betta_tolerance ** 2
            * numpy.log(r_ntc / r_ntc_25) ** 2
        )
        / (
            r_ntc_25
            * r_ntc
            * (r_ntc_betta + numpy.log((r_ntc / r_ntc_25) ** temperatura_25)) ** 2
        )
    )
    end = process_time()
    # print("temperatura Exp std = {}".format(end - start))
    # aproksimacija temperature polinomom 3 reda
    A1 = 3.354016e-3
    B1 = 2.744032e-4
    C1 = 3.666944e-6
    D1 = 1.375492e-7
    start = process_time()
    temperatura_polinom = (
        A1
        + B1 * numpy.log(r_ntc / r_ntc_25)
        + C1 * numpy.log(r_ntc / r_ntc_25) ** 2
        + D1 * numpy.log(r_ntc / r_ntc_25) ** 3
    ) ** -1 - 273.15
    end = process_time()
    # print("temperatura polinom= {}".format(end - start))
    start = process_time()
    temperatura_polinom_std = (
        numpy.sqrt(
            r_ntc_25 ** 2 * r_ntc_std ** 2 + r_ntc ** 2 * uncertanty_r_ntc_25 ** 2
        )
        * numpy.abs(
            B1
            + 3 * D1 * numpy.log(r_ntc / r_ntc_25) ** 2
            + numpy.log((r_ntc / r_ntc_25) ** (2 * C1))
        )
        / (
            r_ntc_25
            * r_ntc
            * (
                A1
                + C1 * numpy.log(r_ntc / r_ntc_25) ** 2
                + D1 * numpy.log(r_ntc / r_ntc_25) ** 3
                + numpy.log((r_ntc / r_ntc_25) ** B1)
            )
            ** 2
        )
    )
    end = process_time()
    # print("temperatura polinom std = {}".format(end - start))
    U_ntc_mean = numpy.mean(kanali[0], dtype=numpy.float64)
    U_ntc_std = numpy.std(kanali[0], dtype=numpy.float64, ddof=1)
    U_shunt_mean = numpy.mean(kanali[1], dtype=numpy.float64)
    U_shunt_std = numpy.std(kanali[1], dtype=numpy.float64, ddof=1)
    U_ntc_m_v, U_ntc_s_v, U_shunt_m_v, U_shunt_s_v = map(
        lambda x: x * 5 / (0x7FFFFF), [U_ntc_mean, U_ntc_std, U_shunt_mean, U_shunt_std]
    )

    end_all = process_time() - start_all

    log = {
        "Timestamp": st,
        # "U_ntc_raw":kanali[0],
        "Napon NTC": U_ntc_mean,
        "Napon std NTC": U_ntc_std,
        "Napon SHUNT": U_shunt_mean,
        "std SHUNT": U_shunt_std,
        "Omjer napona sr. vr.": round(r_mean, 6),
        "std Omjera ntc/shunt": round(r_std,2),
        "Napon NTC [V]": round(U_ntc_m_v,2),
        "std NTC[V]": round(U_ntc_s_v,6),
        "Napon SHUNT[V]": round(U_shunt_m_v,2),
        "std SHUNT [V]": round(U_shunt_s_v,6), 
        # "U_shunt_raw":kanali[1],
        "Otpor": round(r_ntc,2),
        "otpor std NTC": round(r_ntc_std,6),
        "Utjecaj tolerancije shunta": uncertanty_shunt_tolerance,
        "Temperatura izracunata polinomom": round(temperatura_polinom,2),
        "STD Temperature polinomom": round(temperatura_polinom_std,2),
        "Temperatura izracunata exp.": round(temperatura_e,2),
        "STD temperature Exp.": round(temperatura_e_std,6),
        "Vrijeme obrade": end_all,
    }

    return log


def open_config(name):
    with open(name, "r") as f:
        c = safe_load(f)
    return c


if __name__ == "__main__":
    print(obrada(open_config("config.yaml"), [[1, 4], [2, 6]], 10 ** 6))
