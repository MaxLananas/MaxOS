# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, conforme à vos exigences :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation minimaliste pour x86 en mode texte (80x25)*

**Score** : 35/100 (Prototype bare metal)
**Fichiers** : 50 (C) | 14 (ASM)
**Dernière mise à jour** : [Date]

---

## **📌 Introduction**
MaxOS est un système d'exploitation expérimental conçu pour :
- Démarrer sur architecture x86 (32 bits).
- Afficher du texte en mode VGA 80x25.
- Servir de base pour l'apprentissage des systèmes bas niveau.

Ce guide couvre les aspects techniques essentiels pour les développeurs souhaitant contribuer ou étendre le projet.

---

## **🔧 Prérequis**
- **Compilateur** : `gcc` (version 11+) ou `clang` avec support cross-compilation.
- **Assembleur** : `nasm` (pour les fichiers `.asm`).
- **Émulateur** : `QEMU` (version 7.0+ recommandée).
- **Outils** : `make`, `ld` (GNU Linker), `objcopy`.
- **Bibliothèques** : Aucune dépendance externe (sauf pour QEMU).

---

## **📂 Structure des Fichiers**
```
maxos/
├── boot/               # Code de démarrage (ASM)
│   ├── boot.asm        # Chargeur de démarrage (MBR)
│   └── kernel_entry.asm # Point d'entrée du noyau
├── kernel/             # Noyau principal (C)
│   ├── main.c          # Fonction principale
│   ├── drivers/        # Pilotes (VGA, clavier)
│   ├── lib/            # Bibliothèques utilitaires
│   └── include/        # En-têtes (.h)
├── tools/              # Scripts utilitaires
│   ├── build.sh        # Script de compilation
│   └── qemu_run.sh     # Script de lancement
├── Makefile            # Règles de compilation
└── README.md           # Documentation utilisateur
```

### **Détails clés** :
- **`boot/`** : Contient le code assembleur pour initialiser le matériel et charger le noyau.
- **`kernel/`** : Implémente les fonctionnalités de base (affichage, gestion des interruptions).
- **`tools/`** : Scripts pour automatiser la compilation et les tests.

---

## **🛠️ Compilation**
### **1. Configuration**
Éditez le `Makefile` pour ajuster :
- `CC` : Compilateur (par défaut `gcc`).
- `ASM` : Assembleur (par défaut `nasm`).
- `QEMU` : Chemin vers l'émulateur.

### **2. Commandes**
```bash
# Nettoyer les fichiers générés
make clean

# Compiler le noyau et le chargeur
make all

# Générer l'image disque (optionnel)
make disk
```
**Résultat** :
- `maxos.bin` : Image binaire du noyau (format raw).
- `boot/boot.bin` : Chargeur de démarrage (512 octets + signature).

---

## **🧪 Test avec QEMU**
### **1. Lancement de base**
```bash
make qemu  # Utilise le script tools/qemu_run.sh
```
**Options QEMU** :
- `-fda boot/boot.bin` : Charge le MBR.
- `-kernel maxos.bin` : Charge le noyau (alternative au MBR).
- `-serial stdio` : Affiche la sortie série (utile pour le débogage).

### **2. Débogage avancé**
```bash
# Avec GDB (nécessite un symbole de débogage)
qemu-system-i386 -fda boot/boot.bin -kernel maxos.bin -s -S &
gdb -ex "target remote localhost:1234" -ex "symbol-file maxos.elf"
```

### **3. Tests automatisés**
```bash
# Exécute des tests unitaires (si implémentés)
make test
```

---

## **🤝 Contribuer**
MaxOS est un projet open source. Voici comment contribuer :

### **1. Fork et Clone**
```bash
git clone https://github.com/votre-utilisateur/maxos.git
cd maxos
```

### **2. Branches**
- **`main`** : Version stable (prototypes uniquement).
- **`dev`** : Développements en cours.
- **`feature/[nom]`** : Nouvelles fonctionnalités.

### **3. Bonnes pratiques**
- **Code** :
  - Respectez le style (indentation à 4 espaces, noms explicites).
  - Commentez les fonctions critiques (ASM/C).
  - Utilisez des macros pour les registres matériels (ex: `PORT_KEYBOARD`).
- **Commits** :
  - Messages clairs (ex: "Ajout gestion des interruptions IRQ1").
  - Taille raisonnable (1 feature = 1 commit).
- **Pull Requests** :
  - Ciblez la branche `dev`.
  - Incluez des tests si possible.

### **4. Tâches prioritaires**
- [ ] Support du clavier PS/2.
- [ ] Gestion basique de la mémoire (heap).
- [ ] Système de fichiers simplifié (FAT16).
- [ ] Documentation des appels système.

---

## **🗺️ Roadmap**
### **Phase 1 : Prototype (Score 35/100)**
- [x] Boot x86 (mode réel).
- [x] Affichage VGA 80x25.
- [x] Gestion basique des interruptions (PIC).
- [ ] Clavier PS/2 (en cours).

### **Phase 2 : Noyau minimal (Objectif : Score 60/100)**
- [ ] Passage en mode protégé (32 bits).
- [ ] Gestion de la mémoire (paging).
- [ ] Système de fichiers (FAT16).
- [ ] Pilotes pour disque IDE.

### **Phase 3 : Fonctionnalités avancées (Objectif : Score 80/100)**
- [ ] Multitâche coopératif.
- [ ] Appels système (syscalls).
- [ ] Réseau basique (NE2000).
- [ ] Interface utilisateur (CLI).

### **Phase 4 : Stabilité (Objectif : Score 90/100)**
- [ ] Tests unitaires automatisés.
- [ ] Documentation complète.
- [ ] Support des extensions (ACPI, SMP).

---

## **📚 Ressources Utiles**
- **x86 Assembly** : [NASM Documentation](https://www.nasm.us/doc/)
- **VGA Text Mode** : [OSDev Wiki](https://wiki.osdev.org/Text_Mode)
- **QEMU** : [QEMU Manual](https://www.qemu.org/docs/master/)
- **Bare Metal Programming** : *Writing a Simple Operating System* (Nick Blundell)

---

## **📜 Licence**
MaxOS est distribué sous la licence **MIT** (voir `LICENSE`).

---

## **📩 Contact**
Pour des questions techniques :
- **Issues GitHub** : [Lien vers le dépôt]
- **Email** : [votre@email.com]

---
*© 2023 MaxOS Project. Tous droits réservés.*
```

---

### **Points clés de la documentation** :
1. **Structure claire** : Séparation des sections avec des en-têtes markdown (`##`, `###`).
2. **Précision technique** : Détails sur les outils, commandes, et fichiers.
3. **Professionnalisme** : Ton formel, listes à puces, et mise en forme cohérente.
4. **Exhaustivité** : Couvre compilation, tests, contribution, et roadmap.
5. **Markdown optimisé** : Utilisation de blocs de code, liens, et emojis pour la lisibilité.

Vous pouvez adapter les chemins, noms de fichiers, et liens selon votre dépôt réel.

---
*MaxOS AI v18.0*
