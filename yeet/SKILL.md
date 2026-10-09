---
name: yeet
description: Put a generated or built static site live at its own public subdomain, with a name like hungover-hyena unless the user picks one. Also lists and deletes sites deployed this way. Use when the user asks to deploy, publish, host, ship, yeet, or put a site online, or wants to see or clean up their deployed sites.
---

# yeet

`scripts/yeet.py` does the work. It talks to Netlify and reads the token from `~/.config/yeet/token`, or from `NETLIFY_AUTH_TOKEN` if that's set. Never ask for the token, and never read, print or write it yourself. Paths below are relative to this skill's folder.

## Deploy

1. **Find the folder.** It must contain `index.html`. For HTML you or the user wrote, deploy that folder. A project with a `build` script in `package.json` needs `npm install && npm run build` first, then you deploy the output folder. Astro and Vite write to `dist/`, CRA and SvelteKit to `build/`, Next export to `out/`, Eleventy to `_site/`. Never deploy the project root.

2. **Pick the name.** Use the user's name if they gave one, slugified to lowercase letters, digits and hyphens. To update a site you deployed earlier in this conversation, reuse its name with `--overwrite`. Otherwise pass no name and the script makes one up.

3. **Run it.**

   ```bash
   python3 <skill-dir>/scripts/yeet.py deploy <folder> [name] [--overwrite] [--spa | --no-spa]
   ```

   The last line it prints is the live URL. Along the way it:

   - skips hidden files and folders, except `.well-known/`, and skips `node_modules/`
   - spots single-page apps, meaning one HTML page that loads a bundle from `/assets/` or `/static/js/`, and makes unknown paths serve `index.html` so a refresh on `/about` still works. Pass `--spa` if it missed a client-routed app and `--no-spa` to switch the fallback off.
   - hides the "Powered by Netlify" badge. If it warns that this failed, give the user the link from the warning.

4. **Read the exit code.**

   - `0` means it worked.
   - `3` means the name already belongs to one of the user's sites. Ask before replacing it, and only rerun with `--overwrite` after a clear yes.
   - `4` means someone else owns the name. Ask the user for another, or rerun with no name.
   - `5` means the script uploaded nothing because the folder looked unsafe. Either it has a `package.json`, so it's probably a project root, or it holds files that look private, like `.env`, keys, certificates or databases. Show the user the files it listed and deploy the build output instead. Don't delete or move their files to get past the check. A leaked key is the one mistake here that can't be taken back.
   - `1` with "no token" means setup isn't done. Tell the user to create a personal access token at app.netlify.com under User settings, Applications, Personal access tokens, then save it with the command below. Don't ask them to paste it in chat.

     ```bash
     mkdir -p ~/.config/yeet && read -rsp 'token: ' t && printf '%s' "$t" > ~/.config/yeet/token && chmod 600 ~/.config/yeet/token
     ```

5. **Check it.** Before you say it worked, run `curl -sI <url>`. You want `200` and `content-type: text/html`.

6. **Report.** Give the URL as a link, and the name so the user can update the site later.

## List

```bash
python3 <skill-dir>/scripts/yeet.py list
```

Prints every site on the account with its name, URL and last update, newest first.

## Delete

Deleting is permanent, and anyone can grab the name afterwards. Show the user the exact names you're about to delete and wait for a clear yes on those names.

```bash
python3 <skill-dir>/scripts/yeet.py delete <name> [name...]
```

Exit `4` means one of the names isn't the user's. The script checks every name before deleting anything, so nothing was deleted.

## Requirements

Python 3, standard library only. Static sites only. Server code, API routes and server-side rendering won't run.
