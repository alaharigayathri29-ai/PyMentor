/**
 * Markdown rendering and code block decoration utility.
 */

export function renderMarkdown(rawText) {
  if (!rawText) return '';

  if (window.marked) {
    try {
      window.marked.setOptions({ breaks: true, gfm: true });
      const html = window.marked.parse(rawText);
      return enhanceCodeBlocks(html);
    } catch {
      // fallback to basic parser below
    }
  }

  // Fallback lightweight regex formatting
  const formatted = rawText
    .replace(/```python\n?([\s\S]*?)```/g, '<pre><code class="language-python">$1</code></pre>')
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.06);padding:2px 6px;border-radius:4px;color:#c084fc;">$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');

  return enhanceCodeBlocks(formatted);
}

function enhanceCodeBlocks(html) {
  // Wrap <pre> blocks with copy button
  return html.replace(/<pre><code(?:\s+class="([^"]*)")?>([\s\S]*?)<\/code><\/pre>/gi, (match, cls, codeContent) => {
    return `
      <div style="position:relative;margin:12px 0;">
        <pre style="margin:0;padding:14px 16px;background:#090d18;border:1px solid rgba(255,255,255,0.08);border-radius:8px;overflow-x:auto;"><code class="${cls || ''}">${codeContent}</code></pre>
        <button class="code-copy-btn" onclick="window.copyCodeSnippet(this)">Copy</button>
      </div>
    `;
  });
}

// Global copy handler
if (typeof window !== 'undefined') {
  window.copyCodeSnippet = function(buttonEl) {
    const pre = buttonEl.previousElementSibling;
    if (!pre) return;
    const textToCopy = pre.innerText || pre.textContent;
    navigator.clipboard.writeText(textToCopy.trim()).then(() => {
      const orig = buttonEl.textContent;
      buttonEl.textContent = 'Copied! ✓';
      buttonEl.style.color = '#4ade80';
      setTimeout(() => {
        buttonEl.textContent = orig;
        buttonEl.style.color = '';
      }, 2000);
    });
  };
}

