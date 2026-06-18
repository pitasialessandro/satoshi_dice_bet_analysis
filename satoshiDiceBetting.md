# Laboratorio di Web Scraping

## BetFlow: analisi di Satoshi Dice, un servizio di betting su Bitcoin

(^)
Scopo del progetto è lo studio delle transazioni su blockchain generate dall’utilizzo di
SatoshiDice, uno dei primi servizi di betting basati su Bitcoin. L’obiettivo è analizzare
la struttura e la dinamica delle operazioni di bet e di payout.
Viene fornito un DataSet di Bitcoin che contiene una selezione delle transazioni incluse nei
blocchi compresi tra il blocco genesis, minato in data 03-01-2009, 17:15:05 e il blocco
di altezza 214562 , minato in data 31-12-2012, 11:52:37.
Il DataSet è stato ottenuto tramite una serie di trasformazioni effettuate sui dati pubblici
reperiti dalla blockchain di Bitcoin. In particolare, per diminuire la dimensione del DataSet:
● sono state eliminate tutte le transazioni Coinbase il cui output non è stato speso
alla data dell’ultimo blocco;
● gli hash delle transazioni, gli indirizzi contenuti negli output delle transazioni, e gli
script sono stati sostituiti con identificatori univoci interi. La corrispondenza tra gli
indirizzi della blockchain e gli identificatori univoci del DataSet è stata memorizzata in un ulteriore file di mapping.

## 1. Descrizione del DataSet

Il DataSet consiste di 4 files csv
● transactions.csv, che contiene una riga per ogni transazione del DataSet, con
i campi:
  ○ timestamp: timestamp del blocco che contiene la transazione. Corrisponde
  al tempo UNIX del miner, e indica il momento in cui il blocco è stato minato
  ○ blockId: identificatore del blocco che contiene la transazione. Indica
  l’altezza di tale blocco, ovvero la sua distanza dal blocco genesis di Bitcoin
  ○ txId: identificatore unico della transazione corrispondente all’hash del
  contenuto della transazione
  ○ isCoinbase: indica se la transazione è una Coinbase, ovvero una
  transazione che trasferisce la ricompensa al miner che ha risolto la PoW (
  false, 1 true)
  ○ fee: eventuale commissione volontaria contenuta nella transazione,
  attribuita al miner che la inserisce in un blocco. Può essere zero.

● inputs.csv, che contiene una riga per ogni campo di input di ogni transazione del
DataSet, con i campi:
  ○ txId: identificatore della transazione all’interno della quale si trova questo
  input
  ○ prevTxId: identificatore della transazione che ha creato l’output
  attualmente speso da questo input
  ○ prevTxpos: posizione dell’output attualmente speso come input, all’interno
  della transazione che lo ha creato (diversa da quella che contiene questo input)

● outputs.csv, che contiene una riga per ogni campo di output di ogni transazione
del DataSet, con i campi:
  ○ txId: identificatore della transazione all’interno della quale si trova questo
  output
  ○ position: posizione di questo output all’interno della transazione che lo ha
  creato
  ○ addressId: indirizzo a cui viene inviato questo output, è un identificatore
  univoco che viene mappato sull’indirizzo reale tramite il file di mapping
  ○ amount: valore trasferito da questo output
  ○ scripttype: codice che identifica lo script contenuto in questo output.
  Questo campo non è utilizzato in questo progetto.
● mapping.csv, file di mapping degli indirizzi, campi:
  ○ hash: hash del corrispondente indirizzo contenuto nella blockchain di Bitcoin
  ○ addressId: identificatore unico di ogni indirizzo contenuto in almeno un output delle transazioni del DataSet

Nel caso di output con script di tipo 0 che non contengono address, nel file di
mapping si trova un identificatore univoco rappresentato da una # seguita da
un numero che rappresenta quell’output e solo quello, associato con
l’identificatore utilizzato per quell’output nel DataSet..
```
### Figura 1: Struttura del DataSet

La struttura del DataSet è mostrata in Fig.1. Il DataSet è disponibile su Drive al link:


### https://drive.google.com/file/d/1q-nmPc3VGdiP4e3Qa83ShMJ7qlpF78Fy/view

Oltre al dataset viene anche fornito un file contenente un insieme di indirizzi Bitcoin
associati al servizio SatoshiDice, ciascuno caratterizzato da uno specifico schema di
payout e da parametri probabilistici distinti. Ogni riga del dataset rappresenta un indirizzo a
cui è possibile inviare una transazione per effettuare una bet, con condizioni di vincita e
rendimento predefinite. Gli indirizzi riportati sono vanity address, ossia indirizzi
generati intenzionalmente per contenere una specifica sequenza di caratteri riconoscibile; in
questo caso, essi presentano il prefisso “1dice”, che li rende facilmente identificabili come
appartenenti al servizio SatoshiDice. Un esempio di indirizzo è il seguente:
1dice9wVtrKZTBbAZqz1XiTmboYyvpD3t

Le colonne del dataset includono le seguenti informazioni:

```
● Name: etichetta descrittiva della condizione di vincita (ad esempio “lessthan X”, che
indica una vincita se il risultato del gioco è inferiore a una certa soglia);
● Address: indirizzo Bitcoin destinatario della bet, univocamente associato a uno
specifico schema di payout;
● WinOdds: probabilità di vincita associata all’indirizzo, espressa in percentuale;
● PriceMultiplier: moltiplicatore applicato alla puntata in caso di vincita;
● HousePercentage: margine del banco (house edge);
● ExpectReturn: rendimento atteso per il giocatore;
● MinimumBet: importo minimo accettato per la bet;
● MaximumBet: importo massimo accettato per la bet.

Il DataSet degli indirizzi è disponibile su Drive al link:

https://drive.google.com/file/d/1pULXhKEUOIVMavJgOnCzMa2XOn7Xm2rB/view?usp=shari
ng

## 2. Il servizio di betting Satoshi Dice

Satoshi Dice è stato uno dei primi e più popolari servizi di gioco d’azzardo basati su
Bitcoin, lanciato nel 2012. Il servizio permetteva agli utenti di scommettere inviando
una quantità di bitcoin (BTC) a specifici indirizzi, ciascuno associato ad una probabilità di
vincita ed un payout prefissato. A differenza dei tradizionali servizi online, non era richiesta
alcuna registrazione o creazione di account: l’intero sistema funzionava esclusivamente
tramite transazioni sulla blockchain.
Il risultato della scommessa veniva determinato in modo trasparente utilizzando dati pubblici
della blockchain, mentre eventuali vincite venivano restituite automaticamente tramite una
nuova transazione Bitcoin. Il servizio, basato unicamente su trasferimenti on-chain,
rappresenta uno dei primi esempi di applicazione che sfrutta direttamente il protocollo
Bitcoin senza intermediari tradizionali.

Esempio 1
Supponiamo di scommettere una bet = 0.01 BTC, su un indirizzo 1dice con probabilità
di vincita = 20%, il payout è 4.8x della puntata in caso di vittoria. Quindi, se vinci, ricevi 0.048 BTC, se perdi, ricevi 0 BTC (oppure 1 Satoshi, a seconda della versione del servizio). Notare che il payout dovrebbe essere 0.05 BTC, in realtà si riceve 0.048

BTC , ma il gioco trattiene sempre un margine, quindi paga un po’ meno, nell’esempio 4.8x.

## 3. Descrizione delle modalità di betting on-chain

Una scommessa su SatoshiDice avviene interamente tramite una normale transazione
Bitcoin, detta transazione di bet, in cui l’utente invia una quantità di BTC a uno
specifico indirizzo del servizio, tipicamente un indirizzo con prefisso 1dice, un vanity
address. Ognuno di questi indirizzi identifica il tipo di scommessa, ovvero la probabilità
di vincita ed il payout associato. La transazione, in generale, può includere più output,
incluso un indirizzo output di resto (change address), che ritorna la differenza all’utente
(ovvero l’importo non speso per la bet). La transazione di bet può contenere più di un input,
anche se nella maggior parte dei casi ne contiene uno solo (quando l’importo scommesso è
coperto da un singolo UTXO).
Una volta che la transazione viene trasmessa alla rete, SatoshiDice ne legge i dettagli, in
particolare l’importo e l’indirizzo di destinazione, e determina l’esito della scommessa
utilizzando dati pubblici della blockchain (ad esempio l’hash della transazione o del blocco
successivo).
Se l’utente perde, in genere non avviene alcun vero payout: i fondi inviati restano al servizio.
In alcuni casi, però, SatoshiDice può comunque inviare una transazione di risposta con
un importo simbolico di 1 Satoshi (10-8 BTC), sia come segnale dell’esito che per
mantenere uniforme il meccanismo di risposta on-chain. Se invece l’utente vince, Satoshi
Dice genera una nuova transazione Bitcoin, detta transazione di payout, che invia
la vincita a uno degli indirizzi utilizzati come input nella transazione di bet. L’importo del
payout è determinato dal valore scommesso e dalla probabilità associata all’indirizzo scelto.
In questo modo, sia la scommessa che il pagamento delle vincite avvengono esclusivamente
tramite transazioni on-chain, senza alcuna interazione diretta tra utente e servizio al di fuori
della blockchain. Il meccanismo di betting è illustrato in Fig. 2.

Figura 2: Bet e Payout Transactions


## 4. Analisi generali delle bet e dei playout

Si richiedono le seguenti analisi generali sulle transazioni effettuate verso Satoshi Dice.

1. Calcolare la percentuale di transazioni di bet rispetto al numero complessivo di
    transazioni, in relazione a diversi periodi temporali.
2. Valutare la popolarità di ogni indirizzo di betting, calcolata considerando,
    rispettivamente, il numero di bet per ogni indirizzo con prefisso 1dice contenuto
    nel file e l’amount complessivo delle bet per quell’indirizzo. Presentare un grafico che
    confronti la popolarità dei vari indirizzi.
3. Valutare la distanza tra transazioni di bet e corrispondenti transazioni di payout. Una
    transazione di payout è considerata associata a una transazione di bet se un input della
    transazione consuma un UTXO della corrispondente transazione di bet (ovvero un
    output non speso della transazione di bet).
4. Eseguire le seguenti analisi, separatamente per i 3 indirizzi più popolari
    o Distribuzione temporale delle bet: analizzare come le puntate
       sono distribuite nel tempo, utilizzando diverse scale temporali (ad esempio:
       per ora, per giorno, per settimana).
    o Analisi correlazione tra fee e amount della bet Verificare
       l’eventuale presenza di una correlazione tra le fee di transazione e l’importo
       scommesso
    o Intervallo tra bet consecutive: analizzare la distribuzione del
       tempo intercorso tra una puntata e la successiva.
Si dovrà scegliere la modalità di visualizzazione più opportuna per evidenziare i risultati delle
precedenti analisi.

## 5. Analisi di sequenze di bet

Si definisce una catena di bet come una sequenza di transazioni in cui gli output di una
bet vengono riutilizzati come input nella bet successiva, stabilendo così un legame diretto e
tracciabile tra le transazioni. Al fine di ottenere catene lineari e facilmente interpretabili, si
considerano esclusivamente le “simple bet”, ovvero transazioni caratterizzate da un solo
input e da esattamente due output, di cui uno destinato a un indirizzo 1dice di
SatoshiDice e l’altro identificato come output di resto (change). Due restricted bet
consecutive appartengono alla stessa catena se e solo se l’input della seconda coincide con
l’output di resto della prima e l'altro output è indirizzato a uno degli indirizzi 1dice. In tal
modo, ogni catena rappresenta una sequenza lineare di transazioni in cui il resto di una
puntata viene riutilizzato come input della puntata successiva.. Un esempio di catena di
restricted bet è mostrata in Fig.3.


```
FIg 3 Catena di restricted bets
```
L’analisi sarà limitata alle simple bet associate all’indirizzo 1dice caratterizzato dal maggior
numero di transazioni nel dataset. Al fine di individuare tali catene, si richiede di costruire un
grafo diretto 𝐺 =(𝑉,𝐸), in cui:
● ogni nodo 𝑣 ∈𝑉 rappresenta una singola simple bet;
● esiste un arco diretto (𝑣௜,𝑣௝)∈𝐸 se e solo se l’ input della simple bet j corrisponde
all’ output di resto della simple bet 𝑖 ;
● a ciascun arco è associata un’etichetta che identifica l’indirizzo responsabile del
collegamento tra le due bet.

Una volta costruito il grafo, si richiede di:

1. identificare le catene di simple bet come cammini nel grafo;
2. calcolare la distribuzione delle lunghezze di tali catene (in termini di numero di nodi o
    di archi);
3. rappresentare graficamente tale distribuzione, al fine di analizzare la struttura e la
    persistenza delle sequenze di gioco.

## 6. Scraping di WalletExplorer per verificare appartenenza a

## wallet

Limitatamente alle ℎ catene di bet di lunghezza massima individuate nella fase precedente, si
richiede di verificare se gli indirizzi associati agli archi di ciascuna catena appartengano a un
medesimo wallet.
In particolare, per ogni catena selezionata, si dovrà considerare l’insieme degli indirizzi che
etichettano gli archi del grafo (ossia gli indirizzi che realizzano il collegamento tra bet
consecutive) e verificarne l’appartenenza a uno stesso wallet.
A tal fine, si richiede di effettuare web scraping sul servizio WalletExplorer, utilizzando
le informazioni disponibili per determinare se tutti gli indirizzi appartengono allo stesso
wallet. Si ricorda che su WalletExplorer, un wallet non è un singolo indirizzo, ma un
cluster di indirizzi Bitcoin che si ritiene appartengano alla stessa entità.
WalletExplorer raggruppa indirizzi la multi-input heuristic che prevede che, se più
indirizzi compaiono come input nella stessa transazione, probabilmente sono controllati dallo
stesso utente. Inoltre, quando possibile, WalletExplorer associa questi wallet a entità


note (come exchange o servizi), effettuando una forma di de-anonimizzazione parziale della

## blockchain.

L’analisi richiesta dovrà stabilire se:
● tutti gli indirizzi di una catena sono riconducibili a un unico wallet;
● oppure se la catena coinvolge indirizzi appartenenti a wallet distinti.
I risultati dell’analisi dovranno includere, per ciascuna catena individuata, almeno le seguenti
informazioni:
● identificativo univoco della catena;
● lunghezza della catena (espressa in numero di nodi o, alternativamente, di archi);
● numero totale di indirizzi coinvolti;
● numero di wallet distinti identificati;
● percentuale di indirizzi riconducibili al wallet predominante;

●^ identificativo del wallet principale.^
Nel caso in cui il wallet principale sia stato deanonimizzato, l’identificativo corrisponderà al
nome del servizio così come riportato su WalletExplorer; in caso contrario, sarà
utilizzato l’identificativo numerico assegnato da WalletExplorer al wallet stesso.

## 7. Modalità di Consegna del progetto

Il progetto deve essere eseguito individualmente.
E’ possibile scaricare il DataSet di riferimento da Drive, link:
https://drive.google.com/file/d/1RWP19B0MbfDL43DAEhPwcVkb8nLoIbhX/view?usp=shari
ng
Il riferimento è a Google Drive fornito da Unipi, per cui l’accesso dovrebbe essere consentito
con credenziali Unipi. In caso di difficoltà nell’accesso, inviare una mail a laura.ricci@unipi.it.
Il materiale da consegnare comprende:
● codice dell'applicazione (Notebook .ipynb) e relazione, integrata nel Notebook. Si
prega di generare il pdf del Notebook e di sottomettere tutto il materiale in formato
.pdf ;
● il codice deve essere sviluppato in Python e per la parte di scraping si deve utilizzare
la libreria Selenium ;
● la scelta di opportune strategie di visualizzazione dei risultati delle analisi richieste
influirà sulla valutazione del progetto.
Il Notebook ed eventuali altri contenuti devono essere consegnati su su Moodle in un unico
archivio compresso in formato zip.

La data pubblicata sul sito si riferisce alla data di consegna del progetto. L’esame si svolge, su
appuntamento, nella settimana successiva alla data di consegna.

Nel caso le dimensioni del DataSet si rivelassero troppo elevate per le risorse computazionali
che lo studente ha a propria disposizione, potete mandate una mail a laura.ricci@unipi.it, per
ricevere un DataSet ulteriormente ridotto.