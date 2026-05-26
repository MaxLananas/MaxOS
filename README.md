# 🖥️ MaxOS — Bare Metal x86 OS

> Développé automatiquement par **MaxOS AI v18.0**

## 📊 État actuel

| Métrique | Valeur |
|---|---|
| 🎯 Score | **35/100** |
| 📈 Niveau | desc |
| 📁 Fichiers | 151 |
| 📝 Lignes | 3,184 |
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
- ISRs 0-31 (exceptions CPU) implémentés
- IRQs 0-15 (PIC) configurés
- Gestionnaire de fautes (fault_handler)
- PIT Timer (timer_init)
- Clavier PS/2 (keyboard_init)
- Écran VGA (screen_init)
- Terminal basique (terminal_run)
- Gestion mémoire basique (pmm/vmm)
- Paging activé
- SMP support (smp.asm)
- Syscalls stubs
- FAT32 filesystem basique
- GUI widgets (ui/widget)
- Applications (about, notepad, sysinfo)

## 🚧 En développement

- ISRs 32-47 (IRQs) incomplets (isr.asm tronqué à isr21)
- Pas de gestion des erreurs d'IRQ (IRQ 7/15 spurious)
- Pas de gestion des exceptions avec code d'erreur (ISRs 8,10-14,17)
- PIC non reprogrammé (IRQs 0-15 en mode 8259A standard)
- Pas de gestion des EOI pour les IRQs
- Pas de gestion des spurious IRQs
- Pas de gestion des exceptions doubles (NMI)
- Pas de gestion des exceptions avec code d'erreur (page fault, GPF)
- Pas de gestion des exceptions avec code d'erreur (segmentation)
- Pas de gestion des exceptions avec code d'erreur (alignement)
- Pas de gestion des exceptions avec code d'erreur (division par zéro)
- Pas de gestion des exceptions avec code d'erreur (overflow)
- Pas de gestion des exceptions avec code d'erreur (bound range)
- Pas de gestion des exceptions avec code d'erreur (invalid opcode)
- Pas de gestion des exceptions avec code d'erreur (device not available)
- Pas de gestion des exceptions avec code d'erreur (coprocessor segment overrun)
- Pas de gestion des exceptions avec code d'erreur (invalid TSS)
- Pas de gestion des exceptions avec code d'erreur (segment not present)
- Pas de gestion des exceptions avec code d'erreur (stack segment fault)
- Pas de gestion des exceptions avec code d'erreur (general protection fault)
- Pas de gestion des exceptions avec code d'erreur (page fault)
- Pas de gestion des exceptions avec code d'erreur (x87 FPU)
- Pas de gestion des exceptions avec code d'erreur (alignment check)
- Pas de gestion des exceptions avec code d'erreur (machine check)
- Pas de gestion des exceptions avec code d'erreur (SIMD FPU)
- Pas de gestion des exceptions avec code d'erreur (virtualization)
- Pas de gestion des exceptions avec code d'erreur (security exception)
- Pas de gestion des exceptions avec code d'erreur (triple fault)
- Pas de gestion des exceptions avec code d'erreur (FPU error)
- Pas de gestion des exceptions avec code d'erreur (reserved)
- Pas de gestion des exceptions avec code d'erreur (reserved)
- Pas de gestion des exceptions avec code d'erreur (reserved)

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
