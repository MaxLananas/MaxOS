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

## Roadmap

- [x] Bootloader
- [x] Mode protégé 32-bit
- [x] Driver VGA
- [x] Driver clavier AZERTY
- [x] Interface multi-fenêtres
- [x] Bloc-Notes
- [x] Terminal
- [ ] Système de fichiers FAT12
- [ ] Gestionnaire de mémoire
- [ ] Multitâche
```

---

## Workflow avec Gemini 🤖

```
TOI : "Gemini, voici mon kernel.c [colle le code]
       Améliore l'interface pour ressembler à Win11"

GEMINI : [donne le code amélioré]

TOI :
  git add .
  git commit -m "feat: amélioration UI par Gemini"
  git push

GITHUB ACTIONS : compile automatiquement ✅
                 crée l'artifact ✅
                 teste ✅
```

---

## Commandes Git pour démarrer

```bash
# 1. Initialiser le repo
cd /mnt/c/Users/MAXENCE/Desktop/mon_os
git init
git branch -M main

# 2. Créer .gitignore
echo "build/" > .gitignore

# 3. Premier commit
git add .
git commit -m "feat: MaxOS v1.0 - Initial commit"

# 4. Sur github.com : créer le repo MaxOS
# Puis :
git remote add origin https://github.com/maxence/MaxOS.git
git push -u origin main

# 5. Actions s'exécute automatiquement !
