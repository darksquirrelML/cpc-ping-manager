# CPC Ping Manager

Keeps these Supabase projects from being auto-paused by pinging each one every
5 days via GitHub Actions, and shows their status on a simple webpage:

- **CPC Connect** (shared with Defect Tracker, Safety Violation Tracker, and
  CPC Site Reports — they're all on the same Supabase project) —
  `ihwgejsioutzcmkaaumi.supabase.co`
- **Vehicle Movement Dashboard** (pick-up schedule) —
  `lahrwbqnurklcsbkghic.supabase.co`

Only 2 Supabase projects, and 2 anon keys, are needed — even though this
covers 5 apps.

## How it works

- `.github/workflows/ping.yml` runs on a schedule (every 5 days) and can also
  be run manually.
- It runs `ping.py`, which sends a small authenticated request to each
  project's REST API. Any successful request counts as activity, which is
  what stops Supabase's free-tier "pause after inactivity" timer.
- The result of each ping is written to `status.json`, which the workflow
  commits back to the repo.
- `index.html` is a plain webpage that reads `status.json` and shows each
  project's status. GitHub Pages serves this file.

## One-time setup

Do these steps in order. None of them need any coding — just clicking
through GitHub and Supabase's websites.

### 1. Create the repo

1. Go to [github.com/new](https://github.com/new) while signed in as
   `darksquirrelml`.
2. Repository name: `cpc-ping-manager` (or whatever you'd like — just update
   the Pages URL below to match).
3. Make it **Public** (GitHub Pages needs this on a free account).
4. Create the repo, then upload all the files from this folder into it
   (drag-and-drop works on the GitHub website, or use `git push` if you're
   comfortable with that).

### 2. Get each project's "anon" API key

For **each** of the 2 Supabase projects:

1. Open [supabase.com/dashboard](https://supabase.com/dashboard) and select
   the project.
2. Go to **Project Settings** (gear icon) → **API**.
3. Under **Project API keys**, copy the key labeled **`anon` `public`**
   (not the `service_role` one).

You'll paste each of these into GitHub in the next step.

### 3. Add the keys as GitHub secrets

In your new repo on GitHub:

1. Go to **Settings** → **Secrets and variables** → **Actions**.
2. Click **New repository secret** and add each of these two, pasting in
   the matching anon key from step 2:

   | Secret name | Project |
   |---|---|
   | `CPC_CONNECT_ANON_KEY` | CPC Connect (shared with Defect Tracker, Safety Violation Tracker, CPC Site Reports) |
   | `VEHICLE_DASHBOARD_ANON_KEY` | Vehicle Movement Dashboard |

### 4. Let the workflow commit its results

1. In the repo, go to **Settings** → **Actions** → **General**.
2. Scroll to **Workflow permissions**.
3. Select **Read and write permissions**.
4. Click **Save**.

(This lets the ping workflow commit the updated `status.json` back to the
repo after each run.)

### 5. Turn on GitHub Pages

1. In the repo, go to **Settings** → **Pages**.
2. Under **Build and deployment** → **Source**, choose **Deploy from a
   branch**.
3. Branch: `main`, folder: `/ (root)`. Save.
4. GitHub will give you a URL — it'll be
   `https://darksquirrelml.github.io/cpc-ping-manager/` unless you renamed
   the repo.

### 6. Test it

1. In the repo, go to the **Actions** tab.
2. Click **Ping Supabase Projects** in the left sidebar.
3. Click **Run workflow** → **Run workflow** to trigger it manually (don't
   wait 5 days to find out if it works).
4. After it finishes (about 30 seconds), refresh your GitHub Pages URL —
   you should see both projects with green "Alive" badges.

If a project shows "Failed", double check the secret name matches the table
in step 3 exactly, and that you copied the `anon` key (not `service_role`).

## Adding another project later

Open `ping.py` and add another entry to the `PROJECTS` list at the top, e.g.:

```python
{
    "name": "Some New App",
    "ref": "xxxxxxxxxxxxxxxxxxxx",
    "secret_env": "SOME_NEW_APP_ANON_KEY",
},
```

Then add a matching `SOME_NEW_APP_ANON_KEY` secret (step 3 above) and add the
same env var line to `.github/workflows/ping.yml` under the `Ping projects`
step. No other changes needed — the webpage picks up new projects
automatically.
