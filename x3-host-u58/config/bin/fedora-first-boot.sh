#!/bin/sh
# U34 2026-11-16 (Derrick t1852u): keep Fedora first in UEFI BootOrder; Windows/firmware may reorder it.
F=$(efibootmgr | awk '/\* Fedora/{print substr($1,5,4); exit}')
[ -n "$F" ] || exit 0
CUR=$(efibootmgr | awk '/^BootOrder/{print $2}')
case "$CUR" in "$F"*) exit 0;; esac
NEW="$F,$(echo "$CUR" | tr ',' '\n' | grep -v "^$F$" | paste -sd,)"
efibootmgr -o "$NEW" >/dev/null && logger -t fedora-first "BootOrder $CUR -> $NEW"
