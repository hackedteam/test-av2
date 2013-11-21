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
    build:

        class AgentBuild:
            __init__(self, backend, frontend=None, platform='windows', kind='silent', ftype='desktop', blacklist=[], param = None)

            execute_elite():
                execute_scout()
                _upgrade_elite(instance)
                sleep(25 *60)
                if _check_elite(instance):
                    _uninstall(instance)

            execute_scout():
                _execute_pull()
                _execute_build()
                sleep(6 minutes)
                for tries in range(10):
                    _trigger_sync()
                    instance = self._check_instance(ident)
                    _click_mouse
                 return instance

            execute_pull():
                mkdir 'build'
                create_new_factory()
                _build_agent(factory_id, meltfile)
                (spacial cases for windows/silent)
                if exploit_:
                    u = urllib2.urlopen(url)

        execute_agent(args, level, platform):
            if not internet_checked and internet_on():
                exit
            vmavtest = AgentBuild(args.backend, args.frontend,
                       platform, args.kind, ftype, args.blacklist, args.param)
            vmavtest.create_user_machine()
            action = {"elite": vmavtest.execute_elite, "scout": vmavtest.execute_scout, "pull": vmavtest.execute_pull}
            action[level]()

        pull(args):
            if args.platform == "all": for f in args.platform_type.keys():
            execute_agent(args, "pull", platform)
        scout(args):
            execute_agent(args, "scout", args.platform)
        elite(args):
            execute_agent(args, "elite", args.platform)
        clean(args):
            deletes targets
        build(action, platform, kind, backend, frontend, params):
            args = Args( action, platform:=platforms, kind:=[silent,melt], backend, frontend, params, blacklist=[...], platform_type:=[desktop, mobile] )
            case action:
               pull(args)
               scout(args)
               elite(args)
               clean(args) // deletes targets
               internet(args) // checks internet on
               test(args) // tasklist
        main(argv):
            action, platform, kind, backend, frontend, params = argv
            platforms = [android, blackberry, exploit, exploit_docx, exploit_ppsx, exploit_web, ios, linux, osx, windows]
            build(action, platform, kind, backend, frontend, params)


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

def class command_STARTAGENT extends command:
  def __init__(vmname):

  # server side, overloaded
  def send(args):
    return "+CMD STARTAGENT"

  # client side, overloaded
  def receive(sent):
    return "+SUCCESS STARTAGENT"

  # server side, overloaded
  def parse_results(received):

  def unit_test():
    parse_results(receive(send(...))) == OK


def class command_PUSH extends command:
  def __init__(vmname):

  # server side, overloaded
  def send(args):
    filename = args[0]
    content = bin2hex(file.read(filename))
    return "+CMD PUSH %s %s" % filename, content

  # client side, overloaded
  def receive(sent):
    filename = sent[0]
    hexcontent = sent[1]
    file.open(filename).write(hex2bin(hexcontent)
    return "+SUCCESS PUSH"

  # server side, overloaded
  def parse_results(received):

  def unit_test():
    parse_results(receive(send(...))) == OK

def class command:
  def send(args):
    pass
  def server():
    redis = redis.open()
    redis.publish(send(args))
    received = redis.read()
    parse_results(received)

  def client():
    redis = redis.open()
    sent = redis.read()
    receive(sent)


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




