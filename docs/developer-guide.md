# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

# Documentation Technique MaxOS

## Introduction

MaxOS est un système d'exploitation bare-metal en cours de développement, conçu comme une plateforme d'apprentissage et d'expérimentation pour les principes fondamentaux des systèmes d'exploitation. Actuellement au stade de prototype "bare metal", MaxOS vise à fournir une base solide pour l'exploration de l'architecture x86, de la gestion matérielle de bas niveau et de la construction d'un noyau à partir de zéro.

Ce document sert de guide technique complet pour les développeurs souhaitant comprendre, compiler, tester et contribuer au projet MaxOS.

## Caractéristiques Actuelles

Malgré son statut de prototype, MaxOS intègre déjà des fonctionnalités essentielles :

*   **Boot x86 :** Le système est capable de démarrer sur une machine x86 (réelle ou virtuelle) grâce à un chargeur de démarrage compatible GRUB.
*   **Affichage texte VGA 80x25 :** MaxOS initialise et utilise le mode texte VGA standard pour afficher des informations à l'écran, permettant une interaction basique avec l'utilisateur.

**Statistiques du code :**
*   Fichiers C : 76
*   Fichiers ASM : 23

## Guide du Développeur

Ce guide fournit les étapes nécessaires pour interagir avec le code source de MaxOS.

### 1. Compilation de MaxOS

La compilation de MaxOS nécessite une chaîne d'outils de développement spécifique pour cibler l'architecture i386 sans dépendre d'un système d'exploitation hôte.

#### Prérequis

Avant de commencer,

---
*MaxOS AI v18.0*
