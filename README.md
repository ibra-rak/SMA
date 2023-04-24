# SMA

## Présentation du travail réalisé

Ce projet de Systèmes Multi-Agents consistait en la modélisation d'une discussion argumentée entre deux agents, tentant d'atteindre un compromis, afin de choisir un véhicule. Nous avons donc implémenté ce système de deux manières différentes (l'une avantage dans l'esprit du cours comme nous le détaillerons), en nous assurant qu'un compromis était trouvé. Nous avons également souhaité pouvoir connecter notre solution à des données externes contenues dans un fichier ***.csv*** d'un certain format, désignant les choix des agents.

## Initialisation du modèle
### Avant-propos

Nous avons choisi de vous présenter deux fichiers, ***pw_argumentation.py*** et ***pw_arg.py***, car nous doutions de la meilleure manière de procéder afin de répondre au problème posé. Néanmoins, la méthode corrrespondant le mieux au cours semblant être cette du fichier ***pw_arg.py***, nous nous concentrerons principalement sur l'analyse de ce fichier.  
Les fonctions sont néanmoins sensiblement identiques, seuls leur déclenchement et leur gestion sont orchestrés différemment.

### Définition du modèle

Dans notre problème, le cadre du modèle est défini par :
- une liste d'items - dans notre cas, les voitures - dotés de caractéristiques
- un ensemble de critères et de valeurs que ces derniers peuvent prendre, qui permettront de discriminer les items lors de la conversation
- une liste d'agents communicants, devant discuter afin de choisir un item leur convenant. 

Nous nous sommes concentrés sur la problématique concernant deux agents uniquement, sachant qu'en utiliser plus consisterait à envoyer les messages sur une boite aux lettres (classe *Mailbox()*) commune, avec un tour de réponse prédéfini ou aléatoire des différents agents présents ; seuls les noms des agents changeraient visuellement, et la convergence serait sans doute plus complexe à atteindre.  

S'agissant de convergence, nous avons décidé de la forcer sur notre système en contraignant les agents à réaliser des compromis (paramètre ***self.mode***) ; cela signifie en pratique que les agents exclueront au fur et à mesure de la conversation les items sur lequels ils ont eu un désaccord, restreignant donc leur choix aux meilleurs éléments restants (contenus dans la liste ***self.items_not_concerned***). 

Le modèle fonctionne par un système de tours (paramètre ***self.turn***) permettant de s'assurer qu'un seul des agents interagisse à chaque *step* ; par ailleurs, nous nous sommes assurés (condition *turn%2==0* et *turn+=1* à chaque pas) qu'il y avait bien alternance de l'intervention des agents pour assurer un échange.

L'arrêt de l'algorithme, en cas de convergence, est assuré par le paramètre ***self.dispute*** qui permet l'arrêt lorsqu'un accord est atteint ; un double-COMMIT est alors échangé.

### Définition des agents

Quant aux agents, ils sont définis par :
- un ordre de priorité concernant les critères : ils ont leurs préférences
- une évaluation personnelle de la qualité (=valeurs) des critères pour chacun des items

Concernant les préférences entre critères des agents, elles sont définies par la méthode ***generate_preferences()*** de la classe *ArgumentAgent* prenant facultativement en argument une liste ordonnée des critères pour l'agent - il aurait été possible de dissocier cette tâche du reste de la fonction mais nous souhaitions réaliser toutes les tâches de gestion de préférences en simultané.  

En guise d'exemple pour la suite du problème, les fichiers ***templateSMA.csv*** et ***templateSMA2.csv*** continennent tous deux une évaluation personnelle des critères de chaque item par chacun des deux agents :
- les colonnes ***Car name*** et ***Description*** correspondent aux description des Items ; générés aléatoirement dans le cadre du projet.
- les colonnes contenues entre ***Cout_prod1*** et ***Environnement1*** incluses correspondent à l'évaluation de chaque critère de chaque Item par l'Agent 1 : les valeurs s'étendent de 0 (correspondant à une valeur très mauvaise, autrement dit *Value.VERY_BAD*) à 4 (pour *Value.VERY_GOOD*).
- de la même façon, les colonnes contenues entre ***Cout_prod2*** et ***Environnement2*** incluses correspondent à l'évaluation de chaque critère de chaque Item par l'Agent 2
En respectant ces formats, il est possible de faire comparer alors plusieurs dizaines de véhicules par nos agents.

## Fonctionnement du modèle

### Articulation de l'échange

L'articulation de l'échange a été implementée sous la forme d'un arbre de décision basé sur la MessagePerformative du message reçu par l'agent devant répondre ; autrement dit :
- si le message recu est une ***proposition*** (PROPOSE), l'agent peut l'accepter (ACCEPT), si l'item remplit les critères attendus, auquel cas ***self.dispute*** permet de conclure. Si l'agent n'est pas convaincu, il envoie un ASK_WHY
- si le message recu est un ASK_WHY, l'agent doit donc se justifier. Pour cela, il recherche un argument support de l'item grâce à la méthode agent ***support_proposal*** : si l'argument est vide (None), il proposera alors un nouvel item (sous reserve de ***self.mode=True***), sinon il défendra son item en argumentant (ARGUE).
- si le message reçu est un ARGUE, il convient tout d'abord de s'assurer de son positionnement et de celui de son interlocuteur : quatre possiblités s'offrent alors à nous, de l'acceptation (si les deux acteurs sont alignés), aux propositions et à l'argumentation.


### Interaction entre agents 

Tout d'abord, nous avons du décider d'un critère selon lequel un agent accepterait une proposition ; ce critère a été de cibler le top 10 % des véhicules ***restants*** (comme mentionné plus haut). Autrement, l'agent la refuse. Cette technique a été choisie de manière arbitraire pour assurer la convergence, mais d'autres existent également.  
Les agents vont donc, à tour de rôle, réaliser des propositions en faveur d'items, étayés par des arguments concernant les critères et leur valeur.
Concernant le débat, lorsque l'agent refuse la proposition, grâce à la fonction *attack_proposal*, nous testons, par ordre d'apparition nous semblant sémantiquement et argumentativement cohérent, deux réponses argumentatives potentielles :
- la différence de point de vue des deux agents : si l'agent A souhaite la voiture V parce qu'un critère *c* est bon à ses yeux, et que le critère *c* est mauvais pour l'agent B, celui-ci refusera la proposition (si l'item n'est pas dans ses meilleurs choix) car l'argument ne marche pas pour lui
- la différence de priorités entre agents : si l'agent A se base sur un certain critère pour son argumentaire, qui est moins important qu'un autre mal noté aux yeux de l'agent B, celui-ci refusera la proposition 
Dans le cas où l'agent souhaiterait refuser la proposition sans pouvoir invoquer l'une ou l'autre de ces argumentations, il proposera alors un nouvel item.

### Visualisation de l'échange par l'utilisateur

L'utilisateur peut visualiser l'échange de la manière suivante, sur son terminal :

![image](https://user-images.githubusercontent.com/104861612/233891432-0f421aa4-e93c-42e6-bc9b-63dc1c75e52b.png)

L'alternance est bien respectée, ainsi que la logique de l'échange et des performatives.

## Résultats et ouverture

### Résultats statistiques

Comme visualisé plus haut, les résolutions faciles et rapides (correspondant au fichier ***templateSMA.csv***, résolution en 5 tours) sont envisageables mais pas systématiques (comme en témoigne le fichier ***templateSMA2.csv***, resolution en 162 tours). En remplaçant les indices de la liste ***pvalues*** par *random.randint(O,4)* (lignes 111/112, pw_arg.py), on peut réaliser une analyse statistique du nombre de tours nécéssaires à une convergence. On obtient, pour environ 50 essais, la distribution suivante : 

![image](https://user-images.githubusercontent.com/104861612/233893813-51097a38-7227-4ac0-9d3f-938b78979f86.png)

On se rend également compte que, tandis que pour ***self.mode=True*** on obtient 100% de convergences, elles demeurent rares pour ***self.mode=False*** d'où la nécessité de ce paramètre.
