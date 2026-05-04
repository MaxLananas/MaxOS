# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

# Documentation Technique MaxOS

## Introduction

MaxOS est un système d'exploitation bare-metal x86 en phase de prototype avancé (score estimé : 35/100). Conçu principalement à des fins éducatives et expérimentales, il vise à fournir une plateforme pour comprendre les rouages fondamentaux d'un système d'exploitation, depuis le démarrage jusqu'à l'interaction basique avec le matériel.

Développé avec un mélange de C (49 fichiers) pour la logique de haut niveau et d'Assembleur (14 fichiers) pour les interactions de bas niveau avec le matériel, MaxOS est une excellente base pour les développeurs souhaitant plonger dans le monde de la programmation système.

## Fonctionnalités Actuelles

Malgré son statut de prototype, MaxOS intègre déjà des fonctionnalités clés :

*   **Boot x86 :** Capacité de démarrer sur une machine x86 (réelle ou virtuelle) via un bootloader compatible.
*   **Mode Texte VGA 80x25 :** Initialisation et gestion de l'affichage en mode texte standard 80 colonnes par 25 lignes, permettant l'affichage de messages et d'informations de base.
*   **Architecture Hybride C/ASM :** Utilisation stratégique de l'Assembleur pour les routines critiques (démarrage, interruptions, accès direct au matériel) et du C pour le reste du noyau, facilitant la maintenabilité et l'extension.

## Architecture Générale

MaxOS suit une architecture monolithique typique des systèmes d'exploitation de

---
*MaxOS AI v18.0*
