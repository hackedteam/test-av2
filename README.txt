
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






