# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

# Documentation Technique MaxOS

## 1. Introduction

MaxOS est un système d'exploitation bare-metal en cours de développement, conçu pour l'architecture x86. Actuellement au stade de prototype (score estimé : 35/100), MaxOS vise à fournir une plateforme éducative et fonctionnelle pour explorer les concepts fondamentaux de la conception de systèmes d'exploitation.

À ce stade initial, MaxOS est capable de :
*   **Boot x86 :** Démarrer sur une machine virtuelle ou physique compatible x86.
*   **VGA Texte 80x25 :** Afficher du texte en mode VGA 80 colonnes par 25 lignes, permettant une sortie basique pour le débogage et l'affichage d'informations.

Le projet est composé de 55 fichiers C et 19 fichiers assembleur (ASM), reflétant une base de code déjà significative pour un prototype bare-metal. Cette documentation est destinée aux développeurs souhaitant comprendre, compiler, tester et contribuer à MaxOS.

## 2. Prérequis

Pour compiler et tester MaxOS, vous aurez besoin des outils suivants installés sur votre système (Linux/macOS recommandé) :

*   **GNU GCC (Cross-compiler) :** Un compilateur C/C++ configuré pour la cible `i686-

---
*MaxOS AI v18.0*
