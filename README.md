# 🖥️ MaxOS — Bare Metal x86 OS

> Développé automatiquement par **MaxOS AI v18.0**

## 📊 État actuel

| Métrique | Valeur |
|---|---|
| 🎯 Score | **35/100** |
| 📈 Niveau | desc |
| 📁 Fichiers | 144 |
| 📝 Lignes | 3,128 |
| 💾 os.img | ✅ Bootable |
| 🔐 Boot sector | Signature 0xAA55 ✅ | 1474560 bytes |

## 🚀 Lancer MaxOS

```bash
# Compiler
make

# Lancer dans QEMU
qemu-system-i386 -drive format=raw,file=os.img,if=floppy -boot a -vga std -k fr -m 32
```

## ✅ Fonctionnalités présentes

- Bootloader fonctionnel (boot.asm)
- GDT et IDT initialisées
- ISR et IRQ configurés (isr.asm, irq.asm)
- Gestion des exceptions (fault_handler.c)
- PIT Timer initialisé (timer.c)
- Clavier PS/2 fonctionnel (keyboard.c)
- Écran VGA basique (screen.c, drivers/screen.h)
- Terminal texte (terminal.c, drivers/terminal.h)
- Gestion mémoire physique (pmm.c)
- Paging activé (paging.c)
- Heap basique (heap.c)
- SMP support (smp.asm, smp.c)
- VFS basique (vfs.c, fs/fat32.c)
- Applications basiques (about, notepad, sysinfo)
- GUI basique (ui.c, widget.c)
- Souris PS/2 (mouse.c)
- PIC remappé (pic.c)
- Ports E/S (io.h)

## 🚧 En développement

- Support du multitâche préemptif (schedule.c incomplet)
- Gestion des processus (process.c vide)
- Système de fichiers complet (FAT32 limité)
- Gestion des interruptions système (syscall.c vide)
- Gestion avancée de la mémoire (VMM incomplet)
- Support des disques ATA (ata.c minimaliste)
- Gestion des erreurs matérielles (MCE non implémenté)
- Optimisation des performances (pas de cache TLB)
- Sécurité mémoire (pas de protection des pages)
- Support des périphériques USB (usb.c minimaliste)

## 📈 Progression


## 🏗️ Architecture

```
MaxOS/
├── boot/          # Bootloader NASM
├── kernel/        # Kernel C + ASM
├── drivers/       # Pilotes (screen, keyboard, vga)
├── apps/          # Applications (terminal)
└── ai_dev/        # Bot IA développeur
```

## 🤖 Bot IA

Aucun historique disponible.

---
*Mis à jour automatiquement par MaxOS AI v18.0*
