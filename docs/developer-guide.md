# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

# Documentation Technique MaxOS

## Introduction

Bienvenue dans la documentation technique de MaxOS, un système d'exploitation bare-metal en cours de développement. MaxOS est conçu pour fonctionner directement sur le matériel x86, sans dépendre d'un système d'exploitation hôte. Actuellement au stade de prototype "bare metal" (score estimé : 35/100), MaxOS démontre des capacités fondamentales telles que le démarrage sur architecture x86 et l'affichage de texte via le mode VGA 80x25.

Ce document est destiné aux développeurs souhaitant comprendre, compiler, tester et contribuer au projet MaxOS.

---

## Guide Développeur MaxOS

Ce guide fournit toutes les informations nécessaires pour démarrer le développement sur MaxOS.

### 1. Prérequis

Avant de pouvoir compiler et tester MaxOS, vous devez installer les outils suivants sur votre système de développement (Linux est fortement recommandé) :

*   **Git** : Pour cloner le dépôt du projet.
*   **GNU Make** : L'outil de construction principal.
*   **GCC (GNU Compiler Collection)** : Le compilateur C.
*   **NASM (Netwide Assembler)** : L'assembleur pour le code x86.
*   **QEMU** : Un émulateur de machine pour tester MaxOS sans matériel réel.
*   **Cross-compilateur i386-elf-gcc** : Un compilateur GCC configuré pour cibler l'architecture i386 (32 bits) et le format ELF, sans dépendre d'une bibliothèque standard (libc) spécifique à un OS. C'est *essentiel* pour le développement bare-metal.

**Installation sur Debian/Ubuntu (exemples) :**

```bash
# Outils de base
sudo apt update

---
*MaxOS AI v18.0*
