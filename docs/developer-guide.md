# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, conforme à vos exigences :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation minimaliste pour x86 en mode texte*

**Score** : 35/100 | **Niveau** : Prototype bare metal
**Fichiers** : 76 (C) + 23 (ASM) | **État** : Boot x86, VGA texte 80x25

---

## **📌 Introduction**
MaxOS est un système d'exploitation minimaliste conçu pour apprendre les bases du développement kernel. Il supporte le boot sur architecture x86 et affiche un terminal texte 80x25 via VGA. Ce guide couvre la compilation, le test, la structure du projet, les contributions et la roadmap.

---

## **🔧 1. Compilation**
### **Prérequis**
- **Compilateur** : `gcc` (version 11+) ou `clang`
- **Assembleur** : `nasm` (pour le code x86)
- **Outils** : `make`, `ld` (GNU Linker)
- **Émulateur** : `qemu-system-x86_64` (pour les tests)

### **Étapes**
1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/votre-utilisateur/maxos.git
   cd maxos
   ```

2. **Compiler** :
   ```bash
   make
   ```
   - **Options** :
     - `make debug` : Active les logs de débogage.
     - `make clean` : Nettoie les fichiers générés.

3. **Fichiers générés** :
   - `maxos.bin` : Image binaire bootable.
   - `kernel.elf` : Fichier ELF du kernel (pour débogage).

---

## **🧪 2. Test avec QEMU**
### **Lancer MaxOS dans QEMU**
```bash
make run
```
- **Options avancées** :
  ```bash
  qemu-system-x86_64 -drive format=raw,file=maxos.bin -serial stdio
  ```
  - `-serial stdio` : Redirige la sortie vers le terminal.
  - `-m 128M` : Alloue 128 Mo de RAM (par défaut).

### **Débogage avec GDB**
1. Lancer QEMU en mode debug :
   ```bash
   make debug
   ```
2. Dans un autre terminal, attacher GDB :
   ```bash
   gdb -q kernel.elf
   (gdb) target remote localhost:1234
   (gdb) continue
   ```

---

## **📂 3. Structure des Fichiers**
```
maxos/
├── boot/               # Code de boot (ASM)
│   ├── boot.asm        # Point d'entrée (MBR)
│   └── gdt.asm         # Table des descripteurs globaux
├── kernel/             # Code du kernel (C)
│   ├── main.c          # Fonction principale
│   ├── drivers/        # Pilotes (VGA, clavier)
│   ├── lib/            # Bibliothèques utilitaires
│   └── include/        # En-têtes
├── Makefile            # Règles de compilation
├── linker.ld           # Script de linkage
└── README.md           # Documentation
```

### **Détails clés**
- **`boot.asm`** : Charge le kernel en mémoire (via `multiboot` ou BIOS).
- **`main.c`** : Initialise le VGA, la GDT, et la boucle principale.
- **`drivers/vga.c`** : Gère l'affichage texte (80x25).
- **`lib/`** : Fonctions utilitaires (`memcpy`, `printf`).

---

## **🤝 4. Contribuer**
### **Processus**
1. **Forker** le dépôt et créer une branche :
   ```bash
   git checkout -b feature/ma-nouvelle-fonction
   ```
2. **Coder** en respectant :
   - **Style** : Indentation à 4 espaces, noms de variables explicites.
   - **Tests** : Ajouter des tests unitaires si possible.
3. **Soumettre une PR** avec :
   - Une description claire.
   - Des commits atomiques (`git commit -m "feat: ajoute le support du clavier"`).

### **Règles**
- **Pas de code non testé** dans `main`.
- **Documenter** les nouvelles fonctions dans les en-têtes.
- **Éviter** les dépendances externes (sauf si critique).

---

## **🗺️ 5. Roadmap**
### **Objectifs à court terme (v0.2)**
- [ ] **Gestion de la mémoire** : Allocateur basique (buddy system).
- [ ] **Interruptions** : Support des IRQ (horloge, clavier).
- [ ] **Système de fichiers** : FAT16 minimal.

### **Objectifs à moyen terme (v0.5)**
- [ ] **Multitâche** : Ordonnanceur préemptif.
- [ ] **Pilotes** : Support du disque (ATA PIO).
- [ ] **Shell** : Interface utilisateur basique.

### **Objectifs à long terme (v1.0)**
- [ ] **SMP** : Support du multiprocesseur.
- [ ] **Réseau** : Pilote Ethernet (via `e1000`).
- [ ] **Compatibilité** : Boot UEFI.

---

## **📜 Licence**
MaxOS est distribué sous **MIT License** (voir `LICENSE`).

---

## **📬 Contact**
- **Auteur** : [Votre Nom](mailto:votre@email.com)
- **Issues** : [GitHub Issues](https://github.com/votre-utilisateur/maxos/issues)

---
*Dernière mise à jour : `date`*
```

---

### **Points clés respectés** :
1. **Format Markdown** : Titres hiérarchisés, listes, code blocks.
2. **Professionnel** : Structure claire, ton technique mais accessible.
3. **Complet** : Couvre tous les points demandés (compilation, QEMU, structure, contributions, roadmap).
4. **Français** : Langage adapté, termes techniques corrects.

Vous pouvez adapter les chemins, noms de fichiers et liens selon votre dépôt réel.

---
*MaxOS AI v18.0*
