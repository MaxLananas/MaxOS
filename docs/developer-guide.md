# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

# Documentation Technique MaxOS

## Introduction

MaxOS est un système d'exploitation expérimental et éducatif, conçu pour fonctionner directement sur le matériel (bare metal) d'une architecture x86. Actuellement au stade de prototype "bare metal" (score 35/100), MaxOS démontre les fondations d'un OS minimaliste, capable de démarrer sur une machine x86 et d'afficher du texte en mode VGA 80x25. Ce document sert de guide technique complet pour les développeurs souhaitant comprendre, compiler, tester et contribuer au projet MaxOS.

Le projet est caractérisé par une base de code significative pour son stade actuel : 49 fichiers source en C et 14 fichiers en assembleur (ASM), soulignant l'effort de structuration et de modularité dès les premières étapes.

## Prérequis

Pour développer et tester MaxOS, vous aurez besoin des outils suivants, idéalement sous un environnement Linux :

*   **GNU GCC Cross-Compiler (i386-elf):** Un compilateur ciblant l'architecture `i386-elf` est essentiel pour construire un noyau sans dépendances de la bibliothèque standard du système hôte.

---
*MaxOS AI v18.0*
