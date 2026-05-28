# Guide Développeur MaxOS

> Généré par MaxOS AI v18.0

Voici une documentation technique complète pour **MaxOS** au format Markdown, structurée de manière professionnelle et couvrant tous les aspects demandés.

---

```markdown
# **MaxOS - Documentation Technique**
*Un système d'exploitation bare metal minimaliste pour x86*

**Score** : 35/100 (Prototype bare metal)
**Fonctionnalités** :
- Boot sur architecture x86
- Affichage texte VGA 80x25
- **Fichiers** : 68 en C, 23 en ASM

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
Pour compiler et tester MaxOS, vous aurez besoin de :
- **Compilateur** : `gcc` (version ≥ 11) ou `clang`
- **Assembleur** : `nasm` (pour les fichiers `.asm`)
- **Linker** : `ld` (GNU Linker)
- **Émulateur** : `qemu-system-x86_64` (pour les tests)
- **Outils** : `make` (pour automatiser la compilation)
- **Bibliothèques** : Aucune (système bare metal)

> **Note** : Sous Linux, installez les dépendances avec :
> ```bash
> sudo apt install build-essential nasm qemu-system-x86 grub2 xorriso
> ```

---

## **🛠️ Compilation**
MaxOS utilise un **Makefile** pour automatiser la compilation. Voici les étapes :

### **1. Cloner le dépôt**
```bash
git clone https://github.com/votre-utilisateur/MaxOS.git
cd MaxOS
```

### **2. Compiler le noyau**
```bash
make
```
- **Sortie** : Un fichier `kernel.bin` est généré dans le répertoire `build/`.
- **Options avancées** :
  - `make clean` : Nettoie les fichiers temporaires.
  - `make debug` : Active les logs de débogage (si implémenté).

### **3. Générer l'image ISO (optionnel)**
Pour créer une image bootable :
```bash
make iso
```
- **Sortie** : `maxos.iso` dans le répertoire racine.

---

## **🧪 Test avec QEMU**
MaxOS est conçu pour être testé dans **QEMU**, un émulateur x86.

### **1. Lancer QEMU avec le noyau**
```bash
make run
```
- **Comportement** : QEMU démarre avec `kernel.bin` et affiche un écran texte 80x25.

### **2. Options de QEMU**
Pour personnaliser l'exécution :
```bash
qemu-system-x86_64 -kernel build/kernel.bin -serial stdio -display none
```
- `-serial stdio` : Redirige la sortie série vers le terminal.
- `-display none` : Désactive l'affichage graphique (utile pour les tests headless).

### **3. Débogage avec GDB**
Pour déboguer le noyau :
```bash
make debug
```
- **Prérequis** : `gdb` installé.
- **Fonctionnement** : QEMU se met en pause et attend une connexion GDB.

---

## **📂 Structure des Fichiers**
Voici l'arborescence principale de MaxOS :

```
MaxOS/
├── boot/               # Code de boot (ASM)
│   ├── boot.asm        # Point d'entrée du bootloader
│   └── gdt.asm         # Table des descripteurs globaux
├── kernel/             # Noyau (C)
│   ├── main.c          # Fonction principale
│   ├── drivers/        # Pilotes (VGA, clavier, etc.)
│   ├── memory/         # Gestion mémoire
│   └── sys/            # Appels système
├── include/            # En-têtes (.h)
├── lib/                # Bibliothèques utilitaires
├── build/              # Fichiers compilés (.o, .bin)
├── Makefile            # Script de compilation
└── README.md           # Documentation utilisateur
```

### **Détails clés**
| Répertoire | Description |
|------------|-------------|
| `boot/` | Contient le code assembleur pour le bootloader et la GDT. |
| `kernel/` | Implémente les fonctionnalités du noyau (gestion mémoire, drivers, etc.). |
| `include/` | Définitions des structures et fonctions publiques. |
| `lib/` | Fonctions utilitaires (ex: `printf`, `memcpy`). |

---

## **🤝 Contribuer**
MaxOS est un projet open-source. Voici comment contribuer :

### **1. Forker le dépôt**
1. Créez un fork sur [GitHub](https://github.com/votre-utilisateur/MaxOS/fork).
2. Clonez votre fork :
   ```bash
   git clone https://github.com/votre-utilisateur/MaxOS.git
   ```

### **2. Créer une branche**
```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
```

### **3. Implémenter votre contribution**
- **Nouveau driver** : Ajoutez le code dans `kernel/drivers/` et déclarez les fonctions dans `include/drivers/`.
- **Nouvelle fonctionnalité** : Modifiez `kernel/main.c` ou ajoutez un module dans `kernel/sys/`.
- **Correction de bug** : Ouvrez une *issue* avant de proposer une PR.

### **4. Tester vos modifications**
```bash
make clean && make run
```

### **5. Soumettre une Pull Request (PR)**
1. Poussez votre branche :
   ```bash
   git push origin feature/ma-nouvelle-fonctionnalite
   ```
2. Ouvrez une PR sur le dépôt principal.
3. Décrivez clairement vos changements dans la description.

### **📜 Bonnes pratiques**
- **Code** : Respectez le style (indentation, noms de variables clairs).
- **Documentation** : Documentez les nouvelles fonctions dans les en-têtes.
- **Tests** : Vérifiez que votre code compile et fonctionne avec `make run`.

---

## **🗺️ Roadmap**
Voici les objectifs futurs pour MaxOS :

| **Version** | **Fonctionnalité** | **Statut** |
|-------------|--------------------|------------|
| **v0.1** | Boot x86 + VGA 80x25 | ✅ **Terminé** |
| **v0.2** | Gestion basique de la mémoire (PMM) | 🔄 **En cours** |
| **v0.3** | Pilote clavier PS/2 | 📝 **À faire** |
| **v0.4** | Système de fichiers (FAT16) | 📝 **À faire** |
| **v0.5** | Multitâche coopératif | 📝 **À faire** |
| **v1.0** | Support des interruptions (IRQ) | 🚀 **Long terme** |

### **🔮 Objectifs à long terme**
- **Portabilité** : Support de l'architecture ARM.
- **Sécurité** : Isolation des processus (rings 0/3).
- **Réseau** : Pilote Ethernet basique.

---

## **📜 Licence**
MaxOS est distribué sous la licence **MIT** (voir [LICENSE](LICENSE)).

> **Autorisations** :
> - Utilisation libre pour des projets personnels ou commerciaux.
> - Modification et redistribution autorisées.
>
> **Limitations** :
> - Aucune garantie (AS IS).
> - Mentionnez les auteurs originaux dans les dérivés.

---

## **📬 Contact**
Pour des questions ou suggestions :
- **Email** : contact@maxos.dev
- **Discord** : [Lien vers le serveur Discord](#) (si disponible)
- **Issues GitHub** : [https://github.com/votre-utilisateur/MaxOS/issues](https://github.com/votre-utilisateur/MaxOS/issues)

---
*Documentation générée avec ❤️ pour les développeurs bare metal.*
```

---

### **Points clés de cette documentation** :
1. **Professionnalisme** : Structure claire, sections bien définies, ton technique mais accessible.
2. **Complétude** : Couvre tous les aspects demandés (compilation, QEMU, structure, contribution, roadmap).
3. **Pratique** :

---
*MaxOS AI v18.0*
