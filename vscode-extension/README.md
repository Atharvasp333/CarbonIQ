# CarbonIQ - VS Code Extension

Analyze and generate sustainable, low-carbon Python code directly inside Visual Studio Code.

---

## 🌟 Key Features

1. **Inline Carbon Linting**:
   - Analyzes Python files for energy anti-patterns ($O(N^2)$ loops, memory-bloating lists, un-memoized recursion).
   - Highlights inefficient lines with squiggly warnings and energy reduction tooltips.
   - Automatically runs on file save (`Ctrl+S`).

2. **One-Click Sustainable Code Generation**:
   - Right-click anywhere in a Python file -> **"CarbonIQ: Generate Sustainable Green Code (Refactor)"**.
   - Review side-by-side Diff or apply vectorization and caching optimizations directly.

3. **Status Bar Carbon Grade**:
   - Shows active file's sustainability rating (`🌿 CarbonIQ: Grade A`) in the status bar.

4. **Live Grid Intensity Checker**:
   - Check real-time regional carbon intensity (gCO₂/kWh) with `Ctrl+Shift+P` -> `CarbonIQ: Check Live Electric Grid Carbon Intensity`.

---

## 🚀 How to Run & Test in Development

1. Open this repository in Visual Studio Code.
2. Ensure you have the `carboniq` Python SDK installed:
   ```bash
   pip install -e .
   ```
3. Open `vscode-extension/extension.js` in VS Code.
4. Press **`F5`** (or go to `Run and Debug` -> `Run Extension`).
5. A new **Extension Development Host** VS Code window will open with the CarbonIQ extension activated!
6. In that window, open [`examples/inefficient_example.py`](file:///c:/Users/Admin/OneDrive/Documents/GitHub/CarbonIQ/examples/inefficient_example.py):
   - You will see the status bar show `🌿 CarbonIQ: Grade F (Severe Carbon Intensity)`.
   - Right-click -> **"CarbonIQ: Generate Sustainable Green Code (Refactor)"** to preview and apply the green code!

---

## ⚙️ Configuration Settings

- `carboniq.pythonPath`: Python executable path (default: `python`).
- `carboniq.autoAuditOnSave`: Automatically audit files on save (default: `true`).
- `carboniq.defaultRegion`: Default electric grid region for live intensity queries (default: `us-east-1`).
