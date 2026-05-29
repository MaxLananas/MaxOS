# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

# Documentation Technique MaxOS

## 1. Introduction

MaxOS est un système d'exploitation bare metal en cours de développement, conçu pour fonctionner sur l'architecture x86. Actuellement au stade de prototype (score 35/100), MaxOS vise à fournir une base solide pour l'apprentissage et l'expérimentation des concepts fondamentaux des systèmes d'exploitation.

Ce document sert de guide technique complet pour les développeurs et les contributeurs potentiels. Il couvre les aspects essentiels du projet, de la compilation et du test à la structure du code et à la feuille de route future.

**État Actuel :**
*   **Boot x86 :** Le système démarre avec succès sur des machines virtuelles (QEMU) et potentiellement sur du matériel réel compatible.
*   **VGA Texte 80x25 :** Une interface texte basique est disponible, permettant l'affichage de messages et d'informations de débogage.
*   **Codebase :** Le projet est composé de 68 fichiers C et 23 fichiers ASM, gérant le processus de démarrage, l'initialisation du noyau et les premières interactions matérielles.

## 2. Guide du Développeur

Ce guide fournit toutes les informations nécessaires pour démarrer avec le développement de MaxOS.

### 2.1. Prérequis

Pour compiler et tester MaxOS, vous aurez besoin des outils suivants sur votre système hôte

---
*MaxOS AI v18.0*
