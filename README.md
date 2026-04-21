# 🖥️ MaxOS — Bare Metal x86 OS

> Développé automatiquement par **MaxOS AI v18.0**

## 📊 État actuel

| Métrique | Valeur |
|---|---|
| 🎯 Score | **35/100** |
| 📈 Niveau | desc |
| 📁 Fichiers | 95 |
| 📝 Lignes | 2,647 |
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
- ISR manuels (isr.asm)
- Gestion des exceptions (fault_handler.c)
- PIT Timer (timer.c)
- Clavier PS/2 (keyboard.c)
- Écran VGA (screen.c/vga.c)
- Terminal basique (terminal.c)
- Gestion mémoire (pmm.c/memory.c)
- GUI basique (ui.c/widget.c)
- Applications (about/notepad/sysinfo)
- Makefile conforme aux règles
- Linker script fonctionnel
- Mode 32-bit pur
- Pas de dépendances standard

## 🚧 En développement

- Gestion avancée des interruptions (IRQ1-15 non prioritaires)
- Paging complet (pas de MMU activée)
- Gestion des fautes matérielles (MCE)
- Système de fichiers
- Gestion des processus
- APIC/IOAPIC (PIC seulement)
- ACPI
- SMP
- Gestion des exceptions matérielles (GPF, PF)
- Optimisation mémoire (bitmap basique seulement)
- Gestion des timers avancés (APIC timer)
- Système de fichiers virtuel
- Gestion des périphériques PCI (pci.c vide)
- Souris (mouse.c non intégré)
- Gestion des erreurs système
- Système de logs
- Gestion des signaux
- Support des syscalls
- Gestion des timers haute résolution
- Optimisation des ISR (pas de partage d'IRQ)

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
