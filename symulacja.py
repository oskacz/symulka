# -*-coding: utf-8 -*-
import simpy
import numpy as np
import matplotlib.pyplot as plt
#import xlwt
czestotliwosc_przyjazdu_auta = np.array((30, 50))
czestotliwosc_przyjazdu_ciezarowki = np.array((6, 10))
czas_oblsugi_auta = [3, 5]

ilosc_bramek_aut = [2, 8]
ilosc_bramek_cie = [2, 0]
srednia_kolejka = []


# kodowanie arkusza
#book = xlwt.Workbook(encoding="utf-8")
#sheet1 = book.add_sheet("Raport zbiorczy")


def gen_czasu():  # czestotliwosc przyjazdu
    return np.random.exponential(1. / cz_przy_auta)


def gen_czasu1():  # czestotliwosc przyjazdu ciezarowek
    return np.random.exponential(1. / cz_przy_cie)


def gen_czas_obslugi():  # czas oblsugi osobowych
    return np.random.exponential(1. / cz_obs_aut)


def gen_T_obslugi_tira():  # czas obslugi ciezarowki
    #return np.random.exponential(1. / 100)
    return 0

def kolejka_do_samochodow_osobowych(sro, servers):
    i = 0
    while True:
        i += 1
        yield sro.timeout(gen_czasu())
        sro.process(auto(sro, i, servers))


t_oczekiwania = []  # czas oczekiwania na obsluge


def auto(sro, auto, servers):
    with servers.request() as request:
        t_przyjazd = sro.now
        print sro.now, 'Przyjechało: {} auto '.format(auto)
        yield request
        print sro.now, 'Obsługa {} auta'.format(auto)
        yield sro.timeout(gen_czas_obslugi())
        print sro.now, 'Auto {} odjechało'.format(auto)
        t_odjazd = sro.now
        t_oczekiwania.append(t_odjazd - t_przyjazd)


def kolejka_do_viatol(sro, servers):
    i = 0
    while True:
        i += 1
        yield sro.timeout(gen_czasu1())
        sro.process(ciezarowka(sro, i, servers))


def ciezarowka(sro, ciezarowka, servers):
    with servers.request() as request:
        print sro.now, 'Przyjechala {} ciezarowka'.format(ciezarowka)
        yield request
        # print sro.now, 'Obsluga {} ciezarowki'.format(ciezarowka)
        yield sro.timeout(gen_T_obslugi_tira())
        # print sro.now, 'Ciezarowka {} Odjechala'.format(ciezarowka)


obs_time = []
q_lenght = []


def Obserwacja(env, servers, servers1):
    while True:
        obs_time.append(env.now)
        q_lenght.append(len(servers.queue) + len(servers1.queue))
        yield env.timeout(0.2)


def Obserwacja_bez_ciezarowek(env, servers):
    while True:
        obs_time.append(env.now)
        q_lenght.append(len(servers.queue))
        yield env.timeout(0.2)


# np.random.seed(0)
licznik = 0
for i_bra_cie in ilosc_bramek_cie:
    if i_bra_cie == 0:
        czestotliwosc_przyjazdu_auta = czestotliwosc_przyjazdu_auta + czestotliwosc_przyjazdu_ciezarowki
    for cz_przy_cie in czestotliwosc_przyjazdu_ciezarowki:
        for cz_obs_aut in czas_oblsugi_auta:
            for i_bra_aut in ilosc_bramek_aut:
                for cz_przy_auta in czestotliwosc_przyjazdu_auta:
                    for i in range(3):
                        if i_bra_cie == 0:
                            env = simpy.Environment()
                            servers = simpy.Resource(env, capacity=i_bra_aut)
                            env.process(kolejka_do_samochodow_osobowych(env, servers))
                            env.process(Obserwacja_bez_ciezarowek(env, servers))  # obserwacja procesu
                            # env.process(Obserwacja(env,servers1)) # obeserwacja z cieżarówkami
                            env.run(until=10)
                            """opis = "srednia kolejka:" + str(srednia_kolejka) + "bramki viatol" \
                                   + "bramki zwykle" + str(i_bra_cie) + \
                                   "czesto przy aut: " + str(cz_przy_auta) + \
                                   "czesto przy cie: " + str(cz_przy_cie)"""
                            srednia_kolejka.append(((np.ceil(np.average(q_lenght)))))
                            print srednia_kolejka
                            licznik +=1


                            q_lenght = []
                            # print "srednia kolejka:" + str(srednia_kolejka), "bramki viatol"+"bramki zwykle" + \
                            #     str(i_bra_cie),  "czesto przy aut: " + str(cz_przy_auta), "czesto przy cie: " + \
                            #                                                              str(cz_przy_cie)
                        else:
                            env = simpy.Environment()
                            servers = simpy.Resource(env, capacity=i_bra_aut)
                            env.process(kolejka_do_samochodow_osobowych(env, servers))
                            servers1 = simpy.Resource(env, capacity=i_bra_cie)  # proces viatol
                            env.process(kolejka_do_viatol(env, servers1))
                            env.process(Obserwacja(env, servers, servers1))  # obserwacja procesu
                            # env.process(Obserwacja(env,servers1)) # obeserwacja z cieżarówkami
                            env.run(until=10)
                            """opis = "srednia kolejka:" + str(srednia_kolejka) + "bramki viatol" \
                                   + "bramki zwykle" + str(i_bra_cie) + \
                                   "czesto przy aut: " + str(cz_przy_auta) + \
                                   "czesto przy cie: " + str(cz_przy_cie)"""

                            srednia_kolejka.append((np.ceil(np.average(q_lenght))))
                            print srednia_kolejka
                            q_lenght = []
                            licznik +=1

print len(srednia_kolejka)


#book.save("wynik.xls")
"""
plt.figure(1)
plt.hist(t_oczekiwania)
plt.xlabel('czas obslugi (min)')
plt.ylabel('liczba klientow')
#plt.show(1)

plt.figure(2)
plt.step(obs_time,q_lenght,where = 'post')
plt.xlabel('czas obslugi (min)')
plt.ylabel('dlugosc kolejki')
#plt.show()

plt.figure(3)
from scipy import stats
np.random.seed(12345678)
x = stats.norm.rvs(loc=5, scale=3, size=100)
plt.hist(x)
plt.show()"""