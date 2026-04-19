# Architecture du système MaxOS

## Vue d'ensemble
MaxOS est un système d'exploitation minimaliste pour x86 (32 bits) développé en assembleur et en C, conforme aux règles bare metal strictes.

## Structure mémoire

### Organisation de la mémoire
- **Adresse de départ du kernel**: 0x8000 (définie dans linker.ld)
- **Taille maximale du kernel**: 2879 secteurs (1,44 Mo)
- **Pile**: 16 Ko réservée dans kernel_entry.asm

### Sections mémoire
1. **.text**: Code exécutable
2. **.data**: Données initialisées
3. **.bss**: Données non initialisées (zéro)

## Composants principaux

### Bootloader (boot.asm)
- Charge le kernel en mémoire à l'adresse 0x8000
- Vérifie que le kernel ne dépasse pas 2879 secteurs
- Passe en mode protégé 32 bits

### Kernel (kernel.c)
- Point d'entrée principal: `_start` dans kernel_entry.asm
- Boucle infinie principale dans `kernel_main()`
- Gestion des interruptions via IDT

### Pilotes (drivers/)
- **screen.c**: Gestion de l'affichage VGA
- **keyboard.c**: Gestion du clavier PS/2
- **vga.c**: Bas niveau VGA

### Applications (apps/)
- **notepad.c**: Éditeur de texte simple
- **terminal.c**: Terminal basique
- **sysinfo.c**: Affichage d'informations système
- **about.c**: Écran d'information

### Gestion système (kernel/)
- **idt.c**: Gestion de la table des interruptions
- **isr.asm**: Routines de service d'interruption (manuelles)
- **isr.c**: Gestion des ISR en C
- **timer.c**: Gestion de l'horloge système
- **memory.c**: Gestion basique de la mémoire

## Flux de démarrage
1. BIOS charge le bootloader depuis le secteur 0
2. Bootloader charge le kernel depuis les secteurs suivants
3. Kernel initialise la GDT, l'IDT et les périphériques
4. Kernel démarre la boucle principale

## Conventions de codage
- Utilisation exclusive de types unsigned pour les tailles
- Pas de fonctions de la libc standard
- Accès bas niveau uniquement via kernel/io.h
- Chaque fichier .c inclut son .h correspondant

## Limitations
- Pas de multitâche
- Pas de gestion avancée de la mémoire
- Pilotes minimalistes
- Pas de système de fichiers