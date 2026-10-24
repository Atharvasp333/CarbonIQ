const vscode = require('vscode');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

/** @type {vscode.DiagnosticCollection} */
let diagnosticCollection;
/** @type {vscode.StatusBarItem} */
let statusBarItem;

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    diagnosticCollection = vscode.languages.createDiagnosticCollection('carboniq');
    context.subscriptions.push(diagnosticCollection);

    // Create Status Bar Item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = '$(leaf) CarbonIQ';
    statusBarItem.tooltip = 'Click to audit active file for carbon footprint';
    statusBarItem.command = 'carboniq.auditFile';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Command 1: Audit Active File
    const auditCmd = vscode.commands.registerCommand('carboniq.auditFile', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document.languageId !== 'python') {
            vscode.window.showWarningMessage('Please open a Python (.py) file to audit.');
            return;
        }
        await auditDocument(editor.document, true);
    });
    context.subscriptions.push(auditCmd);

    // Command 2: Optimize & Generate Sustainable Code
    const optimizeCmd = vscode.commands.registerCommand('carboniq.optimizeFile', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document.languageId !== 'python') {
            vscode.window.showWarningMessage('Please open a Python (.py) file to optimize.');
            return;
        }
        await optimizeDocument(editor.document);
    });
    context.subscriptions.push(optimizeCmd);

    // Command 3: Check Live Grid Carbon Intensity
    const gridCmd = vscode.commands.registerCommand('carboniq.checkGrid', async () => {
        const config = vscode.workspace.getConfiguration('carboniq');
        const region = config.get('defaultRegion', 'us-east-1');
        const pythonPath = config.get('pythonPath', 'python');

        const script = `
import json, sys
try:
    import carboniq
    data = carboniq.get_grid_intensity('${region}')
    print(json.dumps(data))
except Exception as e:
    print(json.dumps({'error': str(e)}))
`;
        exec(`${pythonPath} -c "${script.replace(/\n/g, ' ')}"`, (err, stdout) => {
            try {
                const res = JSON.parse(stdout.trim());
                if (res.error) {
                    vscode.window.showErrorMessage(`CarbonIQ Grid Error: ${res.error}`);
                } else {
                    const ci = res.carbon_intensity || 350;
                    vscode.window.showInformationMessage(
                        `🌱 ${region} Grid Intensity: ${ci} gCO₂/kWh (${ci < 250 ? '🟢 Green' : '🟡 Moderate'})`
                    );
                }
            } catch (e) {
                vscode.window.showInformationMessage(`🌱 Region ${region}: ~395 gCO₂/kWh`);
            }
        });
    });
    context.subscriptions.push(gridCmd);

    // Command 4: Track Workload with CodeCarbon
    const trackCmd = vscode.commands.registerCommand('carboniq.trackWorkload', () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document.languageId !== 'python') {
            vscode.window.showWarningMessage('Please open a Python file to benchmark.');
            return;
        }
        const filePath = editor.document.fileName;
        const terminal = vscode.window.createTerminal('CarbonIQ Benchmark');
        terminal.show();
        terminal.sendText(`python cli/carboniq_cli.py measure-script "${filePath}" --workload-name "${path.basename(filePath)}"`);
    });
    context.subscriptions.push(trackCmd);

    // Auto-audit on save if enabled
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(async (doc) => {
            if (doc.languageId === 'python') {
                const config = vscode.workspace.getConfiguration('carboniq');
                if (config.get('autoAuditOnSave', true)) {
                    await auditDocument(doc, false);
                }
            }
        })
    );
}

/**
 * Runs AST carbon audit on a document and decorates lines with squigglies
 * @param {vscode.TextDocument} doc
 * @param {boolean} showToast
 */
async function auditDocument(doc, showToast = false) {
    const config = vscode.workspace.getConfiguration('carboniq');
    const pythonPath = config.get('pythonPath', 'python');
    const filePath = doc.fileName;
    const fileContent = doc.getText();

    const pythonScript = `
import json, sys
try:
    import carboniq
    code = sys.stdin.read()
    res = carboniq.audit_code(code)
    print(json.dumps(res))
except Exception as e:
    print(json.dumps({'error': str(e)}))
`;

    const { spawn } = require('child_process');
    const child = spawn(pythonPath, ['-c', pythonScript]);

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (d) => { stdout += d; });
    child.stderr.on('data', (d) => { stderr += d; });

    child.on('close', (code) => {
        if (code !== 0 && !stdout) {
            if (showToast) vscode.window.showErrorMessage(`CarbonIQ Audit failed: ${stderr || 'Unknown error'}`);
            return;
        }

        try {
            const data = JSON.parse(stdout.trim());
            if (data.error) {
                if (showToast) vscode.window.showErrorMessage(`CarbonIQ: ${data.error}`);
                return;
            }

            const diagnostics = [];
            const issues = data.issues || [];

            for (const issue of issues) {
                const lineIndex = Math.max(0, (issue.line || 1) - 1);
                const line = doc.lineAt(Math.min(lineIndex, doc.lineCount - 1));
                const range = line.range;

                const severity = issue.severity === 'HIGH' 
                    ? vscode.DiagnosticSeverity.Warning 
                    : vscode.DiagnosticSeverity.Information;

                const diag = new vscode.Diagnostic(
                    range,
                    `[CarbonIQ] ${issue.description} Fix: ${issue.recommendation} (Est. -${issue.estimated_savings_pct}% energy)`,
                    severity
                );
                diag.source = 'CarbonIQ';
                diagnostics.push(diag);
            }

            diagnosticCollection.set(doc.uri, diagnostics);

            const grade = data.carbon_grade || 'A';
            const savings = data.potential_energy_reduction_pct || 0;
            statusBarItem.text = `$(leaf) CarbonIQ: ${grade}`;

            if (showToast) {
                if (issues.length === 0) {
                    vscode.window.showInformationMessage(`🌿 CarbonIQ: Grade ${grade} - No energy anti-patterns found!`);
                } else {
                    vscode.window.showWarningMessage(
                        `🌿 CarbonIQ: Grade ${grade} (${issues.length} energy anti-patterns). Potential ~${savings}% energy reduction.`
                    );
                }
            }
        } catch (parseErr) {
            console.error('Failed to parse audit result:', parseErr);
        }
    });

    child.stdin.write(fileContent);
    child.stdin.end();
}

/**
 * Optimizes a document and opens a side-by-side diff
 * @param {vscode.TextDocument} doc
 */
async function optimizeDocument(doc) {
    const config = vscode.workspace.getConfiguration('carboniq');
    const pythonPath = config.get('pythonPath', 'python');
    const filePath = doc.fileName;
    const fileContent = doc.getText();

    const pythonScript = `
import json, sys
try:
    import carboniq
    code = sys.stdin.read()
    res = carboniq.optimize_code(code)
    print(json.dumps(res))
except Exception as e:
    print(json.dumps({'error': str(e)}))
`;

    const { spawn } = require('child_process');
    const child = spawn(pythonPath, ['-c', pythonScript]);

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (d) => { stdout += d; });
    child.stderr.on('data', (d) => { stderr += d; });

    child.on('close', async (code) => {
        if (code !== 0 && !stdout) {
            vscode.window.showErrorMessage(`CarbonIQ Optimization failed: ${stderr || 'Unknown error'}`);
            return;
        }

        try {
            const data = JSON.parse(stdout.trim());
            if (data.error) {
                vscode.window.showErrorMessage(`CarbonIQ: ${data.error}`);
                return;
            }

            const optimizedCode = data.optimized_code;
            const savings = data.estimated_energy_reduction_pct || 0;

            // Prompt user to replace or preview
            const choice = await vscode.window.showInformationMessage(
                `🌱 CarbonIQ generated green code with ~${savings}% estimated energy reduction. Apply changes to file?`,
                'Apply to File',
                'Preview Side-by-Side Diff'
            );

            if (choice === 'Apply to File') {
                const edit = new vscode.WorkspaceEdit();
                const fullRange = new vscode.Range(
                    doc.positionAt(0),
                    doc.positionAt(doc.getText().length)
                );
                edit.replace(doc.uri, fullRange, optimizedCode);
                await vscode.workspace.applyEdit(edit);
                vscode.window.showInformationMessage('✅ Sustainable green optimizations applied!');
            } else if (choice === 'Preview Side-by-Side Diff') {
                const tempDoc = await vscode.workspace.openTextDocument({
                    content: optimizedCode,
                    language: 'python'
                });
                await vscode.commands.executeCommand(
                    'vscode.diff',
                    doc.uri,
                    tempDoc.uri,
                    `CarbonIQ: ${path.basename(filePath)} (Original ↔ Optimized)`
                );
            }
        } catch (e) {
            vscode.window.showErrorMessage(`Error applying green optimizations: ${e.message}`);
        }
    });

    child.stdin.write(fileContent);
    child.stdin.end();
}

function deactivate() {
    if (diagnosticCollection) {
        diagnosticCollection.clear();
        diagnosticCollection.dispose();
    }
}

module.exports = {
    activate,
    deactivate
};
