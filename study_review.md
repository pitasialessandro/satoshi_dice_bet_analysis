# Study Review - Funzioni Usate Nel Progetto

Questo file raccoglie le funzioni e i metodi più importanti usati nel progetto SatoshiDice. È pensato come ripasso per la discussione orale: non elenca ogni singolo metodo banale, ma quelli che possono essere chiesti perché fondamentali, ricorrenti o leggermente avanzati.

## 1. Pandas: Lettura, Scrittura E Tipi

### `pd.read_csv()`

Legge un file CSV e lo carica in un `DataFrame`.

Nel progetto è usato per leggere sia i dataset raw (`transactions.csv`, `outputs.csv`, `inputs.csv`, `mapping.csv`) sia gli output intermedi in `outputs/processed/`.

Parametri importanti usati:

- `header=None`: indica che il file non ha intestazione.
- `names=[...]`: assegna nomi alle colonne.
- `usecols=[...]`: legge solo alcune colonne, riducendo memoria e complessità.
- `dtype={...}`: impone il tipo delle colonne.
- `nrows=...`: legge solo le prime righe per sample/debug.
- `chunksize=...`: legge il file a blocchi, utile per file grandi come `mapping.csv`.
- `compression="gzip"`: legge CSV compressi `.csv.gz` quando necessario.

Risposta orale possibile:

```text
Ho usato read_csv con usecols e dtype per controllare memoria e schema dei dataset. I CSV raw non hanno header, quindi i nomi delle colonne vengono assegnati manualmente.
```

### `DataFrame.to_csv()`

Scrive un `DataFrame` su file CSV.

Nel progetto è usato per salvare tutti gli intermedi processati.

Parametri importanti:

- `index=False`: evita di salvare l'indice Pandas come colonna extra.
- `compression="gzip"`: salva file compressi per output grandi.

Risposta orale possibile:

```text
Ho salvato gli intermedi in CSV/CSV.GZ perché sono formati semplici, leggibili e coerenti con il progetto. Uso index=False perché l'indice Pandas non è un dato analitico.
```

### `astype()`

Converte una colonna o un DataFrame a un tipo specifico.

Esempi dal progetto:

```python
known_addresses = known_addresses.astype({"addressId": "int64"})
summary["bet_transactions"] = summary["bet_transactions"].fillna(0).astype("int64")
```

Serve per evitare errori nei merge e per avere colonne numeriche coerenti.

### `pd.to_datetime()`

Converte timestamp numerici o stringhe in date Pandas.

Nel progetto è usato con timestamp UNIX:

```python
pd.to_datetime(df["timestamp"], unit="s")
```

`unit="s"` indica che il timestamp è espresso in secondi.

## 2. Pandas: Selezione, Filtri E Copie

### Filtri booleani

Esempio:

```python
transactions[transactions["isCoinbase"] == 0]
```

Filtra le righe che rispettano una condizione.

Nel progetto è usato per escludere transazioni coinbase, selezionare indirizzi SatoshiDice, filtrare top address, selezionare intervalli validi e altro.

### `.copy()`

Crea una copia esplicita di un DataFrame filtrato.

Esempio:

```python
filtered = df[df["addressId"].isin(top_address_ids)].copy()
```

Serve per evitare ambiguità tra vista e copia e per modificare il sottoinsieme in sicurezza.

Risposta orale possibile:

```text
Uso copy quando filtro un DataFrame e poi aggiungo o modifico colonne. In questo modo evito di modificare accidentalmente il DataFrame originale e riduco warning ambigui di Pandas.
```

### `.loc[]`

Seleziona righe e colonne usando label o condizioni.

Esempio:

```python
simple_tx_ids = tx_counts.loc[condition, "txId"]
```

È utile perché rende esplicito che stiamo selezionando righe tramite condizione e una specifica colonna.

### `.iloc[]`

Seleziona per posizione numerica.

Esempio concettuale:

```python
df.iloc[0]
```

Nel progetto è usato meno di `loc`, ma è importante conoscere la differenza:

- `loc`: label o condizioni.
- `iloc`: posizione intera.

### `.isin()`

Controlla se i valori di una colonna appartengono a un insieme.

Esempio:

```python
outputs[outputs["txId"].isin(simple_tx_ids)]
```

Nel progetto è fondamentale per filtrare righe relative a un set di transazioni o indirizzi.

### `.dropna()` e `.fillna()`

`dropna()` elimina righe con valori mancanti.

`fillna()` sostituisce valori mancanti.

Esempi:

```python
satoshi_addresses.dropna(subset=["addressId"])
summary["bet_transactions"].fillna(0)
```

Nel progetto `dropna` serve per tenere solo indirizzi SatoshiDice mappati; `fillna` serve quando un periodo temporale non ha bet e va contato come zero.

### `.duplicated()`

Individua valori duplicati.

Esempio:

```python
if transaction_metadata["txId"].duplicated().any():
    raise ValueError(...)
```

Nel progetto serve come controllo di qualità: dopo aver filtrato le coinbase, `txId` deve essere unico per poter fare merge sicuri.

## 3. Pandas: Merge, Join E Allineamento Dati

### `.merge()`

Unisce due DataFrame usando una o più chiavi.

Esempi dal progetto:

```python
outputs.merge(known_addresses, on="addressId", how="inner")
inputs.merge(bet_outputs, left_on=["prevTxId", "prevTxpos"], right_on=["betTxId", "betOutputPosition"])
```

Tipi di join usati:

- `inner`: tiene solo righe che matchano da entrambe le parti.
- `left`: tiene tutte le righe a sinistra e aggiunge dati se disponibili.

Parametro importante:

- `validate="many_to_one"` o `validate="one_to_one"`: controlla che il merge abbia la cardinalità attesa.

Risposta orale possibile:

```text
Il merge è stato usato per collegare tabelle diverse tramite chiavi comuni, per esempio txId o addressId. Ho usato validate per intercettare errori logici nel join, come duplicati inattesi.
```

### `.rename()`

Rinomina colonne.

Esempio:

```python
outputs.rename(columns={"amount": "betAmount"})
```

Serve per rendere chiaro il significato di una colonna dopo un merge. Per esempio, `txId` può diventare `betTxId` o `payoutTxId` per evitare ambiguità.

### `.drop()`

Elimina colonne o righe.

Esempio:

```python
satoshi_addresses.drop(columns=["hash"])
```

Nel progetto è usato per rimuovere colonne non più necessarie dopo un merge.

### `pd.concat()`

Concatena Series o DataFrame.

Esempi:

```python
pd.concat([total_counts, bet_counts], axis=1)
pd.concat([input_addresses, change_addresses], ignore_index=True)
```

Con `axis=1` affianca colonne. Con `ignore_index=True` ricrea un indice progressivo.

### `.reset_index()`

Trasforma l'indice in una colonna normale.

Esempio:

```python
df.groupby("addressId").size().reset_index(name="count")
```

Serve dopo `groupby` quando si vuole tornare ad avere una tabella normale, utile per merge e salvataggio CSV.

## 4. Pandas: Groupby E Aggregazioni

### `.groupby()`

Divide il DataFrame in gruppi secondo una o più colonne.

Esempio:

```python
bet_transactions.groupby(["addressId", "diceName"])
```

Nel progetto è usato per:

- contare bet per address;
- calcolare importi totali;
- contare transazioni per periodo;
- calcolare intervalli per ogni address;
- aggregare wallet per chain.

### `.agg()`

Applica aggregazioni multiple e produce colonne nominate.

Esempio:

```python
popularity = bet_transactions.groupby(address_columns, as_index=False).agg(
    bet_count=("txId", "nunique"),
    total_bet_amount_btc=("betAmountBtc", "sum"),
)
```

È molto utile perché rende esplicito cosa rappresenta ogni colonna aggregata.

### `.size()`

Conta quante righe ci sono in ogni gruppo.

Esempio:

```python
transactions.groupby("period").size()
```

Differenza da `count()`: `size()` conta tutte le righe, anche se alcune colonne hanno `NaN`. `count()` conta valori non nulli di una colonna.

### `.nunique()`

Conta valori distinti.

Esempio:

```python
bet_count=("txId", "nunique")
```

Nel progetto è importante perché alcune tabelle sono a granularità output, quindi una stessa transazione può comparire più di una volta. `nunique()` evita di sovrastimare il numero di transazioni.

### `.sum()`, `.mean()`, `.median()`, `.quantile()`

Funzioni statistiche usate nel progetto.

Esempi:

```python
transactions["isCoinbase"].sum()
block_distance.mean()
block_distance.median()
block_distance.quantile(0.95)
```

`quantile(0.95)` restituisce il 95° percentile.

### `.nlargest()`

Seleziona le righe con i valori più grandi in una colonna.

Esempio:

```python
address_popularity.nlargest(3, "bet_count")
```

Nel progetto serve per trovare i top 3 indirizzi SatoshiDice e la chain più lunga.

### `.value_counts()`

Conta la frequenza di ogni valore distinto.

Esempio:

```python
values.value_counts().sort_index()
```

Nel progetto è usato per la distribuzione della distanza payout in blocchi.

### `.sort_values()` e `.sort_index()`

`sort_values()` ordina righe in base a una o più colonne.

`sort_index()` ordina in base all'indice.

Esempi:

```python
df.sort_values(["timestamp", "txId"])
counts.sort_index()
```

Nel progetto ordinare è importante per costruire sequenze temporali e chain.

## 5. Pandas: Time Series

### `.dt.to_period()`

Converte date in periodi temporali.

Esempio:

```python
pd.to_datetime(df["timestamp"], unit="s").dt.to_period("M")
```

Nel progetto serve per raggruppare transazioni per giorno, settimana o mese.

Frequenze usate:

- `D`: day.
- `W`: week.
- `M`: month.
- `h`: hour.

### `pd.PeriodIndex()`

Crea un indice di periodi a partire da stringhe o valori periodici.

Esempio:

```python
pd.PeriodIndex(df["period"], freq="M").to_timestamp()
```

Nel plotting serve perché Matplotlib lavora meglio con timestamp/date vere invece che stringhe tipo `2012-06`.

### `.to_timestamp()`

Converte un periodo in un timestamp.

Esempio:

```python
period.to_timestamp()
```

Serve per visualizzare serie temporali su asse x.

### `pd.period_range()`

Crea una sequenza completa di periodi.

Esempio:

```python
pd.period_range(start, end, freq="D")
```

Nel progetto serve per creare tutti i periodi temporali anche quando alcuni non hanno bet.

### `pd.MultiIndex.from_product()`

Crea un indice multi-livello come prodotto cartesiano.

Esempio:

```python
pd.MultiIndex.from_product([all_periods, top_address_ids], names=["period", "addressId"])
```

Nel progetto serve per avere tutte le combinazioni periodo-address, così i periodi senza bet vengono mostrati come zero.

### `.reindex()`

Allinea un DataFrame o una Series a un nuovo indice.

Esempio:

```python
distribution.reindex(full_index, fill_value=0)
```

Nel progetto serve per riempire con `0` le combinazioni periodo-address mancanti.

### `.shift()`

Sposta i valori di una colonna di una o più posizioni.

Esempio:

```python
previous_timestamp = grouped["timestamp"].shift()
```

Nel progetto serve per confrontare una bet con la bet precedente dello stesso address e calcolare intervalli temporali.

Risposta orale possibile:

```text
Uso shift dentro un groupby per prendere il timestamp della riga precedente nello stesso gruppo. Così l'intervallo viene calcolato tra bet consecutive dello stesso indirizzo e non tra address diversi.
```

### `.diff()` e rolling/expanding

Nel codice finale abbiamo usato `shift()` invece di `diff()`, ma il concetto è simile: `diff()` calcola differenze tra valori consecutivi.

`rolling()` e `expanding()` sono funzioni di time series viste nel corso. Non sono centrali nel codice finale, ma possono essere collegate al tema:

```python
series.rolling(7).mean()
series.expanding().mean()
```

`rolling()` usa una finestra mobile; `expanding()` usa una finestra crescente.

## 6. Pandas: Correlazione E Statistica

### `.corr()`

Calcola la correlazione tra due Series.

Esempi:

```python
points["feeBtc"].corr(points["betAmountBtc"], method="pearson")
points["feeBtc"].corr(points["betAmountBtc"], method="spearman")
```

Pearson misura relazione lineare.

Spearman misura relazione monotona basata sui ranghi.

Nel progetto serve per verificare se c'è relazione tra importo della bet e fee della transazione.

Risposta orale possibile:

```text
Pearson misura correlazione lineare sui valori originali, Spearman lavora sui ranghi ed è più robusta per relazioni monotone e distribuzioni molto asimmetriche.
```

### `.idxmax()`

Restituisce l'indice del valore massimo.

Esempio:

```python
peak = df.loc[df["bet_percentage"].idxmax()]
```

Nel progetto serve per annotare il mese con il picco di percentuale SatoshiDice.

### `.sample()`

Estrae un campione casuale.

Esempio:

```python
df.sample(120_000, random_state=42)
```

Nel progetto è usato nel grafico fee/amount per non plottare milioni di punti. `random_state` rende il campionamento riproducibile.

### `pd.unique()`

Restituisce valori unici preservando l'ordine di apparizione.

Nel progetto serve per estrarre addressId unici nelle chain da mappare con `mapping.csv`.

## 7. Matplotlib: Struttura Dei Grafici

### `plt.subplots()`

Crea figura e assi.

Esempio:

```python
fig, ax = plt.subplots(figsize=(10, 6))
```

Nel progetto è la base di tutti i grafici.

Con più assi:

```python
fig, (ax_count, ax_amount) = plt.subplots(ncols=2, sharey=True)
```

### `ax.bar()` e `ax.barh()`

Creano bar chart verticali e orizzontali.

Usati per:

- transazioni mensili;
- popolarità indirizzi;
- distribuzione lunghezza chain;
- payout distance in blocks.

### `ax.plot()`

Crea un line plot.

Usato per serie temporali, per esempio andamento delle bet nel tempo.

### `ax.scatter()`

Crea uno scatter plot.

Usato per visualizzare relazione tra `betAmountBtc` e `feeBtc`.

### `ax.hist()`

Crea un istogramma.

Usato per distribuzione degli intervalli temporali tra bet consecutive.

Parametri importanti:

- `bins=100`: numero di intervalli dell'istogramma.
- `log=True`: asse y in scala logaritmica per frequenze molto sbilanciate.

### `ax.boxplot()`

Crea un box plot.

Nel progetto è usato per la payout distance in blocks.

Concetti da ricordare:

- linea centrale: mediana;
- box: Q1-Q3;
- IQR: Q3-Q1;
- outlier/flier: punti oltre `1.5 * IQR` dai quartili.

Parametri usati:

- `showfliers=True`: mostra outlier;
- `patch_artist=True`: permette di colorare il box;
- `boxprops`, `medianprops`, `flierprops`: personalizzazione estetica.

### `ax.twinx()`

Crea un secondo asse y che condivide lo stesso asse x.

Nel progetto è usato per mostrare nello stesso grafico:

- numero totale di transazioni Bitcoin;
- percentuale di transazioni SatoshiDice.

Risposta orale possibile:

```text
Ho usato twinx perché le due variabili hanno scale diverse: una è un conteggio assoluto, l'altra è una percentuale. Con due assi y posso confrontare visivamente gli andamenti senza normalizzare i dati.
```

### `ax.set_yscale("log")` e `ax.set_xscale("log")`

Impostano scale logaritmiche.

Usate quando i dati sono molto sbilanciati o coprono ordini di grandezza diversi.

Nel progetto:

- y log per conteggi molto sbilanciati;
- x log per importi di bet nello scatter fee/amount.

Nota importante: la scala log non può rappresentare direttamente valori `0` sull'asse interessato.

### `ax.annotate()`

Aggiunge annotazioni testuali al grafico.

Usato per:

- indicare il picco mensile SatoshiDice;
- indicare la longest chain;
- annotare mediana, Q1, Q3, p95 e massimo nel box plot.

### `ax.legend()` e `get_legend_handles_labels()`

`legend()` mostra legenda.

`get_legend_handles_labels()` recupera elementi della legenda da assi diversi.

Nel grafico con `twinx()` serve per unire le legende dei due assi.

### `ax.grid()`

Mostra griglia sul grafico.

Nel progetto è usato per rendere più leggibili valori e confronti.

### `fig.tight_layout()`

Ottimizza spazi tra elementi del grafico.

Serve per evitare sovrapposizioni tra titolo, assi, label e legenda.

### `fig.savefig()`

Salva la figura su file.

Parametri usati:

- `dpi=160`: risoluzione;
- `bbox_inches="tight"`: ritaglia margini inutili.

### `fig.clear()`

Libera la figura dopo averla salvata.

Utile quando si generano molti grafici in uno script.

### `matplotlib.use("Agg")`

Imposta backend non interattivo.

Nel progetto è usato in `build_figures.py` per generare PNG senza aprire finestre grafiche.

### `mdates.MonthLocator()` e `mdates.DateFormatter()`

Gestiscono tick e formato delle date sull'asse x.

Esempio:

```python
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
```

Servono per rendere leggibile l'asse temporale.

### `fig.autofmt_xdate()`

Ruota e formatta automaticamente le date sull'asse x.

Nel progetto è usato per evitare sovrapposizione delle label temporali.

## 8. NetworkX: Grafo Delle Simple-Bet Chains

### `nx.DiGraph()`

Crea un grafo diretto.

Nel progetto ogni nodo è una simple bet identificata da `txId`. Ogni arco indica che il change output di una bet viene speso come input della bet successiva.

Risposta orale possibile:

```text
Uso un grafo diretto perché la relazione tra le bet ha una direzione temporale e UTXO: una bet precedente genera un output di change, che viene speso da una bet successiva.
```

### `graph.add_nodes_from()`

Aggiunge più nodi al grafo.

Esempio:

```python
graph.add_nodes_from(simple_bets["txId"])
```

Nel progetto i nodi sono solo txId, senza metadati, per mantenere il grafo semplice.

### `graph.add_edges_from()`

Aggiunge più archi al grafo.

Esempio:

```python
graph.add_edges_from(edges[["sourceTxId", "targetTxId"]].itertuples(index=False, name=None))
```

Ogni arco è `sourceTxId -> targetTxId`.

### `itertuples()`

Itera sulle righe del DataFrame restituendo tuple.

Nel progetto è usato per passare archi a NetworkX in modo semplice ed efficiente.

Con `index=False, name=None`, produce tuple pure come:

```python
(sourceTxId, targetTxId)
```

### Dizionari `child_by_source` e `parent_by_target`

Non sono funzioni NetworkX, ma sono centrali nella logica.

```python
child_by_source = dict(edges[["sourceTxId", "targetTxId"]].itertuples(index=False, name=None))
parent_by_target = dict(edges[["targetTxId", "sourceTxId"]].itertuples(index=False, name=None))
```

Servono per seguire linearmente la chain:

- `child_by_source`: data una bet, trova la bet successiva.
- `parent_by_target`: permette di trovare le bet senza parent, cioè gli start delle chain.

### Perché non usare `weakly_connected_components()`?

NetworkX offre funzioni per trovare componenti connesse, ma nel progetto abbiamo scelto una logica più spiegabile:

1. trova nodi senza parent;
2. segue il child finché la chain finisce;
3. salva lunghezza, start, end e durata.

Questo funziona perché una simple bet ha un input e un change output, quindi la struttura attesa è lineare.

## 9. Selenium E WalletExplorer

### `webdriver.Chrome()`

Avvia un browser Chrome controllato da Selenium.

Nel progetto è usato per visitare WalletExplorer.

Esempio:

```python
driver = webdriver.Chrome(options=options)
```

### `Options()` e `options.add_argument()`

Configurano Chrome.

Opzioni usate:

```python
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
```

`--headless=new` avvia Chrome senza finestra grafica.

### `driver.get(url)`

Apre una pagina web.

Nel progetto si visita direttamente:

```text
https://www.walletexplorer.com/address/{address}
```

### `WebDriverWait()`

Aspetta fino a quando una condizione diventa vera o scade il timeout.

Esempio:

```python
WebDriverWait(driver, wait_seconds).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
)
```

Serve perché le pagine web possono richiedere tempo per caricarsi.

### `expected_conditions` / `EC.presence_of_element_located()`

Condizione Selenium che aspetta la presenza di un elemento nel DOM.

Nel progetto si aspetta il `body`, così sappiamo che la pagina è stata caricata almeno a livello base.

### `By.CSS_SELECTOR`

Indica che la ricerca degli elementi avviene tramite selettore CSS.

Esempi usati:

```python
driver.find_element(By.CSS_SELECTOR, "span.wallet_renamer_item")
wallet_item.find_element(By.CSS_SELECTOR, "span.wallet_name")
```

### `find_element()`

Trova il primo elemento che corrisponde al selettore.

Nel progetto serve per trovare:

- container wallet: `span.wallet_renamer_item`;
- nome wallet: `span.wallet_name`;
- link wallet: `a`.

Se l'elemento non esiste, solleva `NoSuchElementException`.

### `get_attribute()`

Legge il valore di un attributo HTML.

Esempi:

```python
wallet_item.get_attribute("data-wallet-id")
wallet_link.get_attribute("href")
```

Nel progetto estrae wallet id e URL del wallet.

### `.text`

Restituisce il testo visibile di un elemento.

Esempio:

```python
wallet_name.text
```

Nel progetto estrae il nome mostrato del wallet.

### `NoSuchElementException` e `TimeoutException`

Eccezioni Selenium gestite nel progetto.

- `NoSuchElementException`: elemento non trovato, per esempio address senza wallet visibile.
- `TimeoutException`: pagina o elemento non caricato entro il timeout.

Gestirle è importante per non interrompere tutto lo scraping al primo errore.

### `driver.quit()`

Chiude il browser e libera risorse.

Nel progetto è dentro un blocco `finally`, così viene eseguito anche se lo scraping fallisce.

### `sleep()`

Pausa tra richieste.

Nel progetto è usato con valore basso (`0.2` secondi), ma può essere aumentato in caso di rate limit.

### Cache CSV

Il progetto usa una cache semplice:

```python
walletexplorer_address_wallets.csv
```

Prima di fare scraping, controlla se un address è già presente con `lookupStatus` valido. Questo evita richieste duplicate e permette di riprendere lo scraping se viene interrotto.

## 10. Funzioni Python E Strutture Dati Ricorrenti

### `dict()`

Converte coppie chiave-valore in dizionario.

Esempio:

```python
child_by_source = dict(edges[["sourceTxId", "targetTxId"]].itertuples(index=False, name=None))
```

Serve per lookup veloci `sourceTxId -> targetTxId`.

### `set()`

Struttura dati che contiene valori unici.

Nel progetto è usata per:

- evitare duplicati;
- controllare membership velocemente;
- tenere traccia dei nodi visitati nelle chain;
- controllare address già presenti in cache.

### `zip()`

Combina due sequenze elemento per elemento.

Esempio:

```python
timestamp_by_tx = dict(zip(simple_bets["txId"], simple_bets["timestamp"]))
```

Crea un dizionario `txId -> timestamp`.

### `enumerate()`

Itera su una sequenza restituendo indice e valore.

Esempio:

```python
for chain_rank, chain in enumerate(chains.itertuples(index=False), start=1):
```

Nel progetto serve per assegnare rank alle chain.

### `Path`

Classe di `pathlib` per gestire percorsi file in modo pulito.

Esempi:

```python
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR / "bet_transactions.csv.gz"
```

È più leggibile e portabile rispetto a concatenare stringhe manualmente.

### `.exists()`

Controlla se un file o directory esiste.

Nel progetto è usato per cache e per generare figure solo se l'output processato esiste.

### `.mkdir(parents=True, exist_ok=True)`

Crea directory se non esistono.

`parents=True` crea anche directory intermedie.

`exist_ok=True` evita errore se la directory esiste già.

### `json.dump()`

Scrive un dizionario Python in formato JSON.

Nel progetto salva `identification_report.json`.

### `argparse.ArgumentParser()`

Gestisce parametri da riga di comando.

Nel progetto è usato negli script con opzioni sample, mentre lo script WalletExplorer è volutamente hardcoded per `TOP_H = 3`.

### `print(..., flush=True)`

Stampa messaggi e forza lo svuotamento del buffer.

È utile negli script lunghi perché mostra subito l'avanzamento.

## 11. Funzioni Specifiche Del Progetto Da Saper Spiegare

### `identify_satoshi_bet_outputs()`

Identifica output verso indirizzi SatoshiDice noti.

Logica:

1. prende output blockchain;
2. prende addressId SatoshiDice mappati;
3. fa merge su `addressId`;
4. ottiene le righe che rappresentano bet verso SatoshiDice.

### `build_bet_transactions()`

Aggancia metadati transazionali agli output di bet.

Logica:

1. filtra coinbase;
2. controlla duplicati txId;
3. merge con transazioni;
4. aggiunge fee in BTC.

### `compute_bet_percentage_over_time()`

Calcola la percentuale di transazioni SatoshiDice nel tempo.

Formula:

```text
bet_percentage = bet_transactions / total_transactions * 100
```

### `compute_address_popularity()`

Calcola popolarità degli indirizzi SatoshiDice tramite:

- numero di bet uniche;
- totale BTC puntati.

### `match_payout_transactions()`

Collega bet e payout usando la relazione UTXO:

```text
inputs.prevTxId / inputs.prevTxpos -> bet_transactions.txId / bet_transactions.position
```

### `compute_top3_bet_intervals()`

Calcola intervalli temporali tra bet consecutive per i top 3 address.

Usa `groupby` e `shift` per confrontare ogni bet con quella precedente dello stesso address.

### `build_simple_bets()`

Identifica simple bet per la chain analysis.

Definizione usata:

- 1 input;
- 2 output totali;
- 1 output verso l'indirizzo SatoshiDice selezionato;
- 1 output di change.

### `build_simple_bet_edges()`

Crea archi tra simple bet:

```text
sourceTxId/changeOutputPosition -> target.inputPrevTxId/inputPrevTxpos
```

In output salva solo:

```text
sourceTxId, targetTxId
```

### `build_simple_bet_chain_summaries()`

Costruisce il grafo diretto e ricostruisce le chain lineari.

Per ogni chain salva:

- lunghezza;
- tx iniziale;
- tx finale;
- timestamp inizio/fine;
- durata.

### `build_top_chain_members()`

Ricostruisce tutte le transazioni appartenenti alle top chain seguendo gli archi `sourceTxId -> targetTxId`.

Serve per preparare l'analisi WalletExplorer.

### `build_top_chain_addresses()`

Estrae gli address utente delle top chain, combinando:

- `inputAddressId`;
- `changeAddressId`.

Poi li mappa a indirizzi Bitcoin testuali tramite `mapping.csv`.

### `scrape_wallet_for_address()`

Visita WalletExplorer per un address e prova a estrarre wallet id, wallet name e wallet URL.

### `summarize_chain_wallets()`

Aggrega risultati WalletExplorer per chain.

Produce:

- address totali;
- address risolti;
- wallet distinti;
- wallet dominante;
- quota del wallet dominante;
- conclusione interpretativa.

## 12. Frasi Utili Per L'Orale

### Pandas

```text
Ho usato Pandas per costruire una pipeline tabellare: lettura typed dei CSV, filtri, merge tra tabelle blockchain, groupby e aggregazioni per produrre output intermedi riutilizzabili.
```

### Merge UTXO

```text
La relazione UTXO viene ricostruita collegando gli input alle uscite precedenti tramite la coppia prevTxId/prevTxpos. Questo permette di identificare payout e catene di change.
```

### Time series

```text
Per le analisi temporali converto i timestamp UNIX in periodi Pandas e poi raggruppo per giorno, settimana o mese.
```

### Grafici

```text
Uso grafici diversi in base al tipo di informazione: line plot per andamento temporale, bar chart per confronti, scatter plot per correlazione, histogram per distribuzioni, box plot per mostrare quartili e outlier.
```

### NetworkX

```text
Uso NetworkX per rappresentare le simple bets come grafo diretto: i nodi sono transazioni e gli archi indicano che il change output di una bet viene speso dalla bet successiva.
```

### Selenium

```text
Uso Selenium perché WalletExplorer è una pagina web da interrogare in modo automatico tramite browser. In questo caso visito direttamente la pagina address e leggo dal DOM il wallet cluster assegnato dal sito.
```

### WalletExplorer

```text
WalletExplorer fornisce un clustering esterno degli address. Se tutti o quasi tutti gli address di una chain appartengono allo stesso wallet cluster, questo rafforza l'ipotesi che la chain sia controllata dallo stesso soggetto. Se ci sono più cluster, bisogna interpretare il risultato con prudenza perché il mancato clustering non implica necessariamente proprietari diversi.
```
