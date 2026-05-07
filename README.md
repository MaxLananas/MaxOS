# 🖥️ MaxOS — Bare Metal x86 OS

> Développé automatiquement par **MaxOS AI v18.0**

## 📊 État actuel

| Métrique | Valeur |
|---|---|
| 🎯 Score | **35/100** |
| 📈 Niveau | desc |
| 📁 Fichiers | 121 |
| 📝 Lignes | 3,021 |
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

- bootloader fonctionnel (boot.asm)
- chargement du kernel en 0x1000:0x0000
- mode 32 bits activé
- IDT initialisée (idt.c/idt.h)
- ISR manuels (isr.asm) sans macros
- IRQ et PIC configurés (irq.asm/irq.c)
- Gestion des exceptions (exceptions.c)
- Gestion des fautes (fault_handler.c)
- PIT Timer initialisé (timer.c)
- Clavier PS/2 fonctionnel (keyboard.c)
- Écran VGA basique (screen.c/screen.h)
- Terminal texte (terminal.c)
- Gestion mémoire basique (pmm.c/vmm.c)
- Paging activé (paging.c)
- Heap basique (heap.c)
- VFS et FAT32 (fs/fat32.c)
- Souris PS/2 (mouse.c)
- GUI basique (ui.c/widget.c)
- Applications (about.c/notepad.c/sysinfo.c/terminal.c)
- Entrées/sorties bas niveau (io.h)
- Linker script fonctionnel (linker.ld)
- Makefile complet avec règles de build

## 🚧 En développement

- Pas de gestion des interruptions système (syscall)
- Pas de multitâche (scheduler vide)
- Pas de gestion des exceptions matérielles avancées (MCE, HPET)
- Pas de gestion des périphériques PCI/USB avancée
- Pas de système de fichiers complet (seulement FAT32 basique)
- Pas de gestion des processus utilisateur
- Pas de protection mémoire avancée (SMAP/SMEP)
- Pas de gestion des interruptions APIC au lieu de PIC
- Pas de support ACPI pour la gestion de l'énergie
- Pas de gestion des timers avancés (HPET)
- Pas de support des disques ATA avancé (DMA)
- Pas de gestion des erreurs matérielles (PCI, MCE)
- Pas de système de logging structuré
- Pas de gestion des signaux
- Pas de support des extensions CPU (SSE, MMX)
- Pas de gestion des interruptions NMI
- Pas de support des périphériques modernes (NVMe, SATA AHCI)
- Pas de gestion des interruptions virtuelles (VT-x)
- Pas de support des systèmes de fichiers autres que FAT32
- Pas de gestion des permissions utilisateur

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
