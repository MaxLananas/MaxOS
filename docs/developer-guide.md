# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

# Documentation Technique MaxOS

## Introduction

MaxOS est un système d'exploitation bare-metal en cours de développement, conçu pour l'architecture x86. Actuellement au stade de prototype "bare metal" (score 35/100), MaxOS vise à fournir une plateforme éducative et fonctionnelle pour explorer les concepts fondamentaux des systèmes d'exploitation, de la gestion du matériel au développement de services de base. Ce document sert de guide technique complet pour les développeurs souhaitant comprendre, compiler, tester et contribuer au projet MaxOS.

## Caractéristiques Actuelles

Malgré son stade précoce, MaxOS intègre déjà des fonctionnalités essentielles :

*   **Boot x86 :** Le système est capable de démarrer sur une machine x86 (réelle ou virtuelle) grâce à un chargeur de démarrage basé sur GRUB.
*   **Affichage texte VGA 80x25 :** MaxOS peut interagir avec l'utilisateur via la console texte standard VGA, affichant des caractères sur un écran de 80 colonnes par 25 lignes.
*   **Base de code :** Le projet est composé de 76 fichiers C pour la logique du noyau et des pilotes, et de 23 fichiers ASM pour les routines de bas niveau et le démarrage.

## Guide du Développeur

Ce guide fournit les informations nécessaires pour démarrer le développement sur MaxOS.

### 1. Compilation de MaxOS

Pour compiler MaxOS, vous aurez besoin d'une chaîne d'outils de compilation croisée (cross-toolchain) et de quelques utilitaires.

#### Pré

---
*MaxOS AI v18.0*
