"""
Slovenské Spravodajské Vyhľadávanie

Tento modul implementuje systém pre sémantické vyhľadávanie v slovenských spravodajských
článkoch pomocou vektorovej databázy Pinecone a jazykového modelu Sentence Transformers.

Hlavné funkcie:
- Sťahovanie správ z RSS feedov slovenských médií
- Vytvorenie vektorových reprezentácií textov
- Ukladanie do Pinecone vektorovej databázy
- Interaktívne vyhľadávanie pomocou kosinusovej podobnosti

Autor: Váš meno
Dátum: Marec 2025
"""

import os
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from dotenv import load_dotenv
import feedparser
import html
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib
import logging
import sys
import time
from typing import List, Dict, Any

# Konfigurácia logovania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def stiahni_spravy_z_rss(url: str) -> List[Dict[str, Any]]:
    """
    Stiahne a spracuje správy z RSS feedu.
    
    Args:
        url (str): URL adresa RSS feedu
        
    Returns:
        List[Dict[str, Any]]: Zoznam správ v štandardizovanom formáte
        
    Raises:
        Exception: Ak sa nepodarí stiahnuť alebo spracovať RSS feed
    """
    try:
        feed = feedparser.parse(url)
        spravy = []
        
        # Získanie názvu zdroja z URL
        zdroj = url.split('/')[2]
        
        for entry in feed.entries:
            nadpis = html.unescape(entry.title)
            perex = ""
            if hasattr(entry, 'description'):
                perex = html.unescape(BeautifulSoup(entry.description, 'html.parser').get_text())
            
            # Pridanie zdroja do ID aby sa správy neprepisovali
            id = hashlib.md5(f"{zdroj}:{nadpis}".encode()).hexdigest()
            
            datum = datetime.now().isoformat()
            if hasattr(entry, 'published_parsed'):
                datum = datetime(*entry.published_parsed[:6]).isoformat()
            
            # Pridanie kategórie z URL ak existuje
            kategoria = "hlavné"
            if '/rss/' in url:
                kategoria = url.split('/rss/')[-1].strip('/')
            
            sprava = {
                'id': id,
                'nadpis': nadpis,
                'perex': perex,
                'text': f"{nadpis}\n\n{perex}",
                'datum': datum,
                'zdroj': zdroj,
                'kategoria': kategoria
            }
            spravy.append(sprava)
        
        logger.info(f"Stiahnutých {len(spravy)} správ z RSS feedu {url}")
        return spravy
    except Exception as e:
        logger.error(f"Chyba pri sťahovaní správ z RSS feedu {url}: {str(e)}")
        raise

def vloz_spravy_do_indexu(spravy: List[Dict[str, Any]], model: SentenceTransformer, index: pinecone.Index) -> None:
    """
    Vloží správy do Pinecone indexu.
    
    Args:
        spravy (List[Dict[str, Any]]): Zoznam správ na vloženie
        model (SentenceTransformer): Model pre vytvorenie embeddings
        index (pinecone.Index): Pinecone index
        
    Returns:
        None
    """
    try:
        if not spravy:
            logger.warning("Žiadne správy na vloženie do indexu")
            return
            
        vectors = []
        for sprava in spravy:
            embedding = model.encode(sprava['text'])
            vector = {
                'id': sprava['id'],
                'values': embedding.tolist(),
                'metadata': {
                    'nadpis': sprava['nadpis'],
                    'perex': sprava['perex'],
                    'datum': sprava['datum'],
                    'zdroj': sprava['zdroj'],
                    'kategoria': sprava['kategoria']
                }
            }
            vectors.append(vector)
        
        # Vkladáme po 100 správach aby sme nepresiahli limity API
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            index.upsert(vectors=batch)
            logger.info(f"Vložená dávka {i//batch_size + 1} z {(len(vectors)-1)//batch_size + 1}")
        
        logger.info(f"Úspešne vložených {len(vectors)} správ do indexu")
        
    except Exception as e:
        logger.error(f"Chyba pri vkladaní správ do indexu: {str(e)}")
        raise

def vyhladaj_podobne_spravy(text: str, model: SentenceTransformer, index: pinecone.Index, pocet: int = 5) -> List[Dict[str, Any]]:
    """
    Vyhľadá podobné správy pomocou kosinusovej podobnosti.
    
    Args:
        text (str): Text na vyhľadávanie
        model (SentenceTransformer): Model pre vytvorenie query embeddings
        index (pinecone.Index): Pinecone index
        pocet (int, optional): Počet výsledkov. Predvolené na 5.
        
    Returns:
        List[Dict[str, Any]]: Zoznam najpodobnejších správ
    """
    try:
        # Vytvoríme embedding pre vyhľadávaný text
        print(f"\nVytváranie vektorovej reprezentácie pre text: '{text}'")
        query_embedding = model.encode(text)
        
        # Vyhľadáme podobné vektory pomocou kosinusovej podobnosti
        print("Vyhľadávam najpodobnejšie správy...")
        results = index.query(
            vector=query_embedding.tolist(),
            top_k=pocet,
            include_metadata=True
        )
        
        # Vypíšeme informácie o podobnosti
        print(f"\nNájdených {len(results['matches'])} podobných správ:")
        for i, match in enumerate(results['matches'], 1):
            podobnost_percenta = match['score'] * 100  # Prevod na percentá (0-100%)
            metadata = match.get('metadata', {})
            
            print(f"\n{i}. Správa (Podobnosť: {podobnost_percenta:.1f}%):")
            print(f"Nadpis: {metadata.get('nadpis', 'Neznámy nadpis')}")
            
            # Vypíšeme ďalšie metadáta len ak existujú
            if 'zdroj' in metadata:
                print(f"Zdroj: {metadata['zdroj']}")
            if 'kategoria' in metadata:
                print(f"Kategória: {metadata['kategoria']}")
            if 'perex' in metadata:
                print(f"Perex: {metadata['perex']}")
            if 'datum' in metadata:
                print(f"Dátum: {metadata['datum']}")
        
        return results
    except Exception as e:
        logger.error(f"Chyba pri vyhľadávaní správ: {str(e)}")
        raise

def interaktivne_vyhladavanie(model, index):
    """Interaktívne vyhľadávanie podobných správ."""
    try:
        print("\nVítajte vo vyhľadávaní podobných správ!")
        print("Pre každý dotaz nájdem najrelevantnejšie správy pomocou kosinusovej podobnosti.")
        print("Napíšte text a ja nájdem správy, ktoré sú mu obsahovo najpodobnejšie.")
        print("Pre ukončenie napíšte 'koniec'")
        
        while True:
            # Získame dotaz od používateľa
            print("\nZadajte text, ku ktorému chcete nájsť podobné správy:")
            query = input().strip()
            
            # Kontrola ukončenia
            if query.lower() in ['koniec', 'quit', 'exit', 'q']:
                print("\nĎakujem za použitie vyhľadávania. Dovidenia!")
                break
            
            if not query:
                print("Prázdny dotaz, skúste znova.")
                continue
            
            # Vyhľadáme podobné správy
            vyhladaj_podobne_spravy(query, model, index)
            
    except KeyboardInterrupt:
        print("\nVyhľadávanie prerušené používateľom.")
    except Exception as e:
        logger.error(f"Chyba pri interaktívnom vyhľadávaní: {str(e)}")
        raise

def main():
    """
    Hlavná funkcia programu.
    
    Vykoná nasledujúce kroky:
    1. Inicializuje pripojenie k Pinecone
    2. Načíta jazykový model
    3. Stiahne správy z RSS feedov
    4. Vloží správy do indexu
    5. Spustí interaktívne vyhľadávanie
    """
    try:
        print("\n=== Spúšťam program na vyhľadávanie správ ===\n")
        
        # Načítanie premenných prostredia
        print("Načítavam premenné prostredia...")
        load_dotenv()
        api_key = os.getenv('PINECONE_API_KEY')
        
        print(f"PINECONE_API_KEY: {'nastavený' if api_key else 'chýba'}")
        
        if not api_key:
            raise ValueError("Chýbajú potrebné premenné prostredia")
        
        # Inicializácia Pinecone
        print("\nInicializujem Pinecone...")
        try:
            pc = Pinecone(api_key=api_key)
            print("Pinecone úspešne inicializovaný")
        except Exception as e:
            logger.error(f"Chyba pri inicializácii Pinecone: {str(e)}")
            raise
        
        # Načítanie modelu
        print("\nNačítavam model pre spracovanie textu...")
        model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        print("Model úspešne načítaný")
        
        # Kontrola a vytvorenie indexu ak neexistuje
        index_name = "slovenske-spravy"
        print(f"\nKontrolujem existenciu indexu '{index_name}'...")
        
        if index_name not in pc.list_indexes().names():
            print(f"Index '{index_name}' neexistuje, vytváram nový...")
            pc.create_index(
                name=index_name,
                dimension=384,
                metric="cosine",
                spec={
                    "serverless": {
                        "cloud": "aws",
                        "region": "us-east-1"
                    }
                }
            )
            print("Index úspešne vytvorený")
            # Počkáme kým bude index pripravený
            print("Čakám na inicializáciu indexu...")
            time.sleep(10)
        else:
            print("Index už existuje")
        
        # Pripojenie k indexu
        print(f"\nPripájam sa k indexu '{index_name}'...")
        index = pc.Index(index_name)
        print("Index úspešne pripojený")
        
        # Kontrola počtu záznamov v indexe
        stats = index.describe_index_stats()
        pocet_zaznamov = stats.total_vector_count
        print(f"\nPočet záznamov v indexe: {pocet_zaznamov}")
        
        if pocet_zaznamov < 250:
            print("\nIndex obsahuje menej ako 250 záznamov, sťahujem nové správy...")
            
            # Zoznam RSS feedov s viacerými kategóriami
            rss_feeds = [
                # Aktuality.sk
                "https://www.aktuality.sk/rss",
                "https://www.aktuality.sk/rss/domace",
                "https://www.aktuality.sk/rss/zahranicne",
                "https://www.aktuality.sk/rss/ekonomika",
                "https://www.aktuality.sk/rss/sport",
                "https://www.aktuality.sk/rss/veda",
                "https://www.aktuality.sk/rss/auto",
                "https://www.aktuality.sk/rss/kultura",
                
                # SME.sk
                "https://rss.sme.sk/rss/rss.asp",
                "https://domov.sme.sk/rss",
                "https://svet.sme.sk/rss",
                "https://ekonomika.sme.sk/rss",
                "https://sport.sme.sk/rss",
                "https://tech.sme.sk/rss",
                "https://auto.sme.sk/rss",
                "https://kultura.sme.sk/rss",
                
                # Pravda.sk
                "https://feeds.feedburner.com/Pravda",
                "https://spravy.pravda.sk/domace/rss",
                "https://spravy.pravda.sk/svet/rss",
                "https://ekonomika.pravda.sk/rss",
                "https://sport.pravda.sk/rss",
                "https://vat.pravda.sk/rss",
                "https://style.pravda.sk/rss",
                
                # HNonline.sk
                "https://finweb.hnonline.sk/rss",
                "https://slovensko.hnonline.sk/rss",
                "https://zahranicne.hnonline.sk/rss",
                "https://sport.hnonline.sk/rss",
                "https://style.hnonline.sk/rss",
                
                # Denník N
                "https://dennikn.sk/feed/",
                "https://dennikn.sk/slovensko/feed/",
                "https://dennikn.sk/svet/feed/",
                "https://dennikn.sk/ekonomika/feed/",
                "https://dennikn.sk/sport/feed/",
                "https://dennikn.sk/veda/feed/",
                
                # Refresher.sk
                "https://refresher.sk/rss",
                "https://refresher.sk/rss/spravy",
                "https://refresher.sk/rss/tech",
                "https://refresher.sk/rss/kultura",
                
                # StartitUp
                "https://www.startitup.sk/feed/",
                "https://www.startitup.sk/category/tech/feed/",
                "https://www.startitup.sk/category/biznis/feed/"
            ]
            
            # Stiahnutie správ zo všetkých zdrojov
            print("\nSťahujem správy z RSS feedov...")
            vsetky_spravy = []
            
            for url in rss_feeds:
                try:
                    print(f"\nSťahujem správy z {url}...")
                    spravy = stiahni_spravy_z_rss(url)
                    if spravy:
                        vsetky_spravy.extend(spravy)
                        print(f"Úspešne stiahnutých {len(spravy)} správ z {url}")
                    else:
                        print(f"Žiadne správy neboli stiahnuté z {url}")
                except Exception as e:
                    print(f"Chyba pri sťahovaní správ z {url}: {str(e)}")
                    continue
            
            if vsetky_spravy:
                print(f"\nCelkovo stiahnutých {len(vsetky_spravy)} správ")
                print(f"Vkladám správy do indexu...")
                vloz_spravy_do_indexu(vsetky_spravy, model, index)
                print("Správy úspešne vložené do indexu")
                
                # Spustíme interaktívne vyhľadávanie
                print("\nSpúšťam interaktívne vyhľadávanie...")
                interaktivne_vyhladavanie(model, index)
            else:
                print("\nNeboli nájdené žiadne správy")
        
        print("\n=== Program úspešne dokončený ===\n")
        
    except Exception as e:
        print(f"\nChyba: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 