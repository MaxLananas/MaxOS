# 🖥️ MaxOS — Bare Metal x86 OS

> Développé automatiquement par **MaxOS AI v18.0**

## 📊 État actuel

| Métrique | Valeur |
|---|---|
| 🎯 Score | **35/100** |
| 📈 Niveau | desc |
| 📁 Fichiers | 167 |
| 📝 Lignes | 3,563 |
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
- ISR et IRQ configurées (isr.asm, irq.asm)
- Gestion basique du clavier (keyboard.c)
- Gestion basique de l'écran (screen.c)
- Timer PIT initialisé (timer.c)
- Terminal basique (terminal.c)
- Gestion des exceptions (exceptions.c)
- Gestion de la mémoire physique (pmm.c)
- Gestion des processus basique (process.c)
- Gestion des appels système (syscall.c)
- Gestion du VFS (vfs.c)
- Gestion du FAT32 (fat32.c)
- Gestion du paging (paging.c)
- Gestion de la heap (heap.c)
- Gestion des périphériques (ATA, PCI, USB)
- Gestion de la souris (mouse.c)
- Gestion de la GUI basique (ui.c, widget.c)
- Applications basiques (about, notepad, sysinfo, terminal)

## 🚧 En développement

- Gestion avancée de la mémoire (buddy allocator, slab allocator)
- Gestion des threads et scheduling avancé
- Gestion des fichiers système (ext2, NTFS, etc.)
- Gestion des permissions et sécurité
- Gestion du réseau (TCP/IP stack)
- Gestion des pilotes graphiques avancés (VESA, framebuffer)
- Gestion des interruptions avancées (APIC, MSI)
- Gestion du SMP (multi-cœurs)
- Gestion des timers avancés (HPET, RTC)
- Gestion des systèmes de fichiers virtuels (procfs, sysfs)
- Gestion des signaux entre processus
- Gestion des devices dynamiques (udev-like)
- Gestion des modules noyau chargeables
- Gestion des systèmes de fichiers journalisés
- Gestion des ACLs et chiffrement
- Gestion des systèmes de fichiers distribués
- Gestion des systèmes de fichiers en réseau (NFS, SMB)
- Gestion des systèmes de fichiers compressés
- Gestion des systèmes de fichiers chiffrés
- Gestion des systèmes de fichiers temporaires (tmpfs)

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
