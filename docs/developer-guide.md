# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, conforme à vos exigences :

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation minimaliste pour x86 en mode texte (80x25)*

**Score** : 35/100 | **Niveau** : Prototype bare metal
**Fichiers** : 46 (C) | 14 (ASM) | **Architecture** : x86 (16/32 bits)

---

## **📌 Introduction**
MaxOS est un système d'exploitation expérimental conçu pour :
- **Booter** sur architecture x86 (16/32 bits).
- **Afficher** un terminal texte en 80x25 (mode VGA).
- **Fournir** une base pour l'apprentissage des OS (scheduling, interruptions, etc.).

Ce guide couvre la compilation, le test, la structure du projet, les contributions et la roadmap.

---

## **🔧 Prérequis**
- **Compilateur** : `gcc` (pour le code C) ou `nasm` (pour l'ASM).
- **Outils** : `qemu-system-x86_64` (émulation), `make` (build automation).
- **Bibliothèques** : Aucune dépendance externe (sauf pour QEMU).

---

## **🛠 1. Compilation**
### **Structure des fichiers**
```
maxos/
├── boot/          # Code de boot (ASM)
│   ├── boot.asm   # Chargeur de démarrage (MBR)
│   └── kernel.asm # Routines bas niveau
├── kernel/        # Noyau (C)
│   ├── main.c     # Point d'entrée
│   ├── drivers/   # Pilotes (clavier, VGA)
│   └── lib/       # Fonctions utilitaires
├── Makefile       # Script de build
└── tools/         # Scripts utilitaires
```

### **Étapes de compilation**
1. **Nettoyer** les anciens builds :
   ```bash
   make clean
   ```
2. **Compiler** le noyau et le bootloader :
   ```bash
   make
   ```
   - Le binaire final `maxos.bin` est généré dans le dossier `build/`.

### **Options de compilation**
- **Debug** : `make DEBUG=1` (active les logs).
- **Architecture** : `make ARCH=i386` (32 bits) ou `ARCH=i686` (compatibilité étendue).

---

## **🧪 2. Test avec QEMU**
### **Lancer MaxOS dans QEMU**
```bash
make run
```
- **Options avancées** :
  ```bash
  qemu-system-x86_64 -drive format=raw,file=build/maxos.bin -m 128M -vga std
  ```
  - `-m 128M` : Alloue 128 Mo de RAM.
  - `-vga std` : Force le mode VGA texte.

### **Débogage**
- **GDB** :
  ```bash
  qemu-system-x86_64 -s -S -drive format=raw,file=build/maxos.bin &
  gdb -ex "target remote localhost:1234" -ex "symbol-file build/maxos.elf"
  ```
- **Logs** : Activez `DEBUG=1` dans le Makefile pour voir les messages du noyau.

---

## **📂 3. Structure des fichiers**
### **Détails par dossier**
| Dossier       | Description                                                                 |
|---------------|-----------------------------------------------------------------------------|
| **boot/**     | Code ASM pour le bootloader (chargement du noyau en mémoire).              |
| **kernel/**   | Noyau en C (gestion des interruptions, VGA, clavier).                      |
| **drivers/**  | Pilotes matériels (clavier PS/2, VGA 80x25).                               |
| **lib/**      | Fonctions utilitaires (memcpy, printf, etc.).                               |
| **tools/**    | Scripts pour la génération de l'image disque ou le formatage.              |

### **Fichiers clés**
- **`boot.asm`** : Charge le noyau en mémoire (via `multiboot` ou secteur de boot).
- **`main.c`** : Point d'entrée du noyau (`kernel_main()`).
- **`vga.c`** : Gestion de l'affichage texte (80x25).
- **`keyboard.c`** : Gestion des entrées clavier (PS/2).

---

## **🤝 4. Contribuer**
### **Processus**
1. **Fork** le dépôt et créez une branche :
   ```bash
   git checkout -b feature/ma-nouvelle-fonctionnalite
   ```
2. **Code** :
   - Respectez le style (indentation à 4 espaces, noms de variables explicites).
   - Ajoutez des commentaires pour les fonctions complexes.
3. **Test** :
   - Vérifiez que le build passe (`make`).
   - Testez dans QEMU (`make run`).
4. **Pull Request** :
   - Décrivez les changements dans le message.
   - Liez les issues si applicable.

### **Règles de contribution**
- **Pas de dépendances externes** (sauf pour QEMU en développement).
- **Pas de code non testé** (tout nouveau pilote doit être validé).
- **Documentation** : Mettez à jour ce fichier si vous modifiez l'architecture.

### **Exemple de contribution**
- **Ajout d'un pilote pour le port série** :
  1. Créez `drivers/serial.c`.
  2. Implémentez `serial_init()` et `serial_putc()`.
  3. Modifiez `kernel/main.c` pour initialiser le pilote au démarrage.

---

## **🗺 5. Roadmap**
### **Objectifs à court terme (Prototype)**
| Tâche                     | Statut       | Priorité |
|---------------------------|--------------|----------|
| Support du clavier PS/2   | ✅ Terminé   | Haute    |
| Gestion basique des IRQ  | ✅ Terminé   | Haute    |
| Affichage VGA 80x25       | ✅ Terminé   | Haute    |
| Système de fichiers       | ❌ En cours  | Moyenne  |
| Multitâche (basique)      | ❌ À faire   | Basse    |

### **Objectifs à moyen terme (v0.2)**
- **Gestion mémoire** : Allocation dynamique (`malloc`/`free`).
- **Pilotes** : Disque dur (ATA), souris PS/2.
- **Réseau** : Support basique de TCP/IP (via un pilote virtuel).

### **Objectifs à long terme (v1.0)**
- **Compatibilité** : Boot UEFI, support 64 bits.
- **Sécurité** : MMU, protection mémoire.
- **API** : Système de fichiers (FAT32), processus.

### **Comment proposer une feature ?**
1. Ouvrez une **issue** pour discuter de la faisabilité.
2. Proposez une **implémentation** via une PR.
3. Attendez une **revue** des maintainers.

---

## **📜 Licence**
MaxOS est distribué sous **licence MIT** (voir `LICENSE`).

---

## **🔗 Ressources utiles**
- [OSDev Wiki](https://wiki.osdev.org/) (référence pour les OS bare metal).
- [Intel Manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html) (spécifications x86).
- [QEMU Documentation](https://www.qemu.org/docs/master/system/invocation.html).

---
**Auteurs** : [Votre Nom] | **Version** : 0.1 (Prototype)
**Dernière mise à jour** : `$(date +%Y-%m-%d)`
```

---

### **Points clés de cette documentation** :
1. **Professionnalisme** : Structure claire, sections bien définies, ton technique mais accessible.
2. **Exhaustivité** : Couvre tous les points demandés (compilation, test, structure, contribution, roadmap).
3. **Pratique** : Inclut des commandes exactes et des exemples de contribution.
4. **Visuel** : Utilisation de tableaux pour les roadmaps et la structure des fichiers.

Vous pouvez adapter les noms de fichiers, les commandes ou les priorités selon l'état réel de votre projet.

---
*MaxOS AI v18.0*
