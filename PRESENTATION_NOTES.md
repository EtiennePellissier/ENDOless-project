# Notes de presentation - checkpoint "Feasibility" (6 nov. 2026)

## 1. En une phrase (30 s)
"Nous avons pose le cadre pour decider du chemin technique : un banc d'essai reproductible pour comparer extraction par regles et petits modeles, un journal de decisions avec responsables, et le catalogue des etats d'interface."

## 2. Le probleme que la techno doit resoudre (1 min)
Transformer une phrase libre en entree structuree SANS rien inventer : distinguer hier / aujourd'hui, un score de son impact, une absence declaree d'un symptome non mentionne, garder "red wine" comme un seul concept. Rien n'est ecrit sans relecture et recu du backend.

## 3. Demo (2 min)
- `python3 -m bench.run_benchmark --system rules --model baseline`
- Montrer : precision/recall brute puis validee ; le cas C14 ("14 sur 10") est rejete par le validateur ; le cas C15 (negation "did not have pain") est un echec connu de la baseline -> justification d'un modele.
- Dire : la baseline est ecrite sur ces cas, son score est optimiste.

## 4. Ce qui est fait / pas fait (1 min)
Fait : harnais, cas, validateur, schema, journal de decisions, backlog, etats UX.
Pas fait : benchmark des 2 modeles (il faut un endpoint d'Andrei), mapping reel (dictionnaire de champs), relecteur nomme.

## 5. Decisions a demander aujourd'hui (1 min)
1. Andrei : dictionnaire de champs + endpoint/calcul pour la semaine du 13 nov. (D01, D03)
2. Alexandra : nom du relecteur medical et date. (D07)
3. Confirmer roles lead technique / lead UX, superviseur. (D10)
4. Confirmer demo du 20 nov. : "entree relue et enregistree avec recu + 1 reponse sourcee".

## 6. Questions probables
- *Pourquoi pas un gros modele via API ?* Contrainte France + pas de fallback externe.
- *Pourquoi valider apres le modele ?* Le modele peut halluciner un champ ou 14/10 ; l'autorite reste dans le code.
- *Le chatbot sauvegarde-t-il tout seul ?* Non : brouillon -> relecture -> Save -> recu backend, seul le recu affiche "Saved".
