# BOT-SHIELD

Bot Discord spécialisé dans la protection contre l'ajout de bots non autorisés.

## Fonctionnalités
- Détecte l'arrivée d'un compte bot.
- Cherche l'auteur de l'ajout dans les journaux d'audit Discord.
- Autorise le propriétaire du serveur et les IDs listés dans `ALLOWED_INVITER_IDS`.
- Expulse automatiquement un bot ajouté par un utilisateur non autorisé.
- Envoie les événements dans le salon de logs configuré ou dans la console.
- Commande `/shield-status` pour vérifier l'état et les permissions.
- Si l'auteur de l'ajout ne peut pas être identifié, le bot alerte sans expulser au hasard.

## Installation
Python 3.10 ou plus récent :

```bash
python -m venv .venv
# Windows : .venv\\Scripts\\activate
# Linux/macOS : source .venv/bin/activate
pip install -r requirements.txt
```

Copie `.env.example` vers `.env`, puis remplis uniquement les champs nécessaires :

```env
DISCORD_TOKEN=COLLE_TON_NOUVEAU_TOKEN_ICI
ALLOWED_INVITER_IDS=
LOG_CHANNEL_ID=0
```

Lance le bot avec `python bot.py`.

## Configuration Discord
Dans le portail développeur Discord, active l'intent privilégié **Server Members Intent**. Sur ton serveur, donne au bot les permissions **View Audit Log**, **Kick Members** et, si tu utilises un salon de logs, **Send Messages**. Place son rôle au-dessus des bots qu'il doit pouvoir expulser.

## Sécurité importante
- Ne publie jamais le fichier `.env` : il contient ton token privé.
- Le fichier `.env` est ignoré par Git grâce à `.gitignore`.
- Le dépôt contient seulement `.env.example`, un modèle sans secret.
- Un token déjà partagé doit être réinitialisé dans le Discord Developer Portal avant utilisation.
- Teste d'abord sur un serveur privé.

## Limites
BOT-SHIELD protège contre l'ajout de bots non autorisés. Il ne protège pas contre les autres actions de type nuke (suppression de salons, rôles, bannissements, etc.).