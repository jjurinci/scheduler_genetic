## Genetski algoritam

### Terminologija

rasp = atomična jedinica predmeta koja ide u raspored identificirana po 
       kompozitnom ključu sastavljenom od id-a, vrste termina i grupe predmeta.
       Primjerice, neki od rasp-ova koje predmet "Programiranje" može imati
       su "Programiranje, vježbe, grupa 1", "Programiranje, vježbe, grupa 2",
       "Programiranje, teorija, grupa 1", itd.

raspored = rječnik oblika raspored[rasp] = (dvorana, dan, sat)

### Kako algoritam funkcionira

1. Izgenerira N "slučajnih" rasporeda tako što svakom rasp-u pridruži slučajno odabran termin.
2. Slučajni rasporedi se šalju optimizator-u
3. Optimizator iterira K puta po dobivenim rasporedima i u svakoj iteraciji ih izmjenjuje uz pomoć genetskih operatora.
   Nakon što je svaki individualan raspored izmijenjen, poslan je fitness funkciji "grade" koja ocijenjuje njegovu kvalitetu.
   Rasporedi su sortirani po ocjeni i samo M najbolje ocijenjenih služe kao ulaz u iduću iteraciju.
4. Nakon prirodne konvergencije (ocjena optimalna), prisilnog zaustavljanja preko front end-a ili izvršenja svih iteracija
   algoritam vraća 5 najbolje ocijenjenih rasporeda.


### Fitness funkcija "grade"

Grade je funkcija koja prima raspored i vraća ocjenu za njegovu kvalitetu.
Ocjena se smanjuje svakim kršenjem postavljenih ograničenja.
Ocjena '0' označuje optimalnost odnosno da niti jedno ograničenje nije prekršeno.

Postavljena ograničenja su:
* Profesor ne smije imati 2 ili više rasp-a u istom danu i satu
* Dvorana ne smije imati 2 ili više rasp-a u istom danu i satu
* Semestar ne smije imati 2 ili više rasp-a u istom danu i satu
* Rasp-ovi se ne smiju raspoređivati po predefiniranim danima i satima nedostupnosti njihovih profesora
* Rasp-ovi se ne smiju raspoređivati po predefiniranim danima i satima nedostupnosti dvorana
* Računalan rasp mora ići u računalnu dvoranu
* Kapacitet dvorane mora biti dovoljan za broj studenata raspa

### Genetski operatori

##### Mutate
Slučajnim odabirom odabire 1 rasp iz rasporeda kojem pridružuje slučajno
odabran slobodan termin iz skupa slobodnih termina.

##### Crossover
Prima 2 različita rasporeda kao parametar. Svakom rasp-u iz 1. rasporeda
pridružuje ili trenutni termin koji ima u 1. rasporedu ili termin koji ima u
2. rasporedu. Odabir između ta 2 termina je slučajan.

##### Shuffle (professor/semester/classroom)
Uzimamo za primjer shuffle profesora jer je logika gotovo identična za semestre i dvorane.
Svaki rasp u rasporedu se ispituje za kolizije slobodnog vremena njegovog profesora.
Ukoliko se pronađe kolizija profesora raspa u vrijeme kada se taj rasp održava,
pronalazi se novi slobodan termin koji neće izazivati kolizije.
Rasp-u se zatim pridružuje pronađeni termin.

##### Swapper
Svaki rasp u rasporedu se ispituje za kolizije slobodnog vremena profesora, semestara i dvorana.
Ukoliko se pronađe barem 1 kolizija, taj raspored se pridodaje listi problematičnih rasp-ova.
Slučajnim odabirom se odabire 1 problematičan rasp iz liste problematičnih rasp-ova.
Svaki rasp u rasporedu privremeno mijenja svoj termin sa terminom problematičnog rasp-a te nakon
svake izmjene se raspored šalje funckiji grade koja vraća ocjenu. Ukoliko se ocjena poboljšala,
izmjena termina 2 rasp-a se trajno sprema u raspored.


[Frontend (github)](https://github.com/jjurinci/scheduler_ui)

[Servis za DML (github)](https://github.com/jjurinci/scheduler_dml)

[Dokumentacija (pdf)](https://zir.nsk.hr/islandora/object/unipu%3A5086/datastream/PDF/view)

