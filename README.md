# 🖥️ MaxOS — Bare Metal x86 OS

> Développé automatiquement par **MaxOS AI v18.0**

## 📊 État actuel

| Métrique | Valeur |
|---|---|
| 🎯 Score | **35/100** |
| 📈 Niveau | desc |
| 📁 Fichiers | 136 |
| 📝 Lignes | 2,953 |
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
- IDT et ISR implémentés (isr.asm, idt.c)
- Gestion des exceptions (fault_handler.c)
- PIT Timer (timer.c)
- Gestion clavier (keyboard.c)
- Terminal basique (terminal.c)
- VGA et écran (screen.c, vga.c)
- Gestion mémoire (mem.c, pmm.c)
- Système de fichiers FAT32 (fat32.c)
- Gestion des IRQ (irq.c, handlers.asm)
- Paging (paging.c)
- GUI basique (ui.c, widget.c)
- Applications (about, notepad, sysinfo, terminal)
- Makefile fonctionnel avec toolchain bare metal
- Linker script (linker.ld) conforme 32-bit
- SMP support (ap_start.asm, smp.asm)
- Gestion des syscalls (syscall.c)
- Heap basique (heap.c)
- PCI et ATA (pci.c, ata.c)
- Souris (mouse.c)

## 🚧 En développement

- Gestion avancée des processus (scheduler incomplet)
- Gestion complète des interruptions matérielles (PIC/APIC)
- Système de fichiers complet (VFS partiel)
- Gestion des périphériques USB (pilotes basiques)
- Gestion avancée de la mémoire (VMM incomplet)
- Support multi-cœurs stable (SMP partiel)
- Gestion des timers avancés (HPET incomplet)
- Système de fichiers persistant (FAT32 en RAM)
- Gestion des exceptions matérielles (MCE)
- Optimisation des performances (cache, TLB)
- Gestion des erreurs matérielles (NMI)
- Support des disques multiples (ATA/USB)
- Gestion des timers par cœur (APIC timer)
- Système de fichiers réseau (non implémenté)
- Gestion des signaux (non implémenté)
- Support des architectures 64-bit (32-bit uniquement)

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
