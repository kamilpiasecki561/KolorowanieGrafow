import argparse
import heapq
import random
import time

parser = argparse.ArgumentParser(description="Kolorowanie grafu metodą tabu search (TabuCol)")
parser.add_argument("plik", nargs="?", default="dane.txt", help="plik wejściowy z grafem (domyślnie dane.txt)")
parser.add_argument("--iteracje", type=int, default=10000, help="maksymalna liczba iteracji (domyślnie 10000)")
parser.add_argument("--tabu", type=int, default=None,
                    help="stała długość tabu; domyślnie dynamiczna: losowa(0..9) + 0.6 * liczba wierzchołków w konflikcie")
parser.add_argument("--czas", type=float, default=None, help="limit czasu w sekundach (domyślnie brak)")
args = parser.parse_args()


# cały program w funkcji: zmienne lokalne są w Pythonie dużo szybsze od globalnych
def main():
    print(f"Czytanie pliku {args.plik}")
    with open(args.plik, "r") as plik:
        ilosc = int(plik.readline().split()[0])
        zbiory = [set() for _ in range(ilosc+1)]  # set: sprawdzanie duplikatów w O(1)
        for linia in plik:
            czesci = linia.split()
            if len(czesci) < 2:
                continue
            a, b = int(czesci[0]), int(czesci[1])
            if a != b:
                zbiory[a].add(b)
                zbiory[b].add(a)
    sasiedzi = [list(s) for s in zbiory]  # wierzchołki 1..ilosc, indeks 0 nieużywany
    del zbiory


    def konflikty(kolory):
        # liczba krawędzi, których oba końce mają ten sam kolor
        return sum(1 for v in range(1, ilosc+1) for u in sasiedzi[v] if u > v and kolory[u] == kolory[v])


    start = time.perf_counter()
    koniec_czasu = start + args.czas if args.czas else float("inf")

    # Rozwiązanie startowe: DSatur - koloruj wierzchołek z największą liczbą różnych kolorów u sąsiadów
    kolory = [0] * (ilosc+1)
    nasycenie = [set() for _ in range(ilosc+1)]
    kopiec = [(0, -len(sasiedzi[v]), v) for v in range(1, ilosc+1)]
    heapq.heapify(kopiec)
    while kopiec:
        _, _, v = heapq.heappop(kopiec)
        if kolory[v]:
            continue  # nieaktualny wpis w kopcu
        kolor = 1
        while kolor in nasycenie[v]:
            kolor += 1
        kolory[v] = kolor
        for u in sasiedzi[v]:
            if not kolory[u] and kolor not in nasycenie[u]:
                nasycenie[u].add(kolor)
                heapq.heappush(kopiec, (-len(nasycenie[u]), -len(sasiedzi[u]), u))
    del nasycenie, kopiec

    k = max(kolory)
    najlepsze = kolory[:]

    # ile[v][c] = ilu sąsiadów wierzchołka v ma kolor c
    # dzięki temu zmianę liczby konfliktów po ruchu znamy od razu, bez przeliczania całego grafu
    ile = [[0] * (k+1) for _ in range(ilosc+1)]
    for v in range(1, ilosc+1):
        for u in sasiedzi[v]:
            ile[u][kolory[v]] += 1
    konf = konflikty(kolory)
    konfliktowe = set()  # wierzchołki, które mają sąsiada w tym samym kolorze
    tabu = [[-1] * (k+1) for _ in range(ilosc+1)]  # tabu[v][c] = do której iteracji v nie może wrócić do koloru c


    def zmien_kolor(v, c):
        stary = kolory[v]
        for u in sasiedzi[v]:
            iu = ile[u]
            iu[stary] -= 1
            iu[c] += 1
            if kolory[u] == stary and iu[stary] == 0:
                konfliktowe.discard(u)
            elif kolory[u] == c:
                konfliktowe.add(u)
        kolory[v] = c
        if ile[v][c]:
            konfliktowe.add(v)
        else:
            konfliktowe.discard(v)


    it = 0
    while it < args.iteracje and time.perf_counter() < koniec_czasu:
        if konf == 0:
            # znaleziono poprawne kolorowanie - zapamiętaj i spróbuj o jeden kolor mniej
            najlepsze = kolory[:]
            k = max(kolory) - 1
            if k < 2:
                break  # graf z krawędziami nie da się pokolorować jednym kolorem
            # wierzchołki z usuniętego koloru dostają kolor z najmniejszą liczbą konfliktów
            for v in range(1, ilosc+1):
                if kolory[v] > k:
                    iv = ile[v]
                    zmien_kolor(v, min(range(1, k+1), key=iv.__getitem__))
            konf = sum(ile[v][kolory[v]] for v in range(1, ilosc+1)) // 2  # O(n) zamiast przeglądania krawędzi
            tabu = [[-1] * (k+1) for _ in range(ilosc+1)]
            it += 1
            continue

        # przeglądamy sąsiedztwo: zmiana koloru jednego wierzchołka będącego w konflikcie
        najlepsza = float("inf")
        ruchy = []
        najlepsza_tabu = float("inf")
        ruch_tabu = None
        for v in konfliktowe:
            iv = ile[v]
            kv = kolory[v]
            teraz = iv[kv]
            if teraz < -najlepsza:
                continue  # nawet kolor bez sąsiadów nie da lepszego ruchu niż już znaleziony
            reszta = iv[1:kv] + iv[kv+1:k+1]
            m = min(reszta)  # wbudowane min() działa w C - dużo szybciej niż pętla po kolorach
            delta = m - teraz
            if delta > najlepsza:
                continue
            tv = tabu[v]
            aspiracja = konf + delta == 0
            wolne = []
            c = 0
            for _ in range(reszta.count(m)):  # kolory z minimalną liczbą sąsiadów, szukane przez index() w C
                c = iv.index(m, c+1, k+1)
                if c == kv:
                    c = iv.index(m, c+1, k+1)
                if tv[c] < it or aspiracja:
                    wolne.append(c)
            if wolne:
                if delta < najlepsza:
                    najlepsza = delta
                    ruchy = [(v, c) for c in wolne]
                else:
                    ruchy.extend((v, c) for c in wolne)
                continue
            # wszystkie najlepsze kolory v są tabu - pełny przegląd kolorów tego wierzchołka
            for c in range(1, k+1):
                if c == kv:
                    continue
                delta = iv[c] - teraz
                # ruch tabu jest dozwolony tylko gdy daje poprawne kolorowanie (kryterium aspiracji)
                if tv[c] >= it and konf + delta != 0:
                    if delta < najlepsza_tabu:
                        najlepsza_tabu = delta
                        ruch_tabu = (v, c)
                    continue
                if delta < najlepsza:
                    najlepsza = delta
                    ruchy = [(v, c)]
                elif delta == najlepsza:
                    ruchy.append((v, c))

        if not ruchy:
            # wszystkie ruchy zakazane - wykonaj najlepszy z nich zamiast marnować iterację
            ruchy = [ruch_tabu]
            najlepsza = najlepsza_tabu
        v, c = random.choice(ruchy)  # losowy wybór przy remisie zapobiega zapętleniu
        dlugosc = args.tabu if args.tabu is not None else random.randint(0, 9) + int(0.6 * len(konfliktowe))
        tabu[v][kolory[v]] = it + dlugosc
        konf += najlepsza
        zmien_kolor(v, c)
        it += 1

    if konf == 0:
        najlepsze = kolory[:]  # poprawne kolorowanie znalezione w ostatniej iteracji

    czas = (time.perf_counter() - start) * 1000

    assert konflikty(najlepsze) == 0, "kolorowanie niepoprawne"
    print("Lista pokolorowanych wierzchołków (nr wierzchołka: kolor): ")
    for v in range(1, ilosc+1):
        print(f"{v}: {najlepsze[v]}")
    print(f"Ilosc kolorow: {max(najlepsze)}")
    print(f"Iteracje: {it}")
    print(f"Czas działania algorytmu: {czas:.3f} ms")


main()
