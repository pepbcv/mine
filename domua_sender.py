# domua_sender.py

import mmap
import time
from cffi import FFI

# Inizializza CFFI
ffi = FFI()

# Carica librerie Xen
xen = ffi.dlopen("libxenctrl.so")
gnttab = ffi.dlopen("libxengnttab.so")

# Definizioni semplificate (puoi ignorarle per ora)
ffi.cdef("""
typedef ... xc_interface;
typedef ... xengnttab_handle;

xc_interface *xc_interface_open(void *unused1, void *unused2, unsigned int flags);
xengnttab_handle *xengnttab_open(xc_interface *xch, unsigned int flags);
int xengnttab_grant_foreign_access(xengnttab_handle *h, int domid, unsigned long frame, int writable);
void *xc_map_foreign_range(xc_interface *xch, int domid, int size, int prot, unsigned long mfn);
""")

# 1. Apri interfaccia Xen e grant table
xch = xen.xc_interface_open(ffi.NULL, ffi.NULL, 0)
gnt = gnttab.xengnttab_open(xch, 0)

# 2. Alloca pagina di memoria (4 KB)
PAGE_SIZE = 4096
shm = mmap.mmap(-1, PAGE_SIZE)

# 3. Scrive un messaggio da 1024 byte
msg = b"ciao da DomU-A" + b"." * (1024 - len("ciao da DomU-A"))
shm.write(msg)

# 4. Simula creazione grant ref (verrà implementata più avanti)
grant_ref = 42  # <--- fittizio per ora
receiver_domid = 1  # <--- DomU-B (da sostituire con reale DomID)

# 5. Scrivi grant_ref e domid su un file condiviso
with open("/tmp/xen_ipc_info.txt", "w") as f:
    f.write(f"grant_ref={grant_ref}\n")
    f.write(f"receiver_domid={receiver_domid}\n")

print("Messaggio scritto e info salvata. (grant_ref è simulato)")
