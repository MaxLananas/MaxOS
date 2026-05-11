# 🖥️ MaxOS — Bare Metal x86 OS

> Développé automatiquement par **MaxOS AI v18.0**

## 📊 État actuel

| Métrique | Valeur |
|---|---|
| 🎯 Score | **35/100** |
| 📈 Niveau | desc |
| 📁 Fichiers | 125 |
| 📝 Lignes | 3,010 |
| 💾 os.img | ❌ Non bootable |
| 🔐 Boot sector | os.img absent |

## 🚀 Lancer MaxOS

```bash
# Compiler
make

# Lancer dans QEMU
qemu-system-i386 -drive format=raw,file=os.img,if=floppy -boot a -vga std -k fr -m 32
```

## ✅ Fonctionnalités présentes

- Bootloader fonctionnel (boot.asm)
- IDT initialisée (idt.c/idt.h)
- ISR/IRQ gérés (isr.asm/irq.asm)
- Gestion des exceptions (fault_handler.c)
- PIT Timer configuré (timer.c)
- Clavier PS/2 fonctionnel (keyboard.c)
- Écran VGA initialisé (screen.c/screen.h)
- Terminal basique (terminal.c/terminal.h)
- Gestion mémoire basique (pmm.c/vmm.c)
- Paging activé (paging.c)
- Heap basique (heap.c)
- FAT32 support (fat32.c)
- VFS (vfs.c)
- PCI basique (pci.c)
- ATA basique (ata.c)
- Souris PS/2 (mouse.c)
- GUI basique (ui.c/widget.c)
- Applications (about.c/notepad.c/sysinfo.c/terminal.c)
- Makefile fonctionnel
- Linker script (linker.ld)

## 🚧 En développement

- Pas de gestion SMP (processeurs multiples)
- Pas de gestion des interruptions APIC (seulement PIC)
- Pas de gestion des interruptions HPET (seulement PIT)
- Pas de gestion des interruptions USB (seulement PS/2)
- Pas de gestion des interruptions réseau
- Pas de gestion des interruptions SATA avancée
- Pas de gestion des interruptions ACPI
- Pas de gestion des interruptions RTC
- Pas de gestion des interruptions CMOS
- Pas de gestion des interruptions FPU
- Pas de gestion des interruptions SSE
- Pas de gestion des interruptions NMI
- Pas de gestion des interruptions SMI
- Pas de gestion des interruptions IPI
- Pas de gestion des interruptions TLB shootdown
- Pas de gestion des interruptions cache
- Pas de gestion des interruptions thermal
- Pas de gestion des interruptions power management
- Pas de gestion des interruptions multi-core
- Pas de gestion des interruptions vectorisés

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
