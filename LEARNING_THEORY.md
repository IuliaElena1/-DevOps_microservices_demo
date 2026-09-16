# DevOps — Teorie

## Ce este Docker?

Docker este o platformă open-source pentru dezvoltarea, transportul și rularea aplicațiilor.
 Docker îți permite să separi aplicațiile de infrastructură , astfel încât să poți livra
 software rapid. Cu Docker, poți gestiona infrastructura exact cum gestionezi aplicațiile.

Folosind metodologiile Docker pentru livrare, testare și deployment, poți reduce semnificativ
 intervalul de timp dintre scrierea codului și rularea lui în producție.

### Platforma Docker

Docker oferă posibilitatea de a împacheta și rula o aplicație într-un mediu izolat numit
 container . Izolarea și securitatea îți permit să rulezi mai multe containere
 simultan pe același host. Containerele sunt ușoare și conțin tot ce este necesar pentru a rula
 aplicația — nu depinzi de ce este instalat pe host.

Docker oferă unelte și o platformă pentru gestionarea ciclului de viață al containerelor tale:
- 1 
 Dezvolți aplicația și componentele ei folosind containere.
- 2 
 Containerul devine unitatea pentru distribuirea și testarea aplicației.
- 3 
 Când ești gata, faci deployment în producție — fie ca un container simplu, fie ca un serviciu orchestrat. Funcționează la fel indiferent dacă producția e un data center local, un cloud provider sau o combinație a celor două.

---

## La ce folosești Docker?

Dezvoltatorii lucrează în medii standardizate cu containere locale. Ideal pentru fluxuri CI/CD.

Containerele rulează pe laptopuri, VM-uri, data centere, cloud sau medii hibride.

Docker e ușor și rapid. Alternativă cost-eficientă față de VM-urile bazate pe hypervisor.

#### Livrare rapidă și consistentă

#### Deployment și scalare flexibile

#### Mai mult pe același hardware

---

## Arhitectura Docker

Docker folosește o arhitectură client-server . Docker Client comunică cu
 Docker Daemon, care face munca grea de build, rulare și distribuire a containerelor.
 Clientul și daemon-ul pot rula pe același sistem sau clientul se poate conecta la un daemon remote.
 Comunicarea se face prin REST API , peste socket-uri UNIX sau o interfață de rețea.

Comenzi: run, build, pull, push…

Canal de comunicare

Gestionează imagini, containere, rețele, volume

### Docker Daemon (dockerd)

Daemon-ul ascultă cererile Docker API și gestionează obiectele Docker: imagini, containere,
 rețele și volume. Un daemon poate comunica și cu alți daemon-i pentru a gestiona servicii Docker.

### Docker Client

Clientul Docker ( docker ) este modul principal prin care utilizatorii interacționează
 cu Docker. Când rulezi comenzi precum docker run , clientul trimite aceste comenzi
 către dockerd , care le execută. Clientul Docker poate comunica cu mai mult de un daemon.

### Docker Desktop

Docker Desktop este o aplicație ușor de instalat pentru Mac, Windows sau Linux care îți permite
 să construiești și să distribui aplicații și microservicii containerizate. Include: daemon-ul Docker,
 clientul Docker, Docker Compose, Docker Content Trust, Kubernetes și Credential Helper.

---

## Docker Registry

Un Docker Registry (cum ar fi Docker Hub, GitHub Packages sau un registry privat) are rolul
 principal de stocare, organizare și distribuție a imaginilor Docker .

Un registry stochează imagini Docker. Docker Hub este un registry public pe care
 oricine îl poate folosi — Docker caută imagini acolo implicit. Poți să-ți rulezi și propriul registry privat.

### Rolurile Registry-ului în fluxul complet

Dacă privim fluxul exact din momentul în care ai creat o imagine local (prin docker build )
 și până când rulează într-un container pe un server, registry-ul îndeplinește mai multe funcții cheie:

Prin docker push , imaginea construită local este stocată centralizat.
 Astfel, nu se pierde (e independentă de dispozitivul tău) și devine accesibilă
 oricărui server de producție sau sistem CI/CD.

Verifică permisiunile înainte să permită descărcarea. Poate fi
 privat (doar echipa ta) sau public (open-source, ca Docker Hub).

Registry-urile moderne scanează imaginea după upload pentru vulnerabilități de securitate,
 pachete învechite sau probleme critice — înainte ca imaginea să fie pusă în producție.

Serverul sau platforma de orchestrare (ex. Kubernetes) descarcă imaginea prin
 docker pull și o pornește ca aplicație funcțională (container).

În rezumat: Registry-ul este „biblioteca" sau „magazia" centrală.
 El face legătura dintre momentul în care dezvoltatorul a terminat de construit codul local
 și momentul în care acel cod este pornit efectiv ca aplicație funcțională (container) pe un server extern.

#### Punct de tranzit centralizat

#### Controlul versiunilor

#### Securitate și autentificare

#### Scanare și validare

#### Sursă pentru crearea containerului
- Organizează imagini cu tag-uri: v1.0 , v2.0 , latest
- Garantează că producția descarcă exact versiunea necesară
- Previne neconcordanțele între medii

---

## Obiecte Docker

Când folosești Docker, creezi și utilizezi imagini, containere, rețele, volume, plugin-uri și alte obiecte.

### Imagini

O imagine este un șablon read-only cu instrucțiuni pentru crearea unui container Docker.
 De obicei, o imagine se bazează pe altă imagine, cu personalizări adăugate. De exemplu, poți construi
 o imagine bazată pe Ubuntu care include Apache și aplicația ta, plus configurațiile necesare.

Pentru a construi propria imagine, creezi un Dockerfile cu o sintaxă simplă ce
 definește pașii de creare. Fiecare instrucțiune din Dockerfile creează un layer în imagine.
 Când modifici Dockerfile-ul și reconstruiești, se reconstruiesc doar layer-ele care s-au schimbat —
 de aceea imaginile sunt atât de ușoare și rapide.

### Containere

Un container este o instanță rulabilă a unei imagini . Poți crea, porni, opri,
 muta sau șterge un container folosind Docker API sau CLI. Poți conecta un container la una sau
 mai multe rețele, atașa stocare sau chiar crea o nouă imagine din starea sa curentă.

Implicit, un container este relativ bine izolat față de alte containere și față de mașina host.
 Când un container este eliminat, orice schimbări la starea sa care nu sunt stocate în stocare
 persistentă dispar .

### Exemplu: comanda docker run

La rularea acestei comenzi (cu configurația registry implicită) se întâmplă:
- 1 
 Dacă imaginea ubuntu nu există local, Docker o descarcă din registry (echivalent cu docker pull ubuntu ).
- 2 
 Docker creează un container nou.
- 3 
 Docker alocă un sistem de fișiere read-write ca layer final — containerul poate crea sau modifica fișiere local.
- 4 
 Docker creează o interfață de rețea și atribuie o adresă IP containerului.
- 5 
 Docker pornește containerul și execută /bin/bash . La exit , containerul se oprește dar nu se șterge.

---

## Tehnologia de bază

Docker este scris în Go și folosește mai multe funcționalități ale kernel-ului Linux
 pentru a-și livra funcționalitatea.

Docker folosește o tehnologie numită namespaces pentru a furniza workspace-ul
 izolat numit container. Când rulezi un container, Docker creează un set de namespace-uri pentru acel container.

---

## Notițe — Concepte fundamentale

Clarificări și analogii practice care completează teoria oficială.

### 1. Ce este o imagine Docker?

Ce este Ubuntu? Un sistem de operare bazat pe Linux — în viața de zi cu zi poate fi un sistem complet pe un laptop, cu interfață grafică, browser, player video etc.

Ce este o imagine Ubuntu în Docker? O imagine este un fel de „rețetă" sau copie de siguranță congelată — un fișier arhivat ce conține doar fișierele și utilitarele de bază necesare ca aplicațiile să ruleze.

### 2. De ce dacă nu o găsește local, o caută în registry?

Când instalezi Docker, ai două zone de depozitare:

Același principiu ca un magazin de aplicații pe telefon — dacă nu ai aplicația instalată, telefonul o descarcă automat din App Store sau Google Play.
- Local 
 Calculatorul tău — unde Docker salvează imaginile descărcate în trecut.
- Cloud 
 Registry-ul — un server centralizat pe internet (implicit Docker Hub) unde comunitatea și companiile publică imaginile.

### 3. De ce nu ar exista o imagine în registry?

Da, este posibil. Situații comune:

### 4. Imaginile trebuie să fie Ubuntu?

Nu. Există patru categorii principale de imagini:

### Sisteme de operare de bază

### Medii de rulare (limbaje de programare)

În culise, aceste imagini sunt construite tot peste un Linux mic (Debian sau Alpine), dar au deja compilatoarele și uneltele limbajului instalate.

### Servicii și baze de date

### Imagini proprii (personalizate)

Când îți creezi propriul proiect, scrii un Dockerfile prin care alegi de la ce imagine pleci:

De ce am folosit ubuntu în exemplu? docker run -i -t ubuntu /bin/bash e folosit ca exemplu clasic pentru a intra într-o linie de comandă Linux standard. În lumea reală vei folosi imaginea potrivită aplicației tale — node pentru un site web, python pentru un script de date, sau alpine pentru o aplicație ultra-ușoară.

---

## Tag-uri — Concept și strategie

Un tag nu e o copie a imaginii — e doar un alias , un pointer către un Image ID.
 Același Image ID poate avea mai multe tag-uri simultan.

### Strategii de tagging

---

## Comenzi — Explicații detaliate

Pornește Docker Desktop pe macOS.

Verifică dacă daemonul Docker rulează și afișează informații despre sistem (versiune, containere, imagini, spațiu pe disk). Dacă daemonul nu e pornit, comanda returnează eroare.

Construiește o imagine Docker din Dockerfile-ul din directorul curent.

Formă alternativă, echivalentă cu docker build . Fac exact același lucru.

Listează imaginile Docker disponibile local. Cu argument specific, filtrează doar imaginea respectivă.

Creează un tag nou care pointează la aceeași imagine. Nu copiază nimic — e doar un alias suplimentar pe același Image ID.

Același lucru în sens invers — util când ai făcut build cu :latest și vrei să adaugi un tag de versiune explicit înainte de push, fără să refaci build-ul. Ambele tag-uri coexistă după comandă.

Pornește un container nou din imaginea specificată. Dacă imaginea nu există local, Docker o descarcă automat din Docker Hub.

---

## Referință rapidă — Toate comenzile

---

## Kafka — Concepte fundamentale

Explicații complete care combină viața reală cu ce se întâmplă exact în cod.
 La finalul acestei secțiuni vei înțelege nu doar termenii, ci și de ce au fost create aceste lucruri.

### 1. Ce este un Topic?

Gândește-te la eMAG . În fiecare secundă se întâmplă lucruri diferite — comenzi noi, plăți, anulări, livrări.
 Dacă ar arunca totul într-o singură cutie de carton ar fi haos. Așa că pun cutii separate:

Un Topic este un canal de comunicare (o categorie) creat în Kafka.
 Când o aplicație trimite o informație, trebuie să spună explicit pe ce canal o trimite.

### 2. Ce este o Partiție și de ce există?

Aceasta este „secretul" vitezei masive a lui Kafka.

Când aplicația trimite 3 comenzi:

De ce e asta genial? (Paralelism) — Poți pune 3 servicii diferite să lucreze simultan:
 Serverul A citește DOAR Partiția 0, Serverul B DOAR Partiția 1, Serverul C DOAR Partiția 2.
 Fără partiții: procesare secvențială. Cu partiții: procesare în paralel, de 3× mai rapid!
- 0 Comanda lui Ion → Partiția 0
- 1 Comanda Mariei → Partiția 1
- 2 Comanda lui Vasile → Partiția 2

### 3. Ce este un Consumer și ce este Lag-ul?

Brutarii ( Producătorii ) pun pâinile pe o bandă rulantă. Angajații le împachetează ( Consumatorii ).

Dacă brutarii fac 100 pâini/min dar angajatul împachetează 60/min ,
 pe bandă se adună 40 de pâini . Acelea sunt Lag-ul .

Un Consumer este un microserviciu care stă într-o buclă infinită și întreabă Kafka:
 „Mai ai mesaje noi?"

### 4. Ce este un Broker?

Gândește-te la o rețea de magazine Mega Image . Fiecare clădire este un „Broker".
 Toate aparțin aceleiași firme (Cluster-ul Kafka), dar sunt clădiri fizice diferite, în locații diferite.

Un Broker este un calculator/server fizic pe care rulează programul Kafka și care are
 un Hard Disk instalat. La tine pe laptop = 1 Broker. Într-o bancă = 10–50 de calculatoare legate în rețea.

Dacă Broker 1 se strică (pică sursa), celelalte două calculatoare continuă să meargă fără probleme.

### 5. Ce sunt Mesajele?

Un Mesaj este scrisoarea din plic, pachetul de pe bandă — datele brute pe care le trimiți.
 De obicei un text în format JSON sau Bytes.

În Kafka UI, secțiunea Messages îți permite să cauți un mesaj după id_comanda 
 ca să vezi exact ce date a primit sistemul în acea secundă.

### 6. Ce este Schema Registry?

La ghișeul de pașapoarte nu îți acceptă un bilet scris pe un șervețel. Trebuie să completezi
 Formularul Model A-12 unde câmpul „CNP" are exact 13 cifre. Dacă scrii litere la CNP,
 ți-l aruncă la gunoi de la intrare.

Schema Registry este un server-gardian care stă între Producător și Kafka.
 Dacă un programator trimite "suma": "doua sute lei" (text în loc de număr),
 Schema Registry respinge mesajul înainte să intre în Kafka — prevenind crash-ul aplicației consumatoare.

### 7. Ce este ZooKeeper?

Într-o Orchestră Simfonică ai 50 de muzicieni. Fiecare își știe meseria, dar ai nevoie de un
 Dirijor . El le spune când să înceapă, cine bate ritmul, și ce se întâmplă dacă
 violonistul principal leșină (îi face semn secundului să preia).
- Verifică cine e viu — întreabă în fiecare secundă fiecare Broker; dacă Broker 2 nu răspunde, anunță imediat: „mutați partițiile lui pe Broker 3!"
- Ține minte setările — știe care partiție unde se află și cine e consumatorul autorizat

### Tabel sintetic — toate componentele

---

## Kafka — Clarificări & Întrebări frecvente

Răspunsuri la punctele nevralgice ale arhitecturii Kafka — legătura dintre Servicii, Docker, Partiții, Consumeri, Brokeri și ZooKeeper.

### 1. Un Topic corespunde unui Serviciu sau unui Container Docker?

O aplicație în sine — un proces care rulează cod (ex: un serviciu Web în Python/Java sau o bază de date).

Doar un fișier de log / un canal de date din interiorul Kafka (care rulează la rândul lui în propriul container).

### 2. Cine creează partițiile? Se creează automat?

Când creezi un Topic, tu (programatorul / omul de DevOps) decizi câte partiții va avea.

Definiția perfectă a partițiilor: Un topic poate avea mai multe partiții pentru ca
 informațiile să se propage în paralel și să fie mai rapid, nu secvențial. ✅
- 1 
 
 Din linie de comandă (CLI): 
 kafka-topics.sh --create --topic comenzi-noi --partitions 3
- 2 
 Din interfața grafică (Kafka UI): Apeși „Create Topic" și completezi câmpul Partitions: 5 .
- 3 
 Automat (dacă e activat auto-creation): Dacă trimiți un mesaj către un topic inexistent, Kafka îl creează pe loc cu numărul de partiții setat în configurația implicită (de obicei 1 partiție).

### 3. Consumer-ul și Lag-ul — clarificare importantă

### 4. Ce este un Broker? (Exemplul cu România și Coreea)

Utilizatorul din România și cel din Coreea sunt utilizatori/clienți , nu Brokeri. Ambii trimit mesaje către același Cluster Kafka .

### 5. Ce altceva mai face ZooKeeper în afară de health check?

ZooKeeper este baza de date de configurare și starea întregului cluster . Face 4 lucruri esențiale:

Fiecare partiție e duplicată pe mai mulți Brokeri, dar doar UN singur Broker poate fi Liderul (cel care primește și trimite date). Dacă Liderul pică, ZooKeeper organizează imediat alegeri și numește alt Broker Lider în milisecunde.

Salvează harta exactă: „Topic-ul comenzi are 3 partiții. Partiția 0 e pe Broker 1, Partiția 1 e pe Broker 2..." — fără această hartă, niciun client nu știe unde să trimită mesajele.

Păstrează regulile de securitate: cine are voie să scrie în ce topic și cine are voie să citească . Fără permisiune → acces refuzat.

Dacă adaugi un Broker nou sau schimbi o setare, ZooKeeper trimite semnal automat tuturor Brokerilor: „S-a schimbat configurația, actualizați-vă!"

#### Alegerea Liderului (Leader Election)

#### Harta Topic-urilor și Partițiilor

#### Control Acces (ACLs)

#### Notificări în timp real

### 6. Ce este un Cluster Kafka și ce configurație stochează ZooKeeper?

Un Cluster Kafka = mai multe servere Kafka (numite Brokeri ) care lucrează împreună ca un singur sistem.
 În local ai un cluster cu un singur Broker (pentru simplitate), dar în producție sunt 3, 5, 10+.

Ce configurație ține ZooKeeper:

### Rezumat — totul într-o singură frază

Aplicația ta ( container Docker ) trimite mesaje într-un
 Topic (împărțit în Partiții pentru viteză),
 care este stocat pe mai multe servere fizice ( Brokeri )
 gestionate de un dirijor ( ZooKeeper ),
 în timp ce aplicația Consumer citește mesajele —
 iar dacă citește prea încet, se creează Lag .

---

## Kafka — Organizare & Câte Partiții?

Un topic nu reprezintă un serviciu — reprezintă un eveniment / o acțiune / un fapt care s-a întâmplat în sistem .
 De aceea se folosesc adesea nume la timpul trecut: comanda-creata , plata-procesata , email-trimis .

### 1. Cum sunt organizate topicurile? — Naming Conventions

Nu există un automatism magic care să ghicească legăturile — totul se bazează pe
 design arhitectural și configurația codului .
 În companiile mari, topicurile sunt denumite după un tipar strict:

### 2. Din Codul Sursă — fiecare serviciu știe exact ce ascultă

Fiecare microserviciu are un fișier de configurare ( application.properties , config.yaml sau variabile de mediu) unde declară explicit ce topicuri ascultă.

### 3. Diagramă — un topic, mai mulți consumatori independenți

Un singur topic poate trimite informația către mai multe servicii în mod independent . Fiecare citește în ritmul lui.

Dacă Serviciul Email pică 10 minute, Serviciul Depozit continuă să funcționeze fără probleme.

### 4. De unde știi câte partiții să creezi?

Numărul de partiții nu se pune la întâmplare — se calculează pe baza capacității (throughput) .

Formula de calcul:

### 5. Best Practices

Regula practică: E mai ușor să mărești numărul de partiții mai târziu decât să îl micșorezi.
 Începe cu o valoare puțin mai mare decât ai nevoie pe moment.

---

## Kafka — PULL vs PUSH & Cluster

De ce mesajele nu „vin pur și simplu" și de ce Consumer-ul trebuie să le citească activ.

### 1. Modelul PUSH — cum „ar trebui să vină pur și simplu"

Există două modele prin care datele pot călători între aplicații:

Aplicația A are un mesaj și îl trimite cu forța către aplicația B.

Rezultat: Aplicația B se blochează, i se umple memoria și pică de tot ( Crash ).
 E ca și cum cineva ți-ar băga cu forța pe gât mâncare mai repede decât poți mesteca.

### 2. Modelul PULL — cum funcționează Kafka

Kafka este ca un bufet suedez : bucătarul (Producătorul) pune mâncarea pe masă (Topic),
 iar tu (Consumer-ul) te duci și iei exact cât poți mânca, când ești pregătit .

Consumer-ul rulează într-un loop:
- 1 Întreabă Kafka: „Ai mesaje noi pentru mine?"
- 2 Kafka îi dă o tranșă de mesaje (ex: 50 de mesaje).
- 3 Consumer-ul le procesează în ritmul lui (le salvează în bază, trimite emailuri etc.).
- 4 Când a terminat, cere următoarea tranșă .

### 3. Lag = mesajele necitite încă de Consumer

### 4. Cluster Kafka = echipa de Brokeri

Cuvântul „Cluster" în IT înseamnă „un grup de servere care lucrează împreună ca o singură echipă" .

Dacă acelui server i se arde placa de bază sau pică curentul,
 toată aplicația ta se oprește . Single point of failure.

Kafka duplică datele pe toate 3 servere. Dacă Broker 1 pică ,
 Broker 2 preia automat treaba în milisecunde .
 Utilizatorii nici nu observă.

### Rezumat — toate conceptele la un loc

### Schema completă a fluxului Kafka

Ritmul este dictat de Consumer: el determină când este pregătit și câte mesaje preia odată.

### De ce este acest model atât de puternic în producție

De Black Friday vin 100.000 mesaje/sec ? Kafka le salvează în siguranță pe discurile Brokerilor.
 Consumer-ul nu dă crash — continuă să proceseze constant (ex: 500/sec) până când Lag-ul scade înapoi la 0 .

Dacă Lag-ul crește prea mult, soluția e simplă: mai pornești încă o instanță de Consumer 
 (un container Docker în plus) care preia o altă partiție și ajută la procesare.
 Fără modificări de cod.

#### Protecție la vârfuri de trafic

#### Scalabilitate simplă

---

## Kafka — Offset

Piesa de mozaic care face ca întregul sistem de citire să funcționeze fără greșeală — chiar și după crash-uri.

### 1. Ce este un Offset?

Citești o carte de 500 de pagini (Topic-ul din Kafka). Nu poți citi totul într-o zi.
 Înainte să te culci, pui un semn de carte la pagina 45.

A doua zi nu o iei de la pagina 1 — te uiți la semn și știi că începi de la pagina 46 .

Offset-ul este acel semn de carte — un număr de ordine unic și secvențial
 atribuit fiecărui mesaj care intră într-o partiție din Kafka.

### 2. Cum funcționează Offset-ul în Kafka?

Mesajele sunt salvate în partiție ca într-o listă numerotată:

### 3. Rolul Offset-ului

Fără offset-uri, Consumer-ul nu ar ști de unde să reia citirea dacă se întâmplă ceva!

Consumer-ul citește Offset 0, 1, 2. După ce procesează Offset 2, trimite un semnal
 numit Committed Offset : „Am terminat de procesat până la Offset 2!"

Serverul Consumer-ului pierde curentul la Offset 2. La repornire, Consumer-ul întreabă Kafka:
 „Care a fost ultimul offset al meu?" → Kafka: „Offset 2" → Consumer cere direct Offset 3 .

Garantează că mesajele sunt procesate o singură dată — sau cel puțin știi exact
 ce ai citit deja și ce nu.

#### Ține minte progresul citirii

#### Crash Recovery

#### Previne citirea dublă

### 4. De ce Kafka are nevoie de volum? (legătura cu offset-ul)

Kafka nu e ca un curier care preia un mesaj și îl livrează imediat.
 Kafka e mai mult ca o arhivă poștală — păstrează toate mesajele pe disc
 pentru o perioadă de timp (implicit 7 zile), indiferent dacă cineva le-a citit sau nu.

Dacă Kafka nu ar scrie pe disc (fără volum), la repornirea containerului:

### 5. Lag = diferența dintre offseturi

Când te uiți în Kafka UI, vei vedea doi termeni:

Offset = numărul de pagină / semnul de carte din partiție (0, 1, 2, 3...).
 Îi spune Consumer-ului exact de unde să citească și unde să reia dacă aplicația se prăbușește și repornește.
 LAG = Log End Offset − Committed Offset.

---

## Must-Have Comenzi — Pipeline DevOps

Comenzi grupate pe etapele reale ale unui flux de lucru DevOps, de la dezvoltare locală până la curățarea sistemului.

Docker Compose este un instrument care îți permite să definești și să pornești
 mai multe containere simultan , dintr-un singur fișier de configurare numit
 docker-compose.yml .

O aplicație reală rareori rulează dintr-un singur container. Un proiect tipic are:

Fără Compose, ar trebui să pornești fiecare container manual, cu comenzi lungi, în ordinea corectă,
 să le conectezi la aceeași rețea, să configurezi volumele. Compose face toate astea automat dintr-o
 singură comandă: docker compose up .

services:
 web:
 build: .
 ports:
 - "8000:8080"

 db:
 image: postgres:15
 volumes:
 - db_data:/var/lib/postgresql/data

 redis:
 image: redis:alpine

volumes:
 db_data: 

 Situație Folosești Compose? 
 
 Aplicație cu mai multe servicii (backend + DB + cache) ✅ Da 
 Development local — vrei să pornești tot dintr-o comandă ✅ Da 
 Testare în CI/CD ✅ Da 
 Un singur container simplu, fără dependințe ❌ Nu — docker run e suficient 
 Producție la scară mare (sute de containere) ❌ Nu — acolo se folosește Kubernetes 

 Pe scurt: docker = gestionezi un container. docker compose = gestionezi o aplicație întreagă formată din mai multe containere.

 docker compose up 
 Pornește toate serviciile definite în docker-compose.yml și afișează jurnalele în terminal. Ctrl+C oprește totul. 

 docker compose up -d 
 Pornește toate serviciile în fundal. -d ( detached ) — procesul rulează independent de terminal; poți închide fereastra fără să oprești serviciile. 

 docker compose up --build 
 Reconstruiește imaginile locale înainte de pornire. --build — forțează rebuild chiar dacă imaginea există deja în cache local. Folosit după modificări de cod sau Dockerfile. 

 docker compose ps 
 Afișează starea serviciilor din fișierul Compose curent: nume container, status (Up/Exit), porturi expuse. 

 docker compose logs -f 
 Urmărește jurnalele live pentru toate serviciile. -f ( follow ) — stream continuu; jurnalele noi apar în timp real. Oprire cu Ctrl+C. 

 docker compose logs -f web 
 Afișează jurnalele doar ale serviciului numit web . Util când vrei să izolezi output-ul unui singur serviciu dintr-o stivă mai mare. 

 docker compose exec web bash 
 Deschide un shell Bash în interiorul containerului serviciului web (care trebuie să fie deja pornit). exec — execută o comandă într-un container activ ; nu creează un container nou. 

 docker compose restart db 
 Repornește doar serviciul db (baza de date), fără a atinge celelalte servicii. Util după modificări de configurație. 

 docker compose down 
 Oprește și șterge containerele și rețelele create de Compose. Volumele de date sunt păstrate (datele din baza de date supraviețuiesc). 

 docker compose down -v 
 Oprește totul și șterge volumele de date. -v ( volumes ) — resetează complet baza de date și orice stocare persistentă. Folosit pentru un fresh start. 

 2 
 
 Construire & Împachetare 
 Docker Build & Local Images — crearea imaginilor pentru aplicație 

 docker build se folosește când vrei să construiești manual o imagine Docker 
 din fișierul Dockerfile aflat în directorul curent.

Da. Depinde de cum e configurat docker-compose.yml :

docker compose up execută automat docker build în spate. Containerul pornit nu se actualizează până nu dai restart sau --build .

Flux: modifici codul → docker build → docker compose up -d ca să folosească noua imagine.

Sunt flag-uri separate combinate ca -it — transformă execuția într-o sesiune de terminal interactivă.

Păstrează canalul de intrare standard ( STDIN ) deschis. Fără -i , containerul ar ignora orice tastezi.

Alocă un terminal virtual responsabil de: prompt colorat, comenzi interactive ( nano , vim ), taste speciale (săgeți, Tab, Ctrl+C).

CE rulează în container — lista proceselor, fără să intri în container.

Util când aplicația nu răspunde — verifici dacă procesul principal există sau s-a prăbușit în interior.

CÂT consumă containerul — CPU%, RAM, I/O rețea în timp real.

Util când aplicația e lentă — verifici dacă consumă prea mult CPU sau memorie.

Îți arată maparea porturilor — prin ce port din calculatorul tău poți accesa aplicația din container.

docker events este un stream de jurnal în timp real — rămâne „deschisă" în terminal și afișează fiecare acțiune efectuată pe Docker:

Dacă un container repornește continuu sau moare subit, docker events îți arată exact evenimentele ( die , kill , oom - out of memory) în secunda în care se produc.

Poți scrie scripturi de DevOps care ascultă aceste evenimente și declanșează alerte sau acțiuni automate când un container pornește sau se prăbușește.

Un daemon este un program care rulează în fundal, fără interfață grafică, așteptând instrucțiuni. Docker e împărțit în două părți:

Ce tastezi tu în terminal: docker run , docker events

Nu face munca — trimite comenzi prin API.

„Creierul" Docker — rulează permanent în fundal.

Descarcă imagini, creează containere, gestionează volume, rețele și generează evenimentele din docker events .

Numai serviciile stateful (care trebuie să-și amintească date între reporniri) au nevoie de volume.
 Cele stateless nu stochează nimic local — pot fi oprite și repornite fără pierderi.

Imaginile Docker pot declara intern directive VOLUME în propriul Dockerfile. Când Docker pornește containerul,
 creează automat volume anonime (cu hash) pentru acele căi — chiar dacă tu nu le-ai specificat în docker-compose.yml .

Un container este efemer — când se oprește sau se șterge, tot ce a scris pe disc dispare.
 Un volume este stocare externă containerului: datele există pe mașina host și supraviețuiesc indiferent ce i se întâmplă containerului.

#### Când se folosește?

#### Dacă am pornit deja cu docker compose , mai pot folosi această comandă?

#### Ce înseamnă flag-urile -i și -t ?

#### Diferența dintre docker top și docker stats

#### Cum citești rezultatul docker port web_app ?

#### Ce este docker events și ce este Docker Daemon?

#### Ce este Docker Daemon?

```
services:
 web:
 build: .
 ports:
 - "8000:8080"

 db:
 image: postgres:15
 volumes:
 - db_data:/var/lib/postgresql/data

 redis:
 image: redis:alpine

volumes:
 db_data:
```

```
[ Cerere Client ]
 │
 ▼
┌─────────────────────────────────────────────────────────────┐
│ MICROSERVICIU (Sender) │
│ │
│ BEGIN TRANSACTION │
│ 1. INSERT INTO orders (...) ← business entity │
│ 2. INSERT INTO outbox (event, payload) ← evenimentul │
│ COMMIT TRANSACTION ← Toate sau Nimic! (ACID) │
└──────────────────────────────┬──────────────────────────────┘
 │
 ▼
┌─────────────────────────────────────────────────────────────┐
│ BAZA DE DATE LOCALĂ │
│ ┌────────────────┐ ┌──────────────────────────┐ │
│ │ Tabela: orders │ │ Tabela: outbox │ │
│ └────────────────┘ └─────────────┬────────────┘ │
└───────────────────────────────────────────┼─────────────────┘
 │
 Citește periodic (Polling / CDC)
 │
 ▼
 ┌──────────────────────────┐
 │ MESSAGE RELAY (Worker) │
 └────────────┬─────────────┘
 │
 Trimite mesajul în siguranță
 │
 ▼
 ┌──────────────────────────┐
 │ MESSAGE BROKER (Kafka) │
 └──────────────────────────┘
```
- 1 
 Testare locală rapidă — ai modificat codul sau Dockerfile-ul și vrei să construiești imaginea fără să pornești un întreg ansamblu de servicii.
- 2 
 CI/CD Pipelines — un robot (GitLab CI, GitHub Actions, Jenkins) preia codul, construiește imaginea, îi pune tag și o urcă în registry.
- 3 
 Imagini modulare — creezi o imagine de bază pe care să o folosească și alți colegi din echipă.
- Salveze comanda în baza de date SQL: INSERT INTO orders...
- Trimită un eveniment în Kafka: kafkaProducer.send("comanda-creata") — astfel Serviciul de Facturare și Serviciul de Depozit să știe că trebuie să proceseze pachetul
- Fără 2PC — nu depinzi de protocoale distribuite
- Garanție 100% : mesajele se trimit dacă și numai dacă tranzacția DB a reușit
- Ordinea se păstrează — ID/Timestamp secvențial din DB → mesaje trimise în Kafka exact în ordine
- Developer-ul poate uita să insereze în outbox → evenimentul nu se trimite niciodată
- Livrare "At Least Once" : Relay-ul poate trimite același mesaj de două ori (crash după publish, înainte să marcheze ca trimis)

---

## Arhitectura Serviciilor — Stub, Mock & Diagrame

### 1. Ce este un Stub? (și diferența față de Mock)

Un stub = o implementare falsă/simplificată a unui serviciu extern real.
 E un înlocuitor temporar folosit când serviciul real nu e disponibil (prea scump, extern, nu există încă).

În diagramă, attestation provider (stub) înseamnă:

Ar trebui să existe un apel către un furnizor extern real (ex: API Vodafone/Orange care validează și semnează un număr de telefon).

În loc de acel API real, avem signer.py care face HMAC-SHA256 local — mimează ce ar face furnizorul real.

Stub vs. Mock — diferența subtilă:

### 2. Cum citești o diagramă de arhitectură

Regulă generală: de sus în jos, urmând săgețile . Fiecare cutie = un serviciu sau o componentă. Fiecare săgeată = un flux de date, cu direcție și tip de eveniment.

Cele 3 componente din diagramă:

---

## Proiect Curent — Number Management Platform

### Port Order Service

Port Order Service gestionează procesul de portare — transferul unui număr de telefon
 de la un operator vechi (ex: Verizon) la 8x8.

reserve → clientul vrea să porteze numărul, pornește procesul. 
 release → clientul renunță la număr, îl eliberează. 
 GET → vezi statusul curent al portării.

Rulează la fiecare 5 secunde, verifică ce ordere au next_action_at în trecut și le avansează. Fără poller, portarea ar sta blocată.

Ascultă number-inventory-service → când apare NUMBER_CREATED , creează un port order pentru acel număr.

Publică în port-order-status → RESERVED, ACTIVE, REJECTED, RELEASED — pentru ca Inventory să actualizeze statusul numărului.

#### HTTP Endpoints — comenzi manuale

#### Poller — buclă de fundal automată

#### Kafka Consumer + Producer

### Numărul terminat în 8 vs. 9 — nu e același lucru

Sunt două refuzuri simulate independente pentru două procese complet diferite:

### Fluxul complet al sistemului

8 și 9 sunt probleme independente:

Ce înseamnă un număr atestat?

Atestat = numărul are o semnătură criptografică care dovedește că 8x8 îl deține.
 Fără asta, apelurile apar "Spam Likely" pe telefonul celui care primește.
 Portarea și atestarea sunt procese separate care se întâmplă la momente diferite:

Un număr terminat în 9 nu ajunge niciodată la atestare — portarea eșuează,
 deci numărul rămâne la Verizon și 8x8 nu are ce să semneze.
 Atestarea se face doar după ce portarea reușește și numărul devine ACTIVE.

### Portat vs. Atestat — consecințe practice
- Numărul funcționează — poți suna și primi apeluri
- Numărul e al tău, e la 8x8
- Apelurile outbound apar ca "Spam Likely"
- Nimeni nu va răspunde — toți cred că e spam
- Numărul nu e al tău — rămâne la Verizon
- Nu poți face nimic cu el prin 8x8

### Registration Service

Registration Service face un singur lucru: dovedește că 8x8 deține un număr de telefon .
 Semnătura confirmă că numărul aparține cu adevărat operatorului care face apelul.

Fluxul real:

### Ordinea de execuție — cine pornește primul?

Registration Service reacționează , nu inițiază. Inventory e cel care anunță, Registration e cel care ascultă și răspunde.

### De ce apare un număr ca ACTIVE în topic dar REGISTRATION_FAILED în altul?

Statusul numărului și semnătura sunt două lucruri complet separate .
 Fiecare serviciu anunță ce știe din domeniul lui — nu se amestecă în treaba celuilalt.

→ "numărul +108 există și e ACTIVE" ✅ 
 Inventory și-a făcut treaba — a schimbat statusul. Nu știe și nu îl interesează dacă Registration va reuși să semneze.

→ "nu am putut semna +108" ❌ 
 Registration și-a făcut treaba — a încercat să semneze. Numărul se termină în 8 → refuz → REGISTRATION_FAILED.

Ordinea evenimentelor pentru +108:

---

## SSH Client — Conectare Securizată la Distanță

Un SSH Client (Secure Shell Client) este un program sau o aplicație software care îți permite să te conectezi de la distanță, în mod securizat și criptat, la un alt calculator sau server (numit SSH Server ).

Când folosești un client SSH, poți trimite comenzi pe serverul la care te-ai conectat și poți opera pe acesta ca și cum ai fi fizic în fața lui, folosind o interfață în linie de comandă (terminal).

### Cum funcționează?

Relația este de tip Client - Server :

### Exemple de SSH Clients (Aplicații)

În funcție de sistemul de operare pe care îl folosești, există mai mulți clienți SSH:

SSH integrat direct în cmd , PowerShell sau Terminal . Conectare prin:

Unul dintre cei mai populari și vechi clienți SSH gratuiți pentru Windows, care oferă o interfață grafică.

Aplicații moderne folosite de administratori de sistem — permit gestionarea zecilor de servere, transfer de fișiere (SFTP) și opțiuni avansate.

Extensie pentru Visual Studio Code care îți permite să editezi codul direct pe serverul la distanță prin SSH.

### La ce este folosit un SSH Client?

Pentru a configura servere precum cele din AWS (EC2) , Google Cloud sau Azure.

Prin protocoale derivate din SSH: SFTP (Secure File Transfer Protocol) sau SCP (Secure Copy Protocol).

Automatizarea sarcinilor pe servere fără interfață grafică.

---
