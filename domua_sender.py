# domua_sender.py (versione reale per DomU)

import mmap
from cffi import FFI

ffi = FFI()

# Carica solo le librerie sicure per DomU (niente libxenctrl)
gnttab = ffi.dlopen("libxengnttab.so")
evtchn = ffi.dlopen("libxenevtchn.so")

ffi.cdef("""
typedef ... xengnttab_handle;
typedef ... xenevtchn_handle;

xengnttab_handle *xengnttab_open(void *logger, unsigned int flags);
int xengnttab_grant_foreign_access(xengnttab_handle *h, int domid, int writable, int *ref);

xenevtchn_handle *xenevtchn_open(void *logger, unsigned int flags);
int xenevtchn_bind_interdomain(xenevtchn_handle *xce, int remote_domid, int remote_port);
int xenevtchn_notify(xenevtchn_handle *xce, int port);
int xenevtchn_unmask(xenevtchn_handle *xce, int port);
int xenevtchn_fd(xenevtchn_handle *xce);
int xenevtchn_close(xenevtchn_handle *xce);
""")

# Configurazione
PAGE_SIZE = 4096
receiver_domid = 1  # <- Cambia questo col DomID di domuB

# 1. Alloca una pagina di memoria
shm = mmap.mmap(-1, PAGE_SIZE)
msg = b"Messaggio da DomU-A" + b"." * (1024 - len("Messaggio da DomU-A"))
shm.write(msg)

# 2. Crea grant table
gnt = gnttab.xengnttab_open(ffi.NULL, 0)
ref = ffi.new("int *")
res = gnttab.xengnttab_grant_foreign_access(gnt, receiver_domid, 1, ref)
if res < 0:
    print("Errore nella creazione del grant ref")
    exit(1)
grant_ref = ref[0]

# 3. Crea event channel
evch = evtchn.xenevtchn_open(ffi.NULL, 0)
port = evtchn.xenevtchn_bind_interdomain(evch, receiver_domid, 0)
if port < 0:
    print("Errore nella creazione dell'event channel")
    exit(1)

# 4. Salva le info su file per DomU-B
with open("/tmp/xen_ipc_info.txt", "w") as f:
    f.write(f"grant_ref={grant_ref}\n")
    f.write(f"port={port}\n")
    f.write(f"msg=Messaggio da DomU-A\n")

# 5. Notifica DomU-B
evtchn.xenevtchn_notify(evch, port)

print(f"Messaggio pronto. Grant ref: {grant_ref}, Event channel: {port}")


