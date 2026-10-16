import argparse
import random

parser = argparse.ArgumentParser(description="Generator grafów w formacie dane.txt")
parser.add_argument("-n", "--wierzcholki", type=int, default=20, help="liczba wierzchołków (domyślnie 20)")
parser.add_argument("-g", "--gestosc", type=float, default=0.3, help="prawdopodobieństwo krawędzi 0-1 (domyślnie 0.3)")
parser.add_argument("-o", "--plik", default="dane_wygenerowane.txt", help="plik wyjściowy")
args = parser.parse_args()

krawedzie = []
for i in range(1, args.wierzcholki + 1):
    for j in range(i + 1, args.wierzcholki + 1):
        if random.random() < args.gestosc:
            krawedzie.append((i, j))

with open(args.plik, "w") as plik:
    plik.write(f"{args.wierzcholki}\n")
    for i, j in krawedzie:
        plik.write(f"{i} {j}\n")

print(f"Zapisano graf: {args.wierzcholki} wierzchołków, {len(krawedzie)} krawędzi -> {args.plik}")
