# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

# Documentation Technique MaxOS

## Introduction

MaxOS est un système d'exploitation expérimental et éducatif, conçu pour fonctionner directement sur le matériel x86 (ou une machine virtuelle). Actuellement au stade de prototype "bare metal" (score 35/100), MaxOS vise à fournir une plateforme pour explorer les concepts fondamentaux des systèmes d'exploitation, de l'amorçage à la gestion des ressources. Ce document sert de guide technique complet pour les développeurs souhaitant comprendre, compiler, tester et contribuer au projet.

## Caractéristiques Actuelles

Malgré son stade précoce, MaxOS intègre déjà des fonctionnalités essentielles :

*   **Amorçage x86 (Boot x86) :** Le système est capable de démarrer sur une architecture x86 standard, initialisant le processeur et transférant le contrôle au noyau.
*   **Affichage Texte VGA 80x25 :** MaxOS peut interagir avec l'écran en mode texte VGA, permettant un affichage de 80 colonnes sur 25 lignes.
*   **Base de Code :** Le projet est composé de 76 fichiers C pour la logique du noyau et des pilotes, et de 23 fichiers ASM (Assembleur) pour les routines de bas niveau et l'amorçage.

## Guide du Développeur

Ce guide fournit les informations nécessaires pour démarrer avec le développement de MaxOS.

### 1. Compilation de MaxOS

La compilation de MaxOS nécessite une chaîne d'outils de développement spécifique pour les systèmes embarqués ou bare-metal.

#### Prérequis

Avant de compiler, assurez-vous d'avoir les outils suivants installés sur votre système (généralement Linux ou macOS) :

*   **Compilateur croisé GCC pour i386-elf :** Un compilateur GCC configuré pour cibler l'architecture

---
*MaxOS AI v18.0*
