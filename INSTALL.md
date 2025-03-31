# Inštalačný návod

## Požiadavky
- Python 3.8 alebo novší
- Pinecone účet (zaregistrujte sa na https://www.pinecone.io/)
- Dostatočný priestor na disku (aspoň 500MB pre model a cache)

## Kroky inštalácie

1. Naklonujte repozitár:
```bash
git clone https://github.com/vase-meno/slovenske-spravy-search.git
cd slovenske-spravy-search
```

2. Vytvorte a aktivujte virtuálne prostredie:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. Nainštalujte závislosti:
```bash
pip install -r requirements.txt
```

4. Vytvorte súbor `.env` v koreňovom adresári projektu s nasledujúcim obsahom:
```
PINECONE_API_KEY=vas_api_kluc
```
Nahraďte `vas_api_kluc` skutočným API kľúčom z vášho Pinecone účtu.

## Spustenie programu

1. Aktivujte virtuálne prostredie (ak ešte nie je aktivované):
```bash
# Windows
.\venv\Scripts\activate

# Linux/MacOS
source venv/bin/activate
```

2. Spustite hlavný program:
```bash
python news_search.py
```

Pri prvom spustení program:
1. Stiahne jazykový model (približne 400MB)
2. Vytvorí Pinecone index
3. Stiahne a spracuje články
4. Spustí interaktívne vyhľadávanie

## Riešenie problémov

### Chyba pri pripojení k Pinecone
- Skontrolujte, či je API kľúč správne nastavený v `.env` súbore
- Overte, či máte prístup na internet
- Skontrolujte, či váš Pinecone účet je aktívny

### Chyba pri sťahovaní modelu
- Skontrolujte pripojenie na internet
- Overte, či máte dostatok miesta na disku
- Skúste vymazať cache: `rm -rf ~/.cache/torch/sentence_transformers`

### Iné problémy
- Skontrolujte verzie závislostí v `requirements.txt`
- Vyskúšajte vytvoriť nové virtuálne prostredie
- Pozrite si logy v konzole pre detailnejšie informácie o chybe 