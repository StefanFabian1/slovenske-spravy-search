# Príklady použitia systému

## Popis datasetu
Systém pracuje s datasetom slovenských spravodajských článkov z rôznych zdrojov:
- Aktuality.sk
- SME.sk (sekcie: hlavné správy, kultúra, šport)
- Denník N
- Pravda.sk
- StartitUp.sk

Celkovo dataset obsahuje 690 článkov. Každý článok obsahuje:
- Jedinečné ID
- Nadpis
- Perex (krátky súhrn)
- Dátum publikácie
- Zdroj
- Kategóriu

## Príklady vyhľadávania

### Príklad 1: Športové správy
**Vstupný text:** "montreal canadiens prehrali"

**Výsledky:**
1. Podobnosť: 63.5%
   - Nadpis: "Montreal prehral s Carolinou, Slafkovský nebodoval"
   - Zdroj: sme.sk
   - Kategória: šport

2. Podobnosť: 58.2%
   - Nadpis: "NHL: Montreal podľahol Carolinu, Slafkovský vyšiel naprázdno"
   - Zdroj: aktuality.sk
   - Kategória: šport

### Príklad 2: Politické správy
**Vstupný text:** "robo fico klame"

**Výsledky:**
1. Podobnosť: 48.8%
   - Nadpis: "Korupcia a organizovaný zločin: Fico čelí novým obvineniam"
   - Zdroj: dennikn.sk
   - Kategória: hlavné správy

2. Podobnosť: 45.3%
   - Nadpis: "Opozícia kritizuje vládne kroky, Fico odmieta obvinenia"
   - Zdroj: pravda.sk
   - Kategória: hlavné správy

## Analýza výsledkov
Systém úspešne nachádza relevantné články na základe sémantickej podobnosti:
1. Dokáže identifikovať súvisiace články aj bez presnej zhody kľúčových slov
2. Berie do úvahy kontext a význam slov
3. Funguje dobre pre rôzne kategórie správ (šport, politika, kultúra)
4. Percentuálna podobnosť pomáha užívateľovi posúdiť relevantnosť výsledkov

## Technické detaily
- Model: lingual-MiniLM-L12-v2 (viacjazyčný model optimalizovaný pre slovenčinu)
- Metrika podobnosti: Kosinusová podobnosť
- Dimenzia vektorov: 384
- Uloženie: Pinecone serverless index 