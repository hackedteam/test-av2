
from multiprocessing import Pool
from time import sleep

# metodo da eseguire in N contest distinti, uno per vm (il nome passato per argomento)
# i risultati vengono restituiti con return
def vmplay(vmname):
    sleep(1)
    return "executed: %s" % vmname

#  a pool of worker processes
po = Pool(200)

# vettore dei nomi delle vm
vmnames = [ "vm%d" % n for n in range(200) ]

# lancio di un processo per ogni vm, asincrono, usando una map
res = po.map_async(vmplay,((i) for i in vmnames))

#i risultati vengono raccolti in un array
print res.get()

#-------------------------------------------------------------------#
#esempio di map
def double(x):
    return x*2
 
map( double, range(10) )
#[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# eseguendo la map su vmnames, ci impega 200 secondi, per questo si usa map_async
r = map(vmplay, ["ciao","mondo"])
print r

# il lambda e' una funzione anonima, in questo caso identica a double
print map( lambda x: 2*x, range(10) )