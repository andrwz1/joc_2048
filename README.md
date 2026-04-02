# 2048 — Documentație proiect

## Prezentare

Implementare Python a jocului 2048, cu efecte vizuale și sonore. Grila standard 4×4, generare pseudo-aleatoare de tile-uri, sistem de scor și gestionare a evenimentelor de joc.


## Caracteristici principale
* Grilă 4×4.  
* Logica standard de deplasare și combinare.  
* Generare de tile-uri noi după fiecare mutare.  
* Scor și high-score.  
* Asset-uri multimedia: imagini, sunete, muzică.  
* Structură simplificată a codului pentru modificări rapide.


## Cerințe
* Python 3.x  
* Dependențe conform implementării (ex. pygame).  
* Fișierele multimedia trebuie păstrate în același director ca executabilul sau scriptul.

## Instalare și rulare
1. Clonezi repository-ul:
```
git clone https://github.com/andrwz1/joc_2048
```
2. Te muți în director:
```
cd joc_2048
```
3. Rulezi jocul:
```
python joc_2048.py
```

## Rulare ca executabil
Dacă ai generat exe-ul:
* Păstrezi executabilul și asset-urile în același director.  
* Rulezi:
```
joc_2048.exe
```

## Mecanică de joc
– Direcții valide: sus / jos / stânga / dreapta.  
– Plăci identice se combină în direcția mutării.  
– Generare tile 2 sau 4 la fiecare mutare validă.  
– Game over când nu mai există mutări posibile.

## Dezvoltare
* Posibilă extindere cu meniuri, efecte, teme.  
* Poți separa logica jocului de interfață pentru întreținere mai ușoară.  
* Poți integra un sistem extern de update pentru exe.

## Debug
* Rulează din terminal pentru vizualizarea erorilor.  
* Verifică încărcarea corectă a resurselor.

## Distribuire
* Menține structura asset-urilor.  
* Pentru PyInstaller: include fișierele media prin argumentul corespunzător.  
* Evită încorporarea resurselor foarte mari în onefile.

## Contribuții
* Pot fi adăugate funcționalități noi, optimizări sau refactorizări.  
* Pull-request-urile trebuie să respecte stilul actual al codului.

## Licență

[MIT](https://choosealicense.com/licenses/mit/)
