# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, conforme à vos exigences :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation minimaliste pour x86 en mode texte (80x25)*
**Niveau :** Prototype bare metal | **Score :** 35/100
**Fichiers :** 46 (C) + 14 (ASM)

---

## **📌 Introduction**
MaxOS est un système d'exploitation expérimental conçu pour :
- Démarrer sur architecture x86 (mode 16/32 bits).
- Afficher un terminal texte en 80x25 via VGA.
- Servir de base pour l'apprentissage des concepts OS (interruptions, gestion mémoire, etc.).

Ce guide couvre les aspects techniques essentiels pour les développeurs souhaitant contribuer ou tester le projet.

---

## **🔧 Prérequis**
- **Compilateur :** `gcc` (pour le code C) + `nasm` (pour l'ASM).
- **Émulateur :** QEMU (recommandé pour le test).
- **Outils :** `make`, `ld` (linker GNU), `objcopy`.
- **Système hôte :** Linux (recommandé) ou WSL.

---

## **🛠️ 1. Compilation du Projet**

### **Structure des fichiers**
```
maxos/
├── boot/               # Code de démarrage (ASM)
│   ├── boot.asm        # Chargeur de démarrage (MBR)
│   └── kernel_entry.asm # Passage en mode 32 bits
├── kernel/             # Noyau principal (C)
│   ├── main.c          # Point d'entrée
│   ├── drivers/        # Pilotes (VGA, clavier)
│   ├── lib/            # Bibliothèques utilitaires
│   └── ...
├── tools/              # Scripts de build
│   └── build.sh        # Script de compilation
├── Makefile            # Règle de build principale
└── README.md           # Documentation utilisateur
```

### **Étapes de compilation**
1. **Nettoyer les anciens builds** (optionnel) :
   ```bash
   make clean
   ```

2. **Compiler le noyau et le bootloader** :
   ```bash
   make
   ```
   - Le script `build.sh` utilise `nasm` pour assembler les fichiers `.asm` et `gcc` pour compiler le C.
   - Le linker (`ld`) génère un binaire `kernel.bin` combiné avec le bootloader.

3. **Résultat** :
   - `maxos.img` : Image disque bootable (format MBR).
   - `kernel.bin` : Noyau chargé en mémoire.

> **Note :** Le Makefile gère les dépendances entre fichiers C/ASM.

---

## **🧪 2. Test avec QEMU**

### **Lancer MaxOS dans QEMU**
```bash
make run
```
- QEMU émule un PC x86 avec :
  - 128 Mo de RAM.
  - Carte VGA standard (80x25).
  - Clavier PS/2.

### **Options avancées**
- **Débogage avec GDB** :
  ```bash
  make debug
  ```
  - QEMU attend une connexion GDB sur le port `1234`.
  - Utilisez `target remote localhost:1234` dans GDB pour attacher le débogueur.

- **Changer la résolution VGA** :
  Modifiez les registres VGA dans `drivers/vga.c` (ex: `0x3` pour 80x25).

### **Dépannage**
- **Échec de boot ?**
  Vérifiez :
  - La taille de `maxos.img` (doit être 512 octets + secteur de boot).
  - Les messages de QEMU (`-d int,cpu_reset` pour les interruptions).

---

## **📂 3. Structure du Code**

### **Fichiers Clés**
| Chemin               | Description                          | Langage |
|----------------------|--------------------------------------|---------|
| `boot/boot.asm`      | Chargeur de démarrage (MBR)          | ASM     |
| `boot/kernel_entry.asm` | Passe en mode 32 bits (protected mode) | ASM |
| `kernel/main.c`      | Point d'entrée du noyau              | C       |
| `kernel/drivers/vga.c` | Pilote VGA (écriture de caractères) | C       |
| `kernel/lib/string.c` | Fonctions utilitaires (memcpy, etc.) | C       |

### **Conventions de Code**
- **Nommage :**
  - Fonctions : `snake_case` (ex: `vga_putchar`).
  - Variables globales : `g_` préfixe (ex: `g_cursor_x`).
- **Style C :**
  - Utilisation de `static inline` pour les fonctions critiques.
  - Éviter les allocations dynamiques (pas de `malloc` dans le noyau).

### **Gestion des Interruptions**
- Les interruptions matérielles (IRQ) sont gérées via :
  - IDT (Interrupt Descriptor Table) définie dans `kernel/idt.c`.
  - Routines en ASM dans `boot/interrupt.asm`.

---

## **🤝 4. Contribuer au Projet**

### **Processus de Contribution**
1. **Forker le dépôt** et créer une branche :
   ```bash
   git checkout -b feature/ma_nouvelle_fonction
   ```

2. **Implémenter la fonctionnalité** :
   - Respectez les conventions de code.
   - Ajoutez des tests unitaires si possible (dans `tests/`).

3. **Soumettre une Pull Request** :
   - Décrivez les changements dans le message.
   - Liez les issues concernées (si applicable).

### **Bonnes Pratiques**
- **Documentation :** Ajoutez des commentaires pour les fonctions complexes.
- **Tests :** Testez dans QEMU avant de soumettre.
- **Style :** Utilisez `clang-format` pour uniformiser le code.

### **Exemple de Contribution**
- **Ajouter un pilote clavier** :
  1. Créer `kernel/drivers/keyboard.c`.
  2. Implémenter `keyboard_init()` et `keyboard_handler()`.
  3. Mettre à jour `kernel/main.c` pour activer l'IRQ1.

---

## **🗺️ 5. Roadmap**

### **Objectifs Court Terme (0-3 mois)**
| Tâche                     | Priorité | Statut |
|---------------------------|----------|--------|
| Support du mode graphique (VESA) | Haute    | ❌     |
| Gestion basique de la mémoire (PMM) | Moyenne  | ⚠️     |
| Système de fichiers (FAT16) | Basse    | ❌     |

### **Objectifs Moyen Terme (3-6 mois)**
| Tâche                     | Priorité | Statut |
|---------------------------|----------|--------|
| Multitâche préemptif (avec timer) | Haute    | ❌     |
| Pilotes USB (clavier/souris) | Moyenne  | ❌     |
| Shell intégré (commandes basiques) | Basse    | ⚠️     |

### **Objectifs Long Terme (6+ mois)**
| Tâche                     | Priorité | Statut |
|---------------------------|----------|--------|
| Support 64 bits (x86_64)  | Haute    | ❌     |
| Réseau (TCP/IP basique)   | Moyenne  | ❌     |
| Système de paquets (pour installer des logiciels) | Basse | ❌ |

### **Comment Proposer une Nouvelle Fonctionnalité ?**
1. Ouvrez une **issue** pour discuter de la faisabilité.
2. Implémentez une **preuve de concept** dans une branche dédiée.
3. Soumettez une PR avec des tests.

---

## **📚 Ressources Utiles**
- **Références :**
  - [OSDev Wiki](https://wiki.osdev.org/) (indispensable pour les concepts OS).
  - [Intel Manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html) (pour les instructions x86).
- **Outils :**
  - `qemu-system-x86_64 -d int,cpu_reset` (débogage avancé).
  - `gdb -q -ex "target remote localhost:1234"` (débogage noyau).

---

## **📜 Licence**
MaxOS est distribué sous **licence MIT

---
*MaxOS AI v18.0*
