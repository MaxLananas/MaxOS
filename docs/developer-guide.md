# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici la documentation technique complète pour MaxOS, formatée en Markdown, incluant le guide développeur demandé.

---

# Documentation Technique MaxOS

## 1. Introduction

MaxOS est un système d'exploitation bare-metal en cours de développement, conçu pour fonctionner sur l'architecture x86. Actuellement au stade de prototype (score estimé : 35/100), MaxOS vise à construire un noyau robuste et modulaire à partir de zéro. Ce document sert de guide technique et de référence pour les développeurs souhaitant comprendre, compiler, tester et contribuer au projet.

**État Actuel du Projet (Prototype Bare Metal):**
*   **Fonctionnalités Implémentées:**
    *   Boot x86 via GRUB (Multiboot 1).
    *   Affichage texte VGA 80x25.
    *   Initialisation des structures de base du noyau (GDT, IDT).
    *   Gestion des interruptions matérielles (PIC).
    *   Gestion basique du timer et du clavier.
*   **Technologies Clés:** C, Assembleur (NASM), GRUB,

---
*MaxOS AI v18.0*
