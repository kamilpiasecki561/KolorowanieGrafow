import argparse
import random
import time

parser = argparse.ArgumentParser(description="Kolorowanie grafu metodą tabu search")
parser.add_argument("plik", nargs="?", default="dane.txt", help="plik wejściowy z grafem (domyślnie dane.txt)")
parser.add_argument("--iteracje", type=int, default=10000, help="maksymalna liczba iteracji (domyślnie 10000)")
parser.add_argument("--tabu", type=int, default=7, help="ile iteracji ruch pozostaje zakazany (domyślnie 7)")
args = parser.parse_args()

lista_par = {}
print(f"Czytanie pliku {args.plik}")
with open(args.plik, "r") as plik:
    ilosc = int(plik.readline().strip().split(" ")[0])
    for i in range(1, ilosc+1):
        lista_par[i] = []
    for linia in plik:
        linia = linia.strip().split()
        klucz = int(linia[0])
        wartosc = int(linia[1])
        if wartosc not in lista_par[klucz]:
            lista_par[klucz].append(wartosc)
        if klucz not in lista_par[wartosc]:
            lista_par[wartosc].append(klucz)


def konflikty(kolory):
    # liczba krawędzi, których oba końce mają ten sam kolor
    return sum(1 for v in lista_par for u in lista_par[v] if u > v and kolory[u] == kolory[v])


start = time.perf_counter()

# Rozwiązanie startowe wyznaczone algorytmem zachłannym
kolory = {v: 0 for v in lista_par}
for i in lista_par:
    zajete_kolory = set()
    for j in lista_par[i]:
        kolor_sasiada = kolory[j]
        if kolor_sasiada != 0:
            zajete_kolory.add(kolor_sasiada)
    kolor = 1
    while kolor in zajete_kolory:
        kolor += 1
    kolory[i] = kolor

k = max(kolory.values())
najlepsze = dict(kolory)
tabu = {}  # (wierzchołek, kolor) -> numer iteracji, do której nie wolno wrócić do tego koloru

# ile[v][c] = ilu sąsiadów wierzchołka v ma kolor c
# dzięki temu zmianę liczby konfliktów po ruchu znamy od razu, bez przeliczania całego grafu
ile = [[0] * (k+1) for _ in range(ilosc+1)]
for v in lista_par:
    for u in lista_par[v]:
        ile[u][kolory[v]] += 1
konf = konflikty(kolory)


def zmien_kolor(v, c):
    stary = kolory[v]
    for u in lista_par[v]:
        ile[u][stary] -= 1
        ile[u][c] += 1
    kolory[v] = c


for it in range(args.iteracje):
    if konf == 0:
        # znaleziono poprawne kolorowanie - zapamiętaj i spróbuj o jeden kolor mniej
        najlepsze = dict(kolory)
        k = max(kolory.values()) - 1
        if k == 0:
            break
        for v in kolory:
            if kolory[v] > k:
                zmien_kolor(v, random.randint(1, k))
        konf = konflikty(kolory)
        tabu = {}
        continue

    # przeglądamy sąsiedztwo: zmiana koloru jednego wierzchołka będącego w konflikcie
    najlepszy_ruch = None
    najlepsza_wartosc = float("inf")
    for v in kolory:
        teraz = ile[v][kolory[v]]  # ilu sąsiadów ma ten sam kolor co v
        if teraz == 0:
            continue
        for c in range(1, k+1):
            if c == kolory[v]:
                continue
            nowa = konf + ile[v][c] - teraz
            # ruch tabu jest dozwolony tylko gdy daje poprawne kolorowanie (kryterium aspiracji)
            if tabu.get((v, c), -1) >= it and nowa != 0:
                continue
            if nowa < najlepsza_wartosc:
                najlepsza_wartosc = nowa
                najlepszy_ruch = (v, c)

    if najlepszy_ruch is None:
        continue
    v, c = najlepszy_ruch
    tabu[(v, kolory[v])] = it + args.tabu
    konf = najlepsza_wartosc
    zmien_kolor(v, c)

czas = (time.perf_counter() - start) * 1000

if najlepsze is None:
    print("Nie znaleziono poprawnego kolorowania - zwiększ liczbę iteracji (--iteracje)")
else:
    assert konflikty(najlepsze) == 0, "kolorowanie niepoprawne"
    print("Lista pokolorowanych wierzchołków (nr wierzchołka: kolor): ")
    for klucz, wartosc in najlepsze.items():
        print(f"{klucz}: {wartosc}")
    print(f"Ilosc kolorow: {max(najlepsze.values())}")
print(f"Czas działania algorytmu: {czas:.3f} ms")