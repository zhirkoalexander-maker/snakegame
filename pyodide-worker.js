importScripts('https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js');

let pyodide = null;

async function loadPyodideAndPackages() {
    pyodide = await loadPyodide();
    await pyodide.loadPackage('pygame');
    return pyodide;
}

self.onmessage = async (event) => {
    if (event.data.type === 'loadPygame') {
        try {
            await loadPyodideAndPackages();
            
            const response = await fetch('main.py');
            const code = await response.text();
            
            await pyodide.runPythonAsync(code);
            
            self.postMessage({ type: 'ready' });
        } catch (error) {
            self.postMessage({ type: 'error', message: error.message });
        }
    }
};
