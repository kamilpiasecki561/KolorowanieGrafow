import argparse
import time

parser = argparse.ArgumentParser(description="Zachłanne kolorowanie grafu")
parser.add_argument("plik", nargs="?", default="dane.txt", help="plik wejściowy z grafem (domyślnie dane.txt)")
args = parser.parse_args()

lista_par = {}
lista_pokolorwanych = {}
print(f"Czytanie pliku {args.plik}")
with open(args.plik, "r") as plik:
    ilosc = int(plik.readline().strip().split(" ")[0])
    for i in range(1, ilosc+1):
        lista_par[i] = []
        lista_pokolorwanych[i] = 0
    for linia in plik:
        linia = linia.strip().split()
        klucz = int(linia[0])
        wartosc = int(linia[1])
        if wartosc not in lista_par[klucz]:
            lista_par[klucz].append(wartosc)
        if klucz not in lista_par[wartosc]:
            lista_par[wartosc].append(klucz)
start = time.perf_counter()
for i in lista_par.keys():
    if lista_pokolorwanych[i] == 0:
        zajete_kolory = []
        for j in lista_par[i]:
            kolor_sasiada = lista_pokolorwanych[j]
            if kolor_sasiada != 0:
                zajete_kolory.append(kolor_sasiada)
        kolor = 1
        while kolor in zajete_kolory:
            kolor += 1
        lista_pokolorwanych[i] = kolor
czas = (time.perf_counter() - start) * 1000
print("Lista połączeń dla każdego wierzchołka: ")
for klucz, wartosci in lista_par.items():
    print(f"{klucz}: {wartosci}")

print("Lista pokolorowanych wierzchołków (nr wierzchołka: kolor): ")
for klucz, wartosc in lista_pokolorwanych.items():
    print(f"{klucz}: {wartosc}")
print(f"Ilosc kolorow: {max(lista_pokolorwanych.values())}")
print(f"Czas działania algorytmu: {czas:.3f} ms")