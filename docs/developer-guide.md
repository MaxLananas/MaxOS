# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

# Documentation Technique MaxOS

## Introduction

MaxOS est un système d'exploitation bare-metal en cours de développement, conçu pour l'architecture x86. Actuellement au stade de prototype "bare metal" (score 35/100), MaxOS vise à fournir une plateforme éducative et fonctionnelle pour explorer les concepts fondamentaux des systèmes d'exploitation. Ce document sert de guide technique complet pour les développeurs souhaitant comprendre, compiler, tester et contribuer au projet.

Le projet met l'accent sur la simplicité et la clarté du code, avec une base significative de code C (76 fichiers) pour la logique du noyau et des pilotes, complétée par de l'assembleur (23 fichiers) pour les opérations de bas niveau critiques comme le démarrage et la gestion des interruptions.

## Caractéristiques Actuelles

Malgré son stade précoce, MaxOS intègre déjà des fonctionnalités essentielles :

*   **Boot x86 :** Le système est capable de démarrer sur une machine virtuelle ou physique compatible x86, grâce à un chargeur de démarrage basé sur GRUB.
*   **Affichage texte VGA 80x25 :** Max

---
*MaxOS AI v18.0*
