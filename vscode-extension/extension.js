const vscode = require('vscode');
const { exec, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

/** @type {vscode.DiagnosticCollection} */
let diagnosticCollection;
/** @type {vscode.StatusBarItem} */
let statusBarItem;

/**
 * Resolves active workspace root path
 * @param {vscode.TextDocument} [doc]
 */
function getWorkspaceRoot(doc) {
    if (doc && doc.uri) {
        const wsFolder = vscode.workspace.getWorkspaceFolder(doc.uri);
        if (wsFolder) return wsFolder.uri.fsPath;
    }
    if (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0) {
        return vscode.workspace.workspaceFolders[0].uri.fsPath;
    }
    return path.resolve(__dirname, '..');
}

/**
 * Automatically detects python interpreter with carboniq installed
 * @param {string} wsRoot
 */
function getResolvedPythonPath(wsRoot) {
    const config = vscode.workspace.getConfiguration('carboniq');
    const configured = config.get('pythonPath', 'python');
    if (configured && configured !== 'python') {
        return configured;
    }

    // Auto-detect project virtualenvs
    if (wsRoot) {
        const candidates = [
            path.join(wsRoot, 'backend', 'venv', 'Scripts', 'python.exe'),
            path.join(wsRoot, 'backend', 'venv', 'bin', 'python'),
            path.join(wsRoot, '.venv', 'Scripts', 'python.exe'),
            path.join(wsRoot, '.venv', 'bin', 'python'),
            path.join(wsRoot, 'venv', 'Scripts', 'python.exe'),
            path.join(wsRoot, 'venv', 'bin', 'python')
        ];
        for (const cand of candidates) {
            if (fs.existsSync(cand)) {
                return cand;
            }
        }
    }
    return 'python';
}

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
        const editor = vscode.window.activeTextEditor;
        const wsRoot = getWorkspaceRoot(editor ? editor.document : null);
        const pythonPath = getResolvedPythonPath(wsRoot);

        const script = `
import json, sys, os
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ws = r"${wsRoot.replace(/\\/g, '\\\\')}"
if ws and ws not in sys.path:
    sys.path.insert(0, ws)
try:
    import carboniq
    data = carboniq.get_grid_intensity('${region}')
    print(json.dumps(data, ensure_ascii=True))
except Exception as e:
    print(json.dumps({'error': str(e)}, ensure_ascii=True))
`;
        exec(`${pythonPath} -c "${script.replace(/\n/g, ' ')}"`, {
            cwd: wsRoot,
            env: {
                ...process.env,
                PYTHONIOENCODING: "utf-8",
                PYTHONPATH: wsRoot ? `${wsRoot}${path.delimiter}${process.env.PYTHONPATH || ''}` : process.env.PYTHONPATH
            }
        }, (err, stdout) => {
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

    // Command 5: Direct Apply Optimizations
    const applyCmd = vscode.commands.registerCommand('carboniq.applyOptimizations', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.document.languageId !== 'python') return;
        await applyOptimizationsDirectly(editor.document);
    });
    context.subscriptions.push(applyCmd);

    // Register Quick Fix (CodeActionProvider)
    context.subscriptions.push(
        vscode.languages.registerCodeActionsProvider(
            { language: 'python' },
            {
                provideCodeActions(document, range, context) {
                    const carboniqDiagnostics = (context.diagnostics || []).filter(d => d.source === 'CarbonIQ');
                    if (carboniqDiagnostics.length === 0) return [];

                    const actions = [];

                    // Action 1: Preview Greener Alternative (Side-by-Side Diff)
                    const previewAction = new vscode.CodeAction(
                        '🌱 CarbonIQ: Preview Greener Alternative (Side-by-Side Diff)',
                        vscode.CodeActionKind.QuickFix
                    );
                    previewAction.command = {
                        command: 'carboniq.optimizeFile',
                        title: 'Preview Greener Alternative'
                    };
                    previewAction.diagnostics = carboniqDiagnostics;
                    previewAction.isPreferred = true;
                    actions.push(previewAction);

                    // Action 2: Apply Green Optimizations Directly
                    const applyAction = new vscode.CodeAction(
                        '⚡ CarbonIQ: Apply Sustainable Refactoring to File',
                        vscode.CodeActionKind.QuickFix
                    );
                    applyAction.command = {
                        command: 'carboniq.applyOptimizations',
                        title: 'Apply Sustainable Refactoring'
                    };
                    applyAction.diagnostics = carboniqDiagnostics;
                    actions.push(applyAction);

                    // Action 3: Explain Issue in Detail
                    for (const diag of carboniqDiagnostics) {
                        const cleanMsg = diag.message.replace('[CarbonIQ] ', '');
                        const issueTitle = cleanMsg.split('Fix:')[0].trim();
                        const explainAction = new vscode.CodeAction(
                            `💡 CarbonIQ: Explain '${issueTitle}'`,
                            vscode.CodeActionKind.QuickFix
                        );
                        explainAction.command = {
                            command: 'carboniq.optimizeFile',
                            title: 'Explain Issue & Preview'
                        };
                        explainAction.diagnostics = [diag];
                        actions.push(explainAction);
                    }

                    return actions;
                }
            },
            {
                providedCodeActionKinds: [vscode.CodeActionKind.QuickFix]
            }
        )
    );

    // Register Hover Provider for Green Squigglies
    context.subscriptions.push(
        vscode.languages.registerHoverProvider({ language: 'python' }, {
            provideHover(doc, position) {
                const diagnostics = diagnosticCollection.get(doc.uri);
                if (!diagnostics || diagnostics.length === 0) return null;

                const hit = diagnostics.find(d => d.range.contains(position));
                if (!hit) return null;

                const md = new vscode.MarkdownString();
                md.isTrusted = true;
                md.appendMarkdown(`### 🌱 **CarbonIQ Green Suggestion**\n\n`);
                md.appendMarkdown(`${hit.message}\n\n`);
                md.appendMarkdown(`---\n`);
                md.appendMarkdown(`[⚡ Preview Greener Alternative (Diff)](command:carboniq.optimizeFile) | [✅ Apply Refactoring](command:carboniq.applyOptimizations)\n`);
                return new vscode.Hover(md);
            }
        })
    );

    // Auto-audit when switching active editor
    context.subscriptions.push(
        vscode.window.onDidChangeActiveTextEditor((editor) => {
            if (editor && editor.document.languageId === 'python') {
                auditDocument(editor.document, false);
            }
        })
    );

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

    // Initial audit for currently open editor
    if (vscode.window.activeTextEditor && vscode.window.activeTextEditor.document.languageId === 'python') {
        auditDocument(vscode.window.activeTextEditor.document, false);
    }
}

/**
 * Runs AST carbon audit on a document and decorates lines with squigglies
 * @param {vscode.TextDocument} doc
 * @param {boolean} showToast
 */
async function auditDocument(doc, showToast = false) {
    const wsRoot = getWorkspaceRoot(doc);
    const pythonPath = getResolvedPythonPath(wsRoot);
    const filePath = doc.fileName;
    const fileContent = doc.getText();

    const pythonScript = `
import json, sys, os
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ws = r"${wsRoot.replace(/\\/g, '\\\\')}"
if ws and ws not in sys.path:
    sys.path.insert(0, ws)
try:
    import carboniq
    code = sys.stdin.read()
    res = carboniq.audit_code(code)
    print(json.dumps(res, ensure_ascii=True))
except Exception as e:
    print(json.dumps({'error': str(e)}, ensure_ascii=True))
`;

    const { spawn } = require('child_process');
    const child = spawn(pythonPath, ['-c', pythonScript], {
        cwd: wsRoot,
        env: {
            ...process.env,
            PYTHONIOENCODING: "utf-8",
            PYTHONPATH: wsRoot ? `${wsRoot}${path.delimiter}${process.env.PYTHONPATH || ''}` : process.env.PYTHONPATH
        }
    });

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
    const wsRoot = getWorkspaceRoot(doc);
    const pythonPath = getResolvedPythonPath(wsRoot);
    const filePath = doc.fileName;
    const fileContent = doc.getText();

    const pythonScript = `
import json, sys, os
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ws = r"${wsRoot.replace(/\\/g, '\\\\')}"
if ws and ws not in sys.path:
    sys.path.insert(0, ws)
try:
    import carboniq
    code = sys.stdin.read()
    res = carboniq.optimize_code(code)
    print(json.dumps(res, ensure_ascii=True))
except Exception as e:
    print(json.dumps({'error': str(e)}, ensure_ascii=True))
`;

    const { spawn } = require('child_process');
    const child = spawn(pythonPath, ['-c', pythonScript], {
        cwd: wsRoot,
        env: {
            ...process.env,
            PYTHONIOENCODING: "utf-8",
            PYTHONPATH: wsRoot ? `${wsRoot}${path.delimiter}${process.env.PYTHONPATH || ''}` : process.env.PYTHONPATH
        }
    });

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

/**
 * Directly applies sustainable AST optimizations to a document
 * @param {vscode.TextDocument} doc
 */
async function applyOptimizationsDirectly(doc) {
    const wsRoot = getWorkspaceRoot(doc);
    const pythonPath = getResolvedPythonPath(wsRoot);
    const fileContent = doc.getText();

    const pythonScript = `
import json, sys, os
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ws = r"${wsRoot.replace(/\\/g, '\\\\')}"
if ws and ws not in sys.path:
    sys.path.insert(0, ws)
try:
    import carboniq
    code = sys.stdin.read()
    res = carboniq.optimize_code(code)
    print(json.dumps(res, ensure_ascii=True))
except Exception as e:
    print(json.dumps({'error': str(e)}, ensure_ascii=True))
`;

    const child = spawn(pythonPath, ['-c', pythonScript], {
        cwd: wsRoot,
        env: {
            ...process.env,
            PYTHONIOENCODING: "utf-8",
            PYTHONPATH: wsRoot ? `${wsRoot}${path.delimiter}${process.env.PYTHONPATH || ''}` : process.env.PYTHONPATH
        }
    });

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

            const edit = new vscode.WorkspaceEdit();
            const fullRange = new vscode.Range(
                doc.positionAt(0),
                doc.positionAt(doc.getText().length)
            );
            edit.replace(doc.uri, fullRange, optimizedCode);
            await vscode.workspace.applyEdit(edit);
            vscode.window.showInformationMessage(`✅ CarbonIQ: Sustainable green optimizations applied! (~${savings}% est. energy reduction)`);
            await auditDocument(doc, false);
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
