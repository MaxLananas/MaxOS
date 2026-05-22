# 🖥️ MaxOS — Bare Metal x86 OS

> Développé automatiquement par **MaxOS AI v18.0**

## 📊 État actuel

| Métrique | Valeur |
|---|---|
| 🎯 Score | **35/100** |
| 📈 Niveau | desc |
| 📁 Fichiers | 149 |
| 📝 Lignes | 3,287 |
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
- IDT initialisée (idt.c/idt.asm)
- ISRs manuels (isr.asm)
- IRQs configurées (irq.asm/irq.c)
- GDT en place (gdt.asm)
- Paging basique (paging.c)
- PMM (Physical Memory Manager)
- VGA driver (vga.c)
- Clavier PS/2 (keyboard.c)
- Timer PIT (timer.c)
- Terminal basique (terminal.c)
- FAT32 filesystem (fat32.c)
- VFS (vfs.c)
- GUI basique (ui.c)
- SMP support (smp.asm/smp.c)
- Exceptions/fault handlers (fault_handler.c)
- PIC remappé (pic.c)
- IO abstractions (io.h)
- Makefile fonctionnel

## 🚧 En développement

- Pas de gestion des processus (schedule.c vide)
- Pas de heap dynamique (heap.c vide)
- Pas de gestion des syscalls
- Pas de support ACPI/SMP avancé
- Pas de gestion des interruptions matérielles avancées (USB, ATA DMA)
- Pas de protection mémoire (segments/ring protection)
- Pas de système de fichiers complet (seulement FAT32 basique)
- Pas de gestion des exceptions matérielles (MCE)
- Pas de support pour les périphériques modernes (PCIe, AHCI)
- Pas de système de logging structuré
- Pas de gestion des timers avancés (HPET)
- Pas de support pour les applications utilisateur (seulement stubs)
- Pas de gestion des erreurs matérielles (NMI)
- Pas de support pour les architectures multi-cœurs avancées
- Pas de système de fichiers journalisé
- Pas de gestion des interruptions NMI
- Pas de support pour les périphériques USB HID
- Pas de gestion des interruptions SMI
- Pas de support pour les instructions CPU avancées (SSE, AVX)
- Pas de système de fichiers réseau

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
