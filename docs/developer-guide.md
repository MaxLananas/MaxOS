# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, conforme à vos exigences :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation bare metal minimaliste pour x86*

**Score** : 35/100 (Prototype bare metal)
**Fonctionnalités** :
- Boot sur architecture x86
- Affichage VGA texte 80x25
- 55 fichiers C | 18 fichiers ASM

---

## **📌 Table des Matières**
1. [Prérequis](#prérequis)
2. [Compilation](#compilation)
3. [Test avec QEMU](#test-avec-qemu)
4. [Structure des Fichiers](#structure-des-fichiers)
5. [Contribuer](#contribuer)
6. [Roadmap](#roadmap)
7. [Licence](#licence)

---

## **🔧 Prérequis**
Avant de commencer, assurez-vous d'avoir installé :
- **Compilateur** : `gcc` (version ≥ 11) ou `clang`
- **Assembleur** : `nasm` (pour les fichiers `.asm`)
- **Linker** : `ld` (GNU Linker)
- **Émulateur** : `qemu-system-x86_64` (pour les tests)
- **Outils** : `make` (pour automatiser la compilation)
- **Bibliothèques** : Aucune dépendance externe (système minimaliste)

> **Note** : Sous Linux, installez les paquets via :
> ```bash
> sudo apt install build-essential nasm qemu-system-x86 grub2 xorriso
> ```

---

## **🏗️ Compilation**
MaxOS utilise un **Makefile** pour automatiser la compilation.

### **Étapes :**
1. **Cloner le dépôt** (si applicable) :
   ```bash
   git clone https://github.com/votre-utilisateur/maxos.git
   cd maxos
   ```

2. **Compiler le noyau** :
   ```bash
   make
   ```
   - Le Makefile génère :
     - Un **fichier binaire** (`kernel.bin`) pour le bootloader.
     - Une **image ISO** (`maxos.iso`) pour QEMU.

3. **Options avancées** :
   - `make clean` : Nettoie les fichiers générés.
   - `make debug` : Active les logs de débogage (si implémenté).
   - `make run` : Lance QEMU directement (voir [Test avec QEMU](#test-avec-qemu)).

---

## **🖥️ Test avec QEMU**
MaxOS est conçu pour être testé dans **QEMU**, un émulateur x86.

### **Méthode 1 : Lancement manuel**
```bash
qemu-system-x86_64 -kernel kernel.bin -display sdl -m 128M
```
- `-kernel kernel.bin` : Charge le noyau compilé.
- `-display sdl` : Utilise l'affichage SDL (alternative : `-nographic` pour la console).
- `-m 128M` : Alloue 128 Mo de RAM (ajustable).

### **Méthode 2 : Via Makefile**
```bash
make run
```
- Exécute QEMU avec les paramètres par défaut.

### **Débogage avec GDB**
Pour déboguer le noyau :
```bash
qemu-system-x86_64 -kernel kernel.bin -s -S &
gdb kernel.bin
```
- Dans GDB :
  ```gdb
  target remote localhost:1234
  continue
  ```

---

## **📂 Structure des Fichiers**
```
maxos/
├── **boot/**               # Code de boot (ASM)
│   ├── boot.asm            # Point d'entrée (MBR)
│   └── gdt.asm             # Table des descripteurs globaux
├── **kernel/**             # Noyau (C)
│   ├── main.c              # Fonction principale
│   ├── drivers/            # Pilotes matériels
│   │   ├── vga.c           # Affichage VGA texte
│   │   └── keyboard.c      # Clavier PS/2
│   ├── lib/                # Bibliothèques utilitaires
│   │   ├── string.c        # Fonctions de chaîne
│   │   └── stdio.c         # Entrée/sortie basique
│   └── include/            # En-têtes
│       ├── kernel.h        # Déclarations globales
│       └── drivers/
├── **linker.ld**           # Script de linkage
├── **Makefile**            # Règles de compilation
├── **iso/**                # Fichiers pour l'ISO
│   └── grub.cfg            # Configuration GRUB
└── **README.md**           # Documentation
```

### **Détails clés :**
- **`boot.asm`** :
  - Charge le noyau en mémoire à l'adresse `0x1000`.
  - Passe en **mode protégé** (32 bits).
- **`main.c`** :
  - Fonction `main()` : Point d'entrée du noyau.
  - Initialise les **interruptions**, la **VGA**, et les **périphériques**.
- **`vga.c`** :
  - Gère l'affichage texte 80x25 via les ports VGA.
  - Fonctions : `vga_clear()`, `vga_putchar()`.
- **`linker.ld`** :
  - Définit les sections mémoire (`.text`, `.data`, `.bss`).
  - Spécifie l'adresse de chargement (`0x1000`).

---

## **🤝 Contribuer**
MaxOS est un projet open-source. Voici comment contribuer :

### **1. Forker le dépôt**
- Créez un fork sur GitHub et clonez-le :
  ```bash
  git clone https://github.com/votre-utilisateur/maxos.git
  ```

### **2. Créer une branche**
```bash
git checkout -b feature/nom-de-la-fonction
```

### **3. Implémenter une fonctionnalité**
- **Nouveau pilote** : Ajoutez un fichier dans `kernel/drivers/`.
- **Amélioration** : Modifiez le code existant et testez.
- **Documentation** : Mettez à jour le `README.md` ou ajoutez des commentaires.

### **4. Soumettre une Pull Request (PR)**
1. Poussez vos changements :
   ```bash
   git add .
   git commit -m "Ajout du support du clavier PS/2"
   git push origin feature/nom-de-la-fonction
   ```
2. Ouvrez une PR sur GitHub avec une description claire.

### **📌 Bonnes pratiques :**
- **Code** :
  - Respectez le style C89 (pour la compatibilité bare metal).
  - Utilisez des noms de variables explicites.
  - Ajoutez des commentaires pour les parties complexes.
- **Tests** :
  - Testez toujours avec `make run` avant de soumettre.
  - Vérifiez que le noyau boot correctement dans QEMU.

---

## **🗺️ Roadmap**
Voici les étapes prévues pour évoluer vers un OS plus mature :

| **Phase**       | **Fonctionnalités**                          | **Statut**       |
|-----------------|---------------------------------------------|------------------|
| **Prototype**   | Boot x86, VGA texte, interruptions basiques | ✅ **Terminé**   |
| **v0.2**        | Gestion mémoire (PMM), multitâche basique  | 🔄 **En cours**  |
| **v0.3**        | Système de fichiers (FAT16)                | 📅 **Prévu**     |
| **v0.4**        | Pilotes USB, réseau (TCP/IP)               | 📅 **Prévu**     |
| **v1.0**        | Interface graphique (SVGA)                 | 🚀 **Objectif**  |

### **Détails par version :**
- **v0.2** :
  - **Gestion mémoire** : Allocation dynamique (`kmalloc`, `kfree`).
  - **Multitâche** : Bascule de contexte simple (sans préemption).
  - **Système de fichiers** : Lecture/écriture sur disque (via ATA PIO).
- **v0.3** :
  - **Pilotes USB** : Support des claviers/souris USB.
  - **Réseau** : Stack TCP/IP basique (DHCP, ping).
- **v1.0** :
  - **SVGA** : Affichage graphique (résolution configurable).
  - **API système

---
*MaxOS AI v18.0*
