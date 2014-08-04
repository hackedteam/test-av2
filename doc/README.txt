

Prerequisiti:
MAC:
    brew install libyaml
    sudo easy_install redis pyyaml pysphere mock
WINDOWS:
    ez_setup
    c:\python27\scripts\easy_install redis pyyaml pysphere mock


    - REPORTLEVEL:
           - CHECK_STATIC: TECH
           - BUILD: EXECUTIVE

    - ON_ERROR: continue

    - REPORT: "windows silent"
        - BUILD: [ elite, windows, silent ]

    - REPORT: "static windows"
        - CHECK_STATIC: [ AVAgent/assets/* ]
        - BUILD: [ pull, windows, silent ]

    - REPORT: "static desktop"
        - BUILD: [ pull, linux, silent ]
        - BUILD: [ pull, osx, silent ]

    - REPORT: "static mobile"
        - BUILD: [ pull, android, silent ]
        - BUILD: [ pull, blackberry, silent ]
        - BUILD: [ pull, ios, silent ]

    - ON_ERROR: break

    - REPORT: "windows melt"
        - PUSH: [ melted.app ]
        - BUILD: [ elite, windows, melt ]



 - aprire il canale redis
    - manda STARTAGENT
  - unzip dei file accessori (tra cui la conf?)
  - ricevere i comandi
  - eseguire i comandi
    - update os/av
    - push
    - silent / melt
    - save file (con un payload)
  - restuire i risultati dei comandi

----------------------------

AVMaster
  - istanziare il demone db
  - gestire redis

  - comandare le vm
    - accendere, spegnere, monitare vm
    - riceve START da publish.py, che e' installato nativo sulle VM
    - push di avagent e dei file accessori (zipped)
    - eseguire remotamente avagent
      - ricezione STARTAGENT
    - inoltrare i comandi ad avagent
      - TRAMITE REDIS
    - raccogliere i risultati di avagent
    - quando riceve + END oppure va in timeout, considera chiuso il lavoro sulla vm

  - mandare mail di report

AVAgent
  - aprire il canale redis
    - manda STARTAGENT
  - unzip dei file accessori (tra cui la conf?)
  - ricevere i comandi
  - eseguire i comandi
    - update os/av
    - push
    - silent / melt
    - save file (con un payload)
  - restuire i risultati dei comandi


All'accensione della VM:
- master <-> agent
  -> COMMAND [name] [arguments]
  <- ack(+SUCCESS/+FAILED) / nack (+ERROR) |> +ENDCOMMAND

Commands:
results: +SUCCESS: success, +ERROR: system, components, +FAILED: AV detecion

STARTAGENT  | +SUCCESS STARTAGENT
SET_SERVER (backend,frontend)
SET_PLATFORM (platform)
SET_BLACKLIST (avs)
PUSH (namefile, content) | +SUCCESS PUSH
BUILD (kind, args)
  BUILD_SILENT
  BUILD_MELT(filehost)
STATICDETECTION (dir) | +SUCCES / +FAILED
EXECUTE_SIMPLE
EXECUTE_SCOUT // aspetta n minuti, muove mouse, aspetta sync
UPGRADE_ELITE // set upgrade, aspetta upgrade, check bl
UNINSTALL


Per ogni comando esiste una classe nella format command_COMMANDNAME
Es:
command_STARTAGENT

Segue una descrizione di un piano di realizzazione di una rete di macchine virtuali atte alla verifica di visibilità delle build RCS su un insieme significativo di Antivirus e Antimalware.

Obiettivo:
 - una VM per antivirus
 - ogni VM deve poter aggiornare, in momenti specificati della giornata, probabilmente di notte, OS e AV, possibilmente automaticamente
 - al di fuori del periodo dell'aggiornamento le VM non potranno mai connettersi ad internet.
 - le VM siano raggiungibili via RDP dagli sviluppatori, dalla rete 172.20.20.0/24
 - le VM possano raggiungere il server (MINOTAURO) posto sulla rete 192.168.100.100/24
 - le procedure di aggiornamento e di test possano essere realizzate in sicurezza in automatico

Proposta:
 - Ci sia una macchina chiamata AVMaster che svolga le funzioni di:
       * gateway per le macchine AV, via NAT
       * AVUpdate per forzare l'update dell'OS e del AV delle VM
       * AVTestDispatcher per eseguire automaticamente i test sulle macchine AV.
 - Ogni VM abbia due interfacce:
	* DEV: per connettersi al server RCS e che ci consenta di connetterci via rtp. Indirizzi nella classe 192.168.100, a partire da 110. Non è specificato il Default Gateway, pertanto da questa interfaccia le VM non potranno in alcun modo raggiungere internet.
	* AV: per connettersi al AVMaster che ne è Default Gateway, così da poter raggiungere Internet.
 - Siccome le VM per raggiungere Internet sfruttano il NAT offerto da AVMaster, sull'interfaccia AV, questo può, con sicurezza, disabilitare la raggiungibilita' di tutte le VM in un comando solo.

Realizzazione:
Siccome occorre avere le VM pronte nel più breve tempo possibile, abbiamo speso un paio d'ore per realizzare la struttura di AVMaster e del templare delle VM sul VSphere, così da consentire la testabilita' manuale degli AV in una prima fase, ma permettere anche lo sviluppo in tempi brevi degli step successivi.

La macchina AVMaster (DEV 172.20.20.167, AV 10.0.20.2 ) è una Linux Ubuntu, dispone di due cartelle di script ShoreWall, una di nome "natenabled", l'altra "natdisabled".

La macchina Template (DEV 192.168.100.110, AV 10.0.20.61) è Windows 7 enterprise N.
 - Creata cartella c:/SHARE per la condivisione dei file
 - Aggiunte le rotte statiche per raggiungere i DNS e
	route -p ADD 172.20.20.0 MASK 255.255.255.0 192.168.100.1
	route -p ADD 192.168.200.0 MASK 255.255.255.0 192.168.100.1

  elevate -c route -p DELETE 192.168.200.0 MASK 255.255.255.0 192.168.100.1
  elevate netsh interface ip set dns name="Local Area Connection 2" static None

Matteo sta cominciando a migrare le VM esistenti secondo questo paradigma e a realizzare quelle mancanti, per arrivare ad avere, se ce la facciamo, entro domani o dopo, tutte e 20 le VM richieste.
SERVE AIUTO PER L'INSTALLAZIONE, CERCHIAMO VOLONTARI.


Gli script:
(da fare)

AVUpdate.py (eseguito su AVMaster)
   switch network ON
   for $vm in VMList:
	revert $vm lastgoodsnaphot
	start $vm
	execute $vm updateOS
	(sleep 2h)
	reboot $vm
	snapshot $vm lastgoodsnaphot
	stop $vm
  switch network OFF

AVTestDispatcher.py
   switch network OFF
   for $vm in VMList:
	start $vm
	upload $vm testAV
        execute $vm testAV

TestAV.py
   if ping gmail? return
   delete target $target
  create target $target
  create factory $factory
  copy config $factory
  build silent/melted
  execute silent/melted
  sleep  / auto mouse
  verify $target contains instances


Dipendenze:
  - Flask (with Flask-SQLAlchemy)
  - Redis
  - SQLite / MySQL / PostgreSQL Database (via Flask-SQLAlchemy) and Python APIs




