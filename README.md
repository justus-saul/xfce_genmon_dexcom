# xfce-genmon-dexcom

Unofficial: shows your current Dexcom CGM glucose value (with trend arrow) in the Xfce4 panel using the
[Generic Monitor (genmon)](https://docs.xfce.org/panel-plugins/xfce4-genmon-plugin/start) plugin.

- Colored value + trend arrow in the panel (red/bold when out of range, green otherwise)
- Tooltip with trend description and age of the reading
- Units: `mg/dL` or `mmol/L`
- Languages: English (`en`) and German (`de`), easily extendable via `locales.json`

## Requirements

- Xfce4 with `xfce4-genmon-plugin`
- Python 3.9+
- A Dexcom account (Dexcom Share must be enabled in the Dexcom app, with at least one follower)
- [`pydexcom`](https://github.com/gagebenne/pydexcom)

## Setup

1. Install the genmon plugin:

   Arch/Manjaro:

   ```bash
   sudo pacman -S xfce4-genmon-plugin python git
   ```

   Debian/Ubuntu:

   ```bash
   sudo apt install xfce4-genmon-plugin python3-venv git
   ```

   Note: on Arch/Manjaro, `pip install` outside a virtual environment is blocked (PEP 668),
   so use the venv from the next step.

2. Clone the repository and install the dependency:

   ```bash
   git clone <repo-url> ~/Apps/xfce-genmon-dexcom
   cd ~/Apps/xfce-genmon-dexcom
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```

3. Create your config:

   ```bash
   cp config.example.json config.json
   ```

   Edit `config.json` and enter your credentials. `config.json` is git-ignored.

4. Test it:

   ```bash
   .venv/bin/python xfce_genmon_dexcom.py
   ```

   Expected output:

   ```
   <txt><span foreground="#4ade80">112 →</span></txt>
   <tool>Glucose: 112 mg/dL (steady)
   Time: 12:05 (3 min ago)</tool>
   ```

5. Add to the panel: right-click the panel → *Panel* → *Add New Items…* → *Generic Monitor*.
   Then open its properties and set:
   - **Command:** `/home/<user>/Apps/xfce-genmon-dexcom/.venv/bin/python /home/<user>/Apps/xfce-genmon-dexcom/dexcom_bar.py`
   - **Label:** disabled
   - **Period (s):** `60` (Dexcom updates roughly every 5 minutes; don't poll too aggressively)
   - **Font:** as you like

## Configuration (`config.json`)

| Key              | Description                                                                 | Default   |
|------------------|-----------------------------------------------------------------------------|-----------|
| `username`       | Dexcom account username, email or phone number (required)                   | –         |
| `password`       | Dexcom account password (required)                                          | –         |
| `region`         | `us` (USA), `ous` (outside USA) or `jp` (Japan)                             | `ous`     |
| `unit`           | `mg/dL` or `mmol/L`                                                         | `mg/dL`   |
| `lang`           | Language key from `locales.json` (`en`, `de`)                               | `de`      |
| `low_threshold`  | Values (mg/dL) below this are shown in red                                  | `70`      |
| `high_threshold` | Values (mg/dL) above this are shown in red                                  | `180`     |

## Adding a language

Copy the `en` block in `locales.json`, rename it to your language code and translate the values.
Then set `"lang"` accordingly in `config.json`.

## Security note

Your Dexcom password is stored in plain text in `config.json`. Restrict access:

```bash
chmod 600 config.json
```

## Disclaimer

This project is not affiliated with Dexcom. It is **not a medical device**, do not use it for
treatment decisions. Always rely on the official Dexcom app/receiver.

