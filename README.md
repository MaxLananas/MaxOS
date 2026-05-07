# 🖥️ MaxOS — Bare Metal x86 OS

> Développé automatiquement par **MaxOS AI v18.0**

## 📊 État actuel

| Métrique | Valeur |
|---|---|
| 🎯 Score | **35/100** |
| 📈 Niveau | desc |
| 📁 Fichiers | 124 |
| 📝 Lignes | 2,867 |
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
- IRQ/PIT (irq.asm/timer.c)
- Gestion mémoire basique (pmm.c/vmm.c)
- VGA et écran (screen.c/drivers/screen.h)
- Clavier (keyboard.c/drivers/keyboard.h)
- Terminal (terminal.c/kernel/terminal.h)
- GUI basique (ui.c/ui.h)
- FAT32 (fs/fat32.c)
- VFS (fs/vfs.c)
- Heap (heap.c)
- Paging (paging.c)
- Exceptions (exceptions.c/fault_handler.c)
- Makefile conforme
- Linker script fonctionnel
- Outils I/O (io.h/io.asm)

## 🚧 En développement

- Support USB complet (drivers/usb.c incomplet)
- Gestion des processus (schedule.c vide)
- Système de fichiers persistant (FAT32 non monté)
- Gestion des interruptions souris (mouse.c incomplet)
- APIC/IOAPIC non configuré (PIC seul)
- ACPI non implémenté (hpet.c vide)
- SMP non supporté
- Syscalls non fonctionnels (syscall.c vide)
- Gestion des erreurs matérielles (mce.c vide)
- Optimisation mémoire (bitmap non utilisée)
- Applications GUI non interactives (about/notepad/sysinfo vides)
- Terminal sans historique ni commandes
- Pas de gestion des exceptions matérielles (MCE, NMI)
- Pas de protection mémoire (segments non configurés)
- Pas de support multi-cœurs

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
