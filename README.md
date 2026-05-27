# 🖥️ MaxOS — Bare Metal x86 OS

> Développé automatiquement par **MaxOS AI v18.0**

## 📊 État actuel

| Métrique | Valeur |
|---|---|
| 🎯 Score | **35/100** |
| 📈 Niveau | desc |
| 📁 Fichiers | 161 |
| 📝 Lignes | 3,188 |
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
- IDT et ISR implémentés (isr.asm, idt.c)
- Gestion des exceptions (fault_handler.c)
- Gestion des IRQ (irq.asm, irq.c)
- PIT Timer (timer.c)
- Clavier PS/2 (keyboard.c)
- Écran VGA (screen.c, drivers/screen.h)
- Terminal basique (terminal.c)
- GDT et paging (paging.c)
- Heap basique (heap.c)
- VFS et FAT32 (vfs.c, fat32.c)
- Gestion des processus (process.c)
- SMP (smp.c)
- GUI basique (ui.c, widget.c)
- ATA (ata.c)
- PCI (pci.c)
- USB (usb.c)
- Souris (mouse.c)
- Makefile fonctionnel
- Linker script (linker.ld)
- Outils de debug (log.c)

## 🚧 En développement

- Gestion avancée de la mémoire (PMM/VMM incomplet)
- Système de fichiers complet (FAT32 limité)
- Multitâche préemptif (schedule.c minimaliste)
- Gestion des syscalls (syscall.c vide)
- Support ACPI (nécessaire pour SMP avancé)
- Gestion des interruptions APIC (PIC obsolète)
- SMP réel (smp.c minimaliste)
- Gestion des exceptions avancées (MCE, etc.)
- Optimisation des drivers (ATA/USB basiques)
- Sécurité mémoire (pas de protection utilisateur)
- Gestion des périphériques modernes (NVMe non utilisé)
- Tests unitaires (aucun)
- Documentation technique (0 commentaires)
- Optimisation des performances (pas de profiling)
- Gestion des erreurs système (pas de panic propre)

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
