/**
 * CodeMirror Editor Component helper.
 */

export function createCodeEditor(containerEl, initialValue = '', readOnly = false, mode = 'python') {
  if (!containerEl) return null;
  containerEl.innerHTML = '';

  if (!window.CodeMirror) {
    const ta = document.createElement('textarea');
    ta.value = initialValue;
    ta.style.width = '100%';
    ta.style.height = '100%';
    ta.style.background = '#FFFFFF';
    ta.style.color = '#1E293B';
    ta.style.border = 'none';
    ta.style.outline = 'none';
    ta.style.padding = '14px';
    ta.style.fontFamily = 'JetBrains Mono, monospace';
    ta.style.fontSize = '13.5px';
    containerEl.appendChild(ta);
    return {
      getValue: () => ta.value,
      setValue: (val) => { ta.value = val; },
      setOption: () => {},
      focus: () => ta.focus(),
      refresh: () => {},
    };
  }

  const editor = window.CodeMirror(containerEl, {
    value: initialValue,
    mode: mode,
    theme: 'default',
    lineNumbers: true,
    matchBrackets: true,
    autoCloseBrackets: true,
    tabSize: 4,
    indentUnit: 4,
    readOnly: readOnly,
    extraKeys: {
      'Tab': (cm) => cm.replaceSelection('    ', 'end'),
    },
  });

  setTimeout(() => editor.refresh(), 100);
  return editor;
}
