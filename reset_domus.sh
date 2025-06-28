#!/bin/bash

echo "Fermo le VM se sono attive..."
sudo xl destroy domuA 2>/dev/null
sudo xl destroy domuB 2>/dev/null

echo "Ripristino immagini disco..."
sudo cp /var/lib/xen/images/debian-domuA.clean.img /var/lib/xen/images/debian-domuA.img
sudo cp /var/lib/xen/images/debian-domuB.clean.img /var/lib/xen/images/debian-domuB.img

echo "Avvio le VM da zero..."
sudo xl create -c /etc/xen/domuA.cfg &
sudo xl create -c /etc/xen/domuB.cfg &

echo "Ripristino completato."
