# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, structurée selon vos exigences :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation bare metal minimaliste pour x86*

**Score** : 35/100 (Prototype bare metal)
**Fonctionnalités** :
- Boot sur architecture x86 (32 bits)
- Affichage texte VGA 80x25
- **Fichiers** : 46 en C, 14 en ASM

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
Avant de compiler ou tester MaxOS, assurez-vous d'avoir installé :

| Outil | Version Recommandée | Installation |
|-------|---------------------|--------------|
| **GCC** (pour C) | 11+ | `sudo apt install gcc` (Linux) |
| **NASM** (pour ASM) | 2.15+ | `sudo apt install nasm` |
| **QEMU** (émulateur) | 7.0+ | `sudo apt install qemu-system-x86` |
| **Make** | 4.3+ | `sudo apt install make` |
| **ld** (linker) | 2.38+ | Inclus avec GCC |

> **Note** : Sous Windows, utilisez [WSL](https://learn.microsoft.com/fr-fr/windows/wsl/install) ou [MSYS2](https://www.msys2.org/).

---

## **🏗️ Compilation**
MaxOS utilise un **Makefile** pour automatiser la compilation.

### **Étapes :**
1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/MaxOS.git
   cd MaxOS
   ```

2. Compilez le noyau :
   ```bash
   make
   ```
   - **Sortie** : `kernel.bin` (fichier binaire brut, compatible avec le bootloader).

### **Options de Compilation**
| Commande | Description |
|----------|-------------|
| `make clean` | Supprime les fichiers temporaires (`*.o`, `kernel.bin`). |
| `make debug` | Génère un binaire avec des symboles de débogage (pour GDB). |
| `make run` | Compile et lance QEMU automatiquement (voir [Test avec QEMU](#test-avec-qemu)). |

### **Détails Techniques**
- **Compilateur C** : Utilise `-m32` pour forcer le mode 32 bits.
- **Linker** : `ld` est configuré pour générer un binaire **flat binary** (sans en-tête ELF).
- **ASM** : Les fichiers `.asm` sont assemblés avec NASM en mode 32 bits.

---

## **🧪 Test avec QEMU**
MaxOS est conçu pour être testé dans **QEMU**, un émulateur x86.

### **Lancement de Base**
```bash
make run
```
- **Résultat attendu** : Une fenêtre QEMU s'ouvre avec l'affichage texte "MaxOS" en haut à gauche.

### **Options Avancées**
| Option | Description |
|--------|-------------|
| `make run ARCH=x86_64` | Force le mode 64 bits (non supporté par défaut). |
| `make run DEBUG=1` | Active le mode débogage (attend un debugger GDB). |
| `qemu-system-i386 -kernel kernel.bin -serial stdio` | Lance QEMU en mode console (utile pour le débogage). |

### **Débogage avec GDB**
1. Lancez QEMU en mode debug :
   ```bash
   make run DEBUG=1
   ```
2. Dans un autre terminal, connectez GDB :
   ```bash
   gdb -q
   (gdb) target remote localhost:1234
   (gdb) continue
   ```

---

## **📂 Structure des Fichiers**
```
MaxOS/
├── **boot/**          # Code de boot (ASM)
│   ├── boot.asm       # Point d'entrée (MBR)
│   └── gdt.asm        # Table des descripteurs globaux
├── **kernel/**        # Noyau (C)
│   ├── main.c         # Fonction principale
│   ├── drivers/       # Pilotes (VGA, clavier)
│   ├── lib/           # Bibliothèques utilitaires
│   └── ...
├── **include/**       # En-têtes (.h)
├── **Makefile**       # Règles de compilation
├── **linker.ld**      # Script du linker
└── **README.md**      # Documentation
```

### **Fichiers Clés**
| Fichier | Rôle |
|---------|------|
| `boot/boot.asm` | Charge le noyau en mémoire (secteur 0 du disque). |
| `kernel/main.c` | Point d'entrée du noyau (appelle `kernel_init()`). |
| `drivers/vga.c` | Gère l'affichage texte (80x25). |
| `linker.ld` | Définit la mémoire virtuelle et les sections du binaire. |

### **Conventions de Code**
- **C** : Respecte le standard **C99**.
- **ASM** : Utilise la syntaxe **Intel** (NASM).
- **Nommage** :
  - Fonctions : `snake_case` (ex: `vga_putchar`).
  - Variables globales : `g_` préfixe (ex: `g_kernel_initialized`).

---

## **🤝 Contribuer**
MaxOS est un projet open-source. Voici comment contribuer :

### **1. Fork & Clone**
```bash
git clone https://github.com/votre-utilisateur/MaxOS.git
cd MaxOS
git checkout -b feature/ma-nouvelle-fonctionnalité
```

### **2. Modifications**
- **Nouvelle fonctionnalité** :
  - Ajoutez des fichiers dans `kernel/` ou `drivers/`.
  - Mettez à jour `linker.ld` si nécessaire.
- **Correction de bug** :
  - Ouvrez une **issue** avant de coder.
  - Respectez le style existant.

### **3. Pull Request**
1. Testez vos modifications :
   ```bash
   make clean && make run
   ```
2. Poussez vos changements :
   ```bash
   git add .
   git commit -m "feat: ajoute le support du clavier PS/2"
   git push origin feature/ma-nouvelle-fonctionnalité
   ```
3. Ouvrez une **PR** sur GitHub avec une description claire.

### **Règles de Contribution**
- **Code Review** : Toute PR doit être validée par au moins 1 mainteneur.
- **Tests** : Les nouvelles fonctionnalités doivent être testées dans QEMU.
- **Documentation** : Mettez à jour le `README.md` si nécessaire.

---

## **🗺️ Roadmap**
MaxOS est en phase de **prototype**. Voici les étapes prévues :

| Phase | Objectif | Statut |
|-------|----------|--------|
| **Phase 1** (Actuelle) | Boot basique + VGA | ✅ Complété |
| **Phase 2** | Gestion des interruptions (IRQ) | 🔄 En cours |
| **Phase 3** | Pilotes (clavier, disque) | 🚧 Planifié |
| **Phase 4** | Système de fichiers (FAT32) | 📅 2025 |
| **Phase 5** | Multitâche (scheduling) | 📅 2026 |
| **Phase 6** | Réseau (TCP/IP) | 📅 2027 |

### **Fonctionnalités en Développement**
- **GDT/IDT** : Configuration des interruptions matérielles.
- **PIT** : Timer pour le multitâche.
- **PS/2** : Pilote clavier pour l'entrée utilisateur.

### **Idées pour Contributeurs**
- Ajouter un **shell minimal**.
- Implémenter un **système de fichiers**.
- Optimiser la gestion mémoire (buddy allocator).

---

## **📜 Licence**
MaxOS est distribué sous la licence **MIT** (voir [LICENSE](LICENSE)).

> **Autorisé** :

---
*MaxOS AI v18.0*
