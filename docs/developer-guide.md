# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, conforme à vos exigences :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation bare metal minimaliste pour x86*

**Score** : 35/100 (Prototype bare metal)
**Fonctionnalités** :
- Boot sur architecture x86
- Affichage texte VGA 80x25
- **Fichiers** : 43 en C, 14 en ASM

---

## **📌 Table des Matières**
1. [Prérequis](#prérequis)
2. [Compilation](#compilation)
3. [Test avec QEMU](#test-avec-qemu)
4. [Structure des Fichiers](#structure-des-fichiers)
5. [Contribuer](#contribuer)
6. [Feuille de Route (Roadmap)](#feuille-de-route-roadmap)
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
| **LD** (Linker) | GNU Binutils 2.38+ | Inclus avec GCC |

> **Note** : Sous Windows, utilisez [WSL](https://learn.microsoft.com/fr-fr/windows/wsl/install) ou un environnement Linux.

---

## **🛠️ Compilation**
MaxOS utilise un **Makefile** pour automatiser la compilation.

### **Étapes :**
1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/MaxOS.git
   cd MaxOS
   ```

2. Compilez avec :
   ```bash
   make
   ```
   - **Sortie** : Un fichier `maxos.bin` (image disque bootable) est généré dans le dossier `bin/`.

### **Options de Compilation**
| Commande | Description |
|----------|-------------|
| `make clean` | Supprime les fichiers temporaires |
| `make debug` | Active les logs de débogage (via `DEBUG=1`) |
| `make run` | Compile et lance QEMU (voir [Test avec QEMU](#test-avec-qemu)) |

> **Détails techniques** :
> - Le **Makefile** utilise `nasm` pour assembler les fichiers `.asm` et `gcc` pour compiler le C.
> - Le linker (`ld`) fusionne les objets en un binaire **ELF** puis le convertit en image disque **raw** (compatible boot).

---

## **🖥️ Test avec QEMU**
MaxOS est conçu pour être testé dans **QEMU**, un émulateur x86.

### **Lancement Basique**
```bash
make run
```
- QEMU démarre avec :
  - 128 Mo de RAM
  - Affichage texte VGA 80x25
  - Clavier PS/2 émulé

### **Options Avancées**
| Option | Description |
|--------|-------------|
| `make run-gdb` | Lance QEMU avec un serveur GDB (port `1234`) pour le débogage. |
| `qemu-system-x86_64 -drive format=raw,file=bin/maxos.bin` | Lancement manuel (si `make run` échoue). |
| `qemu-system-x86_64 -serial mon:stdio` | Redirige la sortie série vers le terminal. |

> **Astuce** : Pour capturer la sortie dans un fichier :
> ```bash
> qemu-system-x86_64 -drive file=bin/maxos.bin -serial file:output.log
> ```

---

## **📂 Structure des Fichiers**
MaxOS suit une architecture **modulaire** avec les dossiers principaux :

```
MaxOS/
├── **boot/**          # Code de démarrage (ASM)
│   ├── boot.asm       # Chargeur de boot (secteur 0)
│   └── gdt.asm        # Table des descripteurs globaux
├── **kernel/**        # Noyau (C)
│   ├── main.c         # Point d'entrée du noyau
│   ├── drivers/       # Pilotes (VGA, clavier)
│   └── lib/           # Bibliothèques utilitaires
├── **include/**       # En-têtes (.h)
├── **scripts/**       # Scripts utilitaires (ex: `build.sh`)
├── **bin/**           # Sorties de compilation
├── **docs/**          # Documentation
└── **Makefile**       # Script de build
```

### **Détails Clés**
| Dossier | Rôle |
|---------|------|
| **`boot/`** | Contient le **bootloader** (écrit en ASM) qui initialise le CPU et charge le noyau. |
| **`kernel/`** | Implémente les fonctionnalités de base (affichage, interruptions). |
| **`include/`** | Déclare les structures et fonctions partagées (ex: `vga.h` pour l'affichage). |
| **`drivers/`** | Pilotes matériels (ex: `vga.c` pour l'affichage texte). |

> **Exemple de flux de démarrage** :
> 1. `boot.asm` → Charge le noyau en mémoire.
> 2. `main.c` → Initialise la VGA et affiche un message.
> 3. Boucle principale attend les entrées clavier.

---

## **🤝 Contribuer**
MaxOS est un projet **open-source** et accueille les contributions !

### **Comment Contribuer ?**
1. **Fork** le dépôt sur GitHub.
2. Créez une **branche** pour votre feature :
   ```bash
   git checkout -b feature/ma-nouvelle-fonctionnalite
   ```
3. Implémentez votre code et ajoutez des tests.
4. Soumettez une **Pull Request** avec une description claire.

### **Règles de Contribution**
- **Style de code** :
  - Utilisez **4 espaces** pour l'indentation (pas de tabs).
  - Noms de variables en **snake_case** (ex: `current_task`).
  - Commentaires en **français** pour le code principal.
- **Tests** :
  - Ajoutez des tests unitaires dans `tests/` si possible.
  - Vérifiez que `make` et `make run` fonctionnent après vos modifications.
- **Documentation** :
  - Mettez à jour ce fichier si vous ajoutez une nouvelle fonctionnalité.

### **Exemple de Contribution**
- Ajout d'un pilote pour le **PS/2** :
  ```c
  // drivers/ps2.c
  void ps2_init() {
      outb(0x64, 0xAE); // Active le port PS/2
      // ... implémentation ...
  }
  ```
  - Ajoutez un en-tête dans `include/ps2.h`.
  - Testez avec `qemu-system-x86_64 -device ps2-kbd`.

---

## **🗺️ Feuille de Route (Roadmap)**
MaxOS est en phase de **prototype**. Voici les étapes prévues :

| Phase | Objectif | Statut |
|-------|----------|--------|
| **Phase 1** (Actuelle) | Boot bare metal + VGA | ✅ Complété |
| **Phase 2** | Gestion des interruptions (IRQ) | 🔄 En cours |
| **Phase 3** | Système de fichiers (FAT16) | 🚧 Planifié |
| **Phase 4** | Multitâche préemptif | 📝 À étudier |
| **Phase 5** | Support du réseau (TCP/IP) | 🔮 Futur |

### **Détails par Phase**
1. **Phase 2 : Interruptions**
   - Implémenter la **IDT** (Interrupt Descriptor Table).
   - Gérer les **IRQ 0-15** (horloge, clavier).
   - Ajouter un gestionnaire d'interruptions en ASM/C.

2. **Phase 3 : Système de Fichiers**
   - Lire/écrire sur un disque virtuel (via QEMU).
   - Implémenter un **FAT16** minimal.

---
*MaxOS AI v18.0*
