# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, conforme à vos exigences :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation bare metal minimaliste pour x86*

**Score** : 35/100 | **Niveau** : Prototype bare metal
**Fonctionnalités** :
- Boot sur architecture x86
- Affichage texte VGA 80x25
- **Fichiers** : 61 en C, 21 en ASM

---

## **📌 Guide Développeur**

Ce guide couvre les aspects essentiels pour contribuer à MaxOS, depuis la compilation jusqu'à l'exécution dans QEMU.

---

## **1️⃣ Compilation du Projet**

### **Prérequis**
- **Compilateur** : `gcc` (version ≥ 10) ou `clang`
- **Assembleur** : `nasm` (pour les fichiers `.asm`)
- **Outils** : `make`, `ld` (GNU Linker)
- **Émulateur** : QEMU (pour les tests)

### **Étapes de Compilation**
1. **Cloner le dépôt** (si applicable) :
   ```bash
   git clone https://github.com/votre-utilisateur/maxos.git
   cd maxos
   ```

2. **Compiler avec Make** :
   ```bash
   make clean && make
   ```
   - **Options disponibles** :
     - `make debug` : Active les logs de débogage.
     - `make iso` : Génère une image ISO bootable (nécessite `xorriso`).

3. **Fichiers générés** :
   - `maxos.bin` : Image binaire brute (pour QEMU).
   - `maxos.iso` : Image ISO bootable (si `xorriso` est installé).

---

## **2️⃣ Test dans QEMU**

### **Exécution de base**
```bash
qemu-system-x86_64 -drive format=raw,file=maxos.bin -vga std
```
- **Options utiles** :
  - `-serial mon:stdio` : Redirige la sortie série vers le terminal.
  - `-d int,cpu_reset` : Active les logs d'interruptions (pour le débogage).

### **Débogage avec GDB**
1. **Lancer QEMU en mode debug** :
   ```bash
   qemu-system-x86_64 -s -S -drive format=raw,file=maxos.bin
   ```
2. **Connecter GDB** :
   ```bash
   gdb maxos.bin
   (gdb) target remote :1234
   (gdb) continue
   ```

---

## **3️⃣ Structure des Fichiers**

```
maxos/
├── **boot/**               # Code de démarrage (ASM)
│   ├── boot.asm            # Point d'entrée (MBR)
│   └── gdt.asm             # Table des descripteurs globaux
├── **kernel/**             # Noyau (C)
│   ├── main.c              # Fonction principale
│   ├── drivers/            # Pilotes matériels
│   │   ├── vga.c           # Gestion de l'affichage texte
│   │   └── keyboard.c      # Pilote clavier PS/2
│   └── lib/                # Bibliothèques utilitaires
│       ├── string.c        # Fonctions de chaîne
│       └── stdio.c         # Entrée/sortie standard
├── **include/**            # En-têtes
│   ├── kernel/             # En-têtes du noyau
│   └── lib/                # En-têtes des bibliothèques
├── **Makefile**            # Règles de compilation
└── **docs/**               # Documentation
```

### **Détails Clés**
- **`boot/boot.asm`** :
  - Charge le noyau en mémoire (adresse `0x1000`).
  - Passe en mode protégé (32 bits).
- **`kernel/main.c`** :
  - Initialise les périphériques (VGA, clavier).
  - Boucle principale du système.
- **`drivers/vga.c`** :
  - Implémente `printf()` pour l'affichage texte.

---

## **4️⃣ Contribuer au Projet**

### **Processus de Contribution**
1. **Forker le dépôt** et créer une branche :
   ```bash
   git checkout -b feature/ma-nouvelle-fonctionnalite
   ```
2. **Respecter les conventions** :
   - **Nommage** : `snake_case` pour les fichiers, `PascalCase` pour les fonctions.
   - **Commentaires** : Utiliser Doxygen pour la documentation.
3. **Soumettre une Pull Request** :
   - Inclure une description claire des modifications.
   - Ajouter des tests si applicable.

### **Bonnes Pratiques**
- **Tests** : Toujours tester dans QEMU avant de soumettre.
- **Style** : Utiliser `clang-format` pour uniformiser le code.
- **Documentation** : Mettre à jour le `README.md` et les commentaires.

---

## **5️⃣ Roadmap**

### **Objectifs à Court Terme (v0.2)**
- [ ] **Gestion de la mémoire** : Allocation dynamique (buddy system).
- [ ] **Système de fichiers** : Support basique pour FAT16.
- [ ] **Multitâche** : Ordonnanceur préemptif (basé sur des timers).

### **Objectifs à Moyen Terme (v0.3)**
- [ ] **Pilotes** : Support du disque dur (ATA PIO).
- [ ] **Réseau** : Stack TCP/IP minimaliste.
- [ ] **Shell** : Interface utilisateur interactive.

### **Objectifs à Long Terme (v1.0)**
- [ ] **Compatibilité** : Boot sur UEFI.
- [ ] **Sécurité** : Mécanismes de protection mémoire (Paging).
- [ ] **Portabilité** : Support ARM (Raspberry Pi).

---

## **📚 Ressources Utiles**
- **Références** :
  - [OSDev Wiki](https://wiki.osdev.org/) (indispensable pour les OS bare metal).
  - [Intel Manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html) (architecture x86).
- **Outils** :
  - `objdump` : Pour analyser les binaires.
  - `xxd` : Pour inspecter les fichiers bruts.

---

## **📜 Licence**
MaxOS est distribué sous **licence MIT** (voir `LICENSE`).

---
**Auteurs** : [Votre Nom] | **Contact** : [votre@email.com]
**Dernière mise à jour** : `$(date +%Y-%m-%d)`
```

---

### **Points Clés de la Documentation**
1. **Professionnalisme** : Structure claire, sections bien définies.
2. **Précision** : Commandes exactes pour la compilation et les tests.
3. **Exhaustivité** : Roadmap détaillée et ressources externes.
4. **Adaptabilité** : Format Markdown compatible avec GitHub/GitLab.

Cette documentation peut être étendue avec des sections supplémentaires (ex : "Architecture du noyau", "Débogage avancé") si nécessaire.

---
*MaxOS AI v18.0*
