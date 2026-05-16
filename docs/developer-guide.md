# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

# Documentation Technique MaxOS

## 1. Introduction

MaxOS est un système d'exploitation bare-metal en cours de développement, conçu pour fonctionner sur l'architecture x86. Actuellement au stade de prototype (score estimé : 35/100), MaxOS vise à fournir une plateforme éducative et expérimentale pour l'apprentissage des concepts fondamentaux des systèmes d'exploitation.

À ce stade initial, MaxOS est capable de :
*   **Boot x86 :** Démarrer sur une machine virtuelle ou physique compatible x86.
*   **Affichage VGA Texte 80x25 :** Interagir avec l'utilisateur via un mode texte standard VGA.

Le projet se distingue par une base de code significative pour son stade, avec 55 fichiers C et 19 fichiers ASM, témoignant d'une architecture déjà pensée pour l'expansion.

## 2. Prérequis

Pour compiler et tester MaxOS, vous aurez besoin des outils suivants sur votre système hôte (Linux est fortement recommandé) :

*   **Compilateur Croisé GCC (i686-elf) :** Un compilateur GCC configuré pour cibler l'architecture `i686-elf`. C'est essentiel car vous ne pouvez pas compiler un

---
*MaxOS AI v18.0*
