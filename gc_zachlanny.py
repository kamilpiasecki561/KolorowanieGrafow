lista_par = {}
lista_pokolorwanych = {}

with open("dane.txt", "r") as plik:
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

print("Lista połączeń dla każdego wierzchołka: ")
for klucz, wartosci in lista_par.items():
    print(f"{klucz}: {wartosci}")

print("Lista pokolorowanych wierzchołków (nr wierzchołka: kolor): ")
for klucz, wartosc in lista_pokolorwanych.items():
    print(f"{klucz}: {wartosc}")
    