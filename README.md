# MaxOS 🖥️

> Système d'exploitation minimaliste en C et Assembly x86

![Build](https://github.com/TON_USERNAME/MaxOS/actions/workflows/build.yml/badge.svg)

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
