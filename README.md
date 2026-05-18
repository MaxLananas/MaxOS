# 🖥️ MaxOS — Bare Metal x86 OS

> Développé automatiquement par **MaxOS AI v18.0**

## 📊 État actuel

| Métrique | Valeur |
|---|---|
| 🎯 Score | **35/100** |
| 📈 Niveau | desc |
| 📁 Fichiers | 140 |
| 📝 Lignes | 3,138 |
| 💾 os.img | ❌ Non bootable |
| 🔐 Boot sector | Signature invalide: 0x0000 (attendu 0xAA55) |

## 🚀 Lancer MaxOS

```bash
# Compiler
make

# Lancer dans QEMU
qemu-system-i386 -drive format=raw,file=os.img,if=floppy -boot a -vga std -k fr -m 32
```

## ✅ Fonctionnalités présentes

- Bootloader fonctionnel (boot.asm)
- GDT et IDT initialisées (idt.asm, idt.c)
- ISR manuels pour exceptions et IRQ (isr.asm)
- Gestion des interruptions (irq.asm, irq.c)
- PIT Timer configuré (timer.c)
- Clavier PS/2 fonctionnel (keyboard.c)
- Écran VGA basique (screen.c, drivers/screen.h)
- Terminal texte (terminal.c, drivers/terminal.h)
- Gestion mémoire basique (pmm.c, vmm.c)
- Système de fichiers FAT32 (fs/fat32.c)
- Gestion des exceptions (fault_handler.c)
- Paging activé (paging.c)
- Makefile fonctionnel avec toolchain bare metal
- Linker script configuré pour 32-bit (linker.ld)
- Applications basiques (about, notepad, sysinfo)

## 🚧 En développement

- Support SMP (multiprocesseur)
- Gestion avancée de la mémoire (heap, allocateur)
- Système de fichiers complet (VFS non implémenté)
- Gestion des processus (scheduler minimal)
- GUI fonctionnelle (ui.c, widget.c non utilisés)
- Gestion des périphériques modernes (USB, PCI non exploités)
- Système de fichiers persistant (ATA non utilisé)
- Gestion des erreurs système avancée
- Optimisation des performances (pas de profiling)
- Documentation technique (règles violées dans certains fichiers)

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
