# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

# Documentation Technique MaxOS

## Introduction

MaxOS est un système d'exploitation bare-metal en cours de développement, conçu principalement à des fins éducatives et d'exploration des principes fondamentaux des systèmes d'exploitation. Actuellement au stade de prototype "bare metal" (score estimé : 35/100), MaxOS vise à fournir une plateforme simple et compréhensible pour apprendre l'architecture x86, la programmation de bas niveau et les concepts de base d'un OS.

Ce document sert de guide technique complet pour les développeurs souhaitant comprendre, compiler, tester et contribuer au projet MaxOS.

## Caractéristiques Actuelles

Malgré son stade précoce, MaxOS intègre déjà des fonctionnalités essentielles :

*   **Boot x86 :** Le système est capable de démarrer sur une machine virtuelle ou physique compatible x86, grâce à un chargeur de démarrage basé sur GRUB et des routines d'initialisation en assembleur.
*   **Affichage texte VGA 80x25 :** MaxOS peut interagir avec l'écran en mode texte VGA standard, permettant l'affichage de messages et d'informations de débogage.

Le projet est composé de 76 fichiers source

---
*MaxOS AI v18.0*
