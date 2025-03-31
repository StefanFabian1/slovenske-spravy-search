# 🔍 Slovenské Spravodajské Vyhľadávanie

Sémantické vyhľadávanie v slovenských spravodajských článkoch pomocou AI a vektorovej databázy.

## 📋 Popis projektu

Tento projekt implementuje systém pre sémantické vyhľadávanie v slovenských spravodajských článkoch. Využíva moderné AI technológie na vytvorenie vektorových reprezentácií textov a umožňuje vyhľadávať články na základe významovej podobnosti.

### 🌟 Hlavné funkcie

- Automatické sťahovanie článkov z RSS feedov slovenských médií
- Vektorová reprezentácia textov pomocou jazykového modelu
- Ukladanie do Pinecone vektorovej databázy
- Interaktívne vyhľadávanie pomocou kosinusovej podobnosti
- Podpora viacerých spravodajských zdrojov

## 🛠️ Technológie

- Python 3.8+
- Sentence Transformers (paraphrase-multilingual-MiniLM-L12-v2)
- Pinecone vektorová databáza
- feedparser pre spracovanie RSS
- BeautifulSoup4 pre parsovanie HTML

## 📦 Inštalácia

1. Klonujte repozitár:
```bash
git clone https://github.com/your-username/slovenske-spravy.git
cd slovenske-spravy
```

2. Nainštalujte závislosti:
```bash
pip install -r requirements.txt
```

3. Vytvorte `.env` súbor s nasledujúcimi premennými:
```env
PINECONE_API_KEY=your_api_key
PINECONE_ENV=your_environment
PINECONE_HOST=your_host
```

## 🚀 Použitie

Spustite hlavný skript:
```bash
python news_search.py
```

### Príklad vyhľadávania:

```
Zadajte text, ku ktorému chcete nájsť podobné správy:
montreal canadiens prehrali

Nájdených 5 podobných správ:

1. Správa (Podobnosť: 63.5%):
Nadpis: NHL: Montreal prehral s Carolinou...
```

## 🔧 Štruktúra projektu

```
├── news_search.py     # Hlavný skript
├── requirements.txt   # Python závislosti
├── .env              # Konfiguračné premenné
└── README.md         # Dokumentácia
```

## 📚 Dokumentácia kódu

### Hlavné komponenty

#### 1. Sťahovanie správ
```python
def stiahni_spravy_z_rss(url):
    """
    Stiahne správy z RSS feedu a spracuje ich do štandardného formátu.
    
    Args:
        url (str): URL adresa RSS feedu
        
    Returns:
        list: Zoznam správ v štandardizovanom formáte
    """
```

#### 2. Spracovanie textu
```python
def vytvor_embedding(text, model):
    """
    Vytvorí vektorovú reprezentáciu textu.
    
    Args:
        text (str): Vstupný text
        model: Natrénovaný jazykový model
        
    Returns:
        numpy.ndarray: Vektorová reprezentácia textu
    """
```

#### 3. Vyhľadávanie
```python
def vyhladaj_podobne_spravy(text, model, index, pocet=5):
    """
    Vyhľadá podobné správy pomocou kosinusovej podobnosti.
    
    Args:
        text (str): Vyhľadávaný text
        model: Jazykový model pre embeddings
        index: Pinecone index
        pocet (int): Počet výsledkov na vrátenie
        
    Returns:
        list: Zoznam najpodobnejších správ
    """
```

## 📊 Podporované zdroje

- Aktuality.sk
- SME.sk
- Pravda.sk
- HNonline.sk
- Denník N
- Refresher.sk
- StartitUp

## 🤝 Prispievanie

Príspevky sú vítané! Prosím, vytvorte issue alebo pull request.

## 📝 Licencia

MIT License

## 👥 Autori

- Váš meno - Hlavný vývojár

## 🙏 Poďakovanie

- Sentence Transformers tím za poskytnutie modelu
- Pinecone za vektorovú databázu
- Všetkým prispievateľom open-source knižníc 