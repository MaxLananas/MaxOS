# MaxOS 🖥️

> Système d'exploitation minimaliste en C et Assembly x86

![Build](https://github.com/MaxLananas/MaxOS/actions/workflows/build.yml/badge.svg)

## Aperçu

MaxOS est un OS fait from scratch en C et Assembly x86 32-bit.
- Interface style Windows 11
- Bloc-Notes avec édition de texte
- Terminal avec commandes
- Horloge en temps réel
- Clavier AZERTY

## Compiler et tester

```bash
# Installer les dépendances
sudo apt install nasm gcc make qemu-system-x86

# Compiler
make

# Lancer
make run
```

## Contrôles

| Touche | Action |
|--------|--------|
| TAB    | Changer d'app |
| F1     | Bloc-Notes |
| F2     | Terminal |
| F3     | Système |
| F4     | À propos |

## Architecture

```
boot/      Bootloader MBR 512 bytes
kernel/    Noyau principal
drivers/   VGA + Clavier PS/2
ui/        Interface graphique
apps/      Applications
```
