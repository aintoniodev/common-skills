#!/usr/bin/env python3
"""Reusable Mermaid HTML helpers for the pr-walkthrough skill.

The generated walkthrough is usually opened via file://. This helper emits a
safe runtime pattern for Mermaid diagrams:

- Define the renderer before loading the external Mermaid script.
- Inject a pinned official Mermaid CDN URL dynamically after DOMContentLoaded.
- Keep readable source fallback visible until rendering succeeds.
- Add a reusable lightbox so wide diagrams can be inspected at a readable size.
- Never use unpinned latest URLs.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from textwrap import dedent

MERMAID_VERSION = "10.9.3"
MERMAID_CDN_URL = f"https://cdn.jsdelivr.net/npm/mermaid@{MERMAID_VERSION}/dist/mermaid.min.js"


def _stable_id(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip()).strip("-").lower()
    return slug or "diagram"


def mermaid_figure(source: str, caption: str, figure_id: str | None = None) -> str:
    """Return a semantic figure containing Mermaid source plus fallback source."""
    escaped_source = html.escape(source.strip())
    escaped_caption = html.escape(caption)
    figure_id = _stable_id(figure_id or caption)
    return dedent(
        f"""
        <figure class="visual-artifact mermaid-artifact" data-source="generated" id="{figure_id}">
          <figcaption>
            {escaped_caption}
          </figcaption>
          <div class="mermaid-actions">
            <button class="mermaid-open-lightbox" type="button">Open diagram</button>
          </div>
          <div class="mermaid-block">
            <div class="mermaid" data-mermaid-source="{figure_id}">{escaped_source}</div>
            <pre class="mermaid-fallback" aria-label="Mermaid source fallback">{escaped_source}</pre>
          </div>
        </figure>
        """
    ).strip()


def mermaid_css() -> str:
    """Return CSS for Mermaid diagrams, fallback handling, and lightbox viewing."""
    return dedent(
        """
        .mermaid-artifact { padding: 18px; }
        .mermaid-block { background: #f8fafc; color: #0f172a; border-radius: 14px; padding: 18px; overflow: auto; }
        .mermaid { min-height: 180px; }
        .mermaid svg { max-width: none; height: auto; }
        .mermaid-fallback { white-space: pre-wrap; color: #dbeafe; background: #0a0f16; border-radius: 10px; }
        .mermaid-artifact.mermaid-rendered .mermaid-fallback { display: none; }
        .mermaid-artifact.mermaid-failed .mermaid-fallback { display: block; }
        .mermaid-actions { display: flex; justify-content: flex-end; margin: 10px 0; }
        .mermaid-open-lightbox, .mermaid-lightbox-close { border: 1px solid var(--border, #303946); background: var(--panel2, #1f2630); color: var(--text, #e6edf3); border-radius: 10px; padding: 8px 12px; cursor: pointer; font: inherit; }
        .mermaid-open-lightbox:hover, .mermaid-lightbox-close:hover { filter: brightness(1.15); }
        .mermaid-lightbox { position: fixed; inset: 0; z-index: 9999; display: none; background: rgba(0, 0, 0, 0.78); padding: 28px; }
        .mermaid-lightbox.open { display: grid; grid-template-rows: auto minmax(0, 1fr); gap: 12px; }
        .mermaid-lightbox-header { display: flex; align-items: center; justify-content: space-between; gap: 16px; color: var(--text, #e6edf3); }
        .mermaid-lightbox-title { font-weight: 700; }
        .mermaid-lightbox-viewport { overflow: auto; background: #f8fafc; border-radius: 16px; padding: 24px; color: #0f172a; }
        .mermaid-lightbox-diagram { min-width: 1100px; width: max-content; }
        .mermaid-lightbox-diagram svg { max-width: none !important; height: auto !important; min-width: 1100px; }
        .mermaid-lightbox-source { min-width: 900px; color: #dbeafe; background: #0a0f16; border-radius: 10px; white-space: pre-wrap; }
        """
    ).strip()


def mermaid_runtime_script() -> str:
    """Return an inline script that loads, renders, and lightboxes Mermaid diagrams."""
    return dedent(
        f"""
        <script>
        (() => {{
          const MERMAID_CDN_URL = {MERMAID_CDN_URL!r};
          let attemptedLoad = false;
          let renderPromise = null;
          let activeLightbox = null;

          function ensureLightbox() {{
            if (activeLightbox) {{
              return activeLightbox;
            }}
            const root = document.createElement('div');
            root.className = 'mermaid-lightbox';
            root.setAttribute('role', 'dialog');
            root.setAttribute('aria-modal', 'true');
            root.setAttribute('aria-label', 'Expanded Mermaid diagram');
            root.innerHTML = `
              <div class="mermaid-lightbox-header">
                <div class="mermaid-lightbox-title">Mermaid diagram</div>
                <button class="mermaid-lightbox-close" type="button">Close diagram</button>
              </div>
              <div class="mermaid-lightbox-viewport" tabindex="0">
                <div class="mermaid-lightbox-diagram"></div>
              </div>
            `;
            const close = () => root.classList.remove('open');
            root.querySelector('.mermaid-lightbox-close').addEventListener('click', close);
            root.addEventListener('click', (event) => {{
              if (event.target === root) {{
                close();
              }}
            }});
            document.addEventListener('keydown', (event) => {{
              if (event.key === 'Escape' && root.classList.contains('open')) {{
                close();
              }}
            }});
            document.body.appendChild(root);
            activeLightbox = root;
            return root;
          }}

          function openMermaidLightbox(figure) {{
            const root = ensureLightbox();
            const title = figure.querySelector('figcaption')?.childNodes?.[0]?.textContent?.trim() || 'Mermaid diagram';
            const titleNode = root.querySelector('.mermaid-lightbox-title');
            const diagramNode = root.querySelector('.mermaid-lightbox-diagram');
            titleNode.textContent = title;
            diagramNode.innerHTML = '';

            const renderedSvg = figure.querySelector('.mermaid svg');
            if (renderedSvg) {{
              const clone = renderedSvg.cloneNode(true);
              clone.removeAttribute('width');
              clone.removeAttribute('height');
              diagramNode.appendChild(clone);
            }} else {{
              const fallback = figure.querySelector('.mermaid-fallback');
              const pre = document.createElement('pre');
              pre.className = 'mermaid-lightbox-source';
              pre.textContent = fallback ? fallback.textContent : 'Mermaid diagram has not rendered yet.';
              diagramNode.appendChild(pre);
            }}

            root.classList.add('open');
            root.querySelector('.mermaid-lightbox-viewport').focus();
          }}

          function setupMermaidLightboxes() {{
            document.querySelectorAll('.mermaid-artifact').forEach((figure) => {{
              if (!figure.querySelector('.mermaid-open-lightbox')) {{
                const actions = document.createElement('div');
                actions.className = 'mermaid-actions';
                const button = document.createElement('button');
                button.className = 'mermaid-open-lightbox';
                button.type = 'button';
                button.textContent = 'Open diagram';
                actions.appendChild(button);
                const block = figure.querySelector('.mermaid-block');
                figure.insertBefore(actions, block || null);
              }}
              figure.querySelectorAll('.mermaid-open-lightbox').forEach((button) => {{
                if (button.dataset.lightboxBound === 'true') {{
                  return;
                }}
                button.dataset.lightboxBound = 'true';
                button.addEventListener('click', () => openMermaidLightbox(figure));
              }});
            }});
          }}

          function markFailed(error) {{
            console.warn('Mermaid render unavailable; source fallback remains visible.', error || 'unknown error');
            document.querySelectorAll('.mermaid-artifact').forEach((figure) => {{
              figure.classList.add('mermaid-failed');
              figure.classList.remove('mermaid-rendered');
              figure.dataset.mermaidError = formatMermaidError(error || 'unknown error');
            }});
            document.body.classList.add('mermaid-has-errors');
            setupMermaidLightboxes();
          }}

          function renderedNodeHasError(node) {{
            const text = node.textContent || '';
            return /Syntax error|Parse error|Lexical error|mermaid version/i.test(text);
          }}

          function formatMermaidError(error) {{
            if (!error) {{
              return 'unknown error';
            }}
            if (typeof error === 'string') {{
              return error;
            }}
            if (error.str) {{
              return error.str;
            }}
            if (error.message) {{
              return error.message;
            }}
            try {{
              return JSON.stringify(error);
            }} catch (_) {{
              return String(error);
            }}
          }}

          function markNodeFailed(node, error) {{
            const figure = node.closest('.mermaid-artifact');
            if (!figure) {{
              return;
            }}
            figure.classList.add('mermaid-failed');
            figure.classList.remove('mermaid-rendered');
            figure.dataset.mermaidError = formatMermaidError(error || 'Mermaid did not produce a valid SVG');
          }}

          function mermaidSourceForNode(node) {{
            const figure = node.closest('.mermaid-artifact');
            const fallback = figure?.querySelector('.mermaid-fallback');
            return (fallback?.textContent || node.textContent || '').trim();
          }}

          async function renderOneMermaidNode(node, index) {{
            const source = mermaidSourceForNode(node);
            if (!source) {{
              throw new Error('Mermaid source is empty');
            }}
            const renderId = `pr_walkthrough_mermaid_${{index}}_${{Date.now()}}`;
            const rendered = await window.mermaid.render(renderId, source);
            if (!rendered?.svg || /Syntax error|Parse error|Lexical error|mermaid version/i.test(rendered.svg)) {{
              throw new Error('Mermaid did not produce a valid SVG');
            }}
            node.innerHTML = rendered.svg;
            if (typeof rendered.bindFunctions === 'function') {{
              rendered.bindFunctions(node);
            }}
          }}

          async function renderMermaidDiagrams() {{
            setupMermaidLightboxes();
            if (!window.mermaid) {{
              markFailed('Mermaid library was not loaded');
              return;
            }}
            if (renderPromise) {{
              return renderPromise;
            }}
            renderPromise = (async () => {{
              try {{
                window.mermaid.initialize({{ startOnLoad: false, theme: 'base', securityLevel: 'strict' }});
                const nodes = Array.from(document.querySelectorAll('.mermaid'));
                if (nodes.length === 0) {{
                  return;
                }}
                let failedCount = 0;
                for (const [index, node] of nodes.entries()) {{
                  const figure = node.closest('.mermaid-artifact');
                  if (!figure) {{
                    continue;
                  }}
                  try {{
                    await renderOneMermaidNode(node, index + 1);
                  }} catch (error) {{
                    failedCount += 1;
                    markNodeFailed(node, error);
                    continue;
                  }}
                  if (node.querySelector('svg') && !renderedNodeHasError(node)) {{
                    figure.classList.add('mermaid-rendered');
                    figure.classList.remove('mermaid-failed');
                    delete figure.dataset.mermaidError;
                  }} else {{
                    failedCount += 1;
                    markNodeFailed(node, 'Mermaid did not produce a valid SVG');
                  }}
                }}
                setupMermaidLightboxes();
                if (failedCount > 0) {{
                  document.body.classList.add('mermaid-has-errors');
                  console.warn(`${{failedCount}} Mermaid diagram(s) failed to render; source fallback remains visible.`);
                }} else {{
                  document.body.classList.add('mermaid-ready');
                  document.body.classList.remove('mermaid-has-errors');
                }}
              }} catch (error) {{
                markFailed(error);
              }}
            }})();
            return renderPromise;
          }}

          function loadMermaidRuntime() {{
            setupMermaidLightboxes();
            if (attemptedLoad) {{
              return;
            }}
            attemptedLoad = true;
            if (window.mermaid) {{
              void renderMermaidDiagrams();
              return;
            }}
            const script = document.createElement('script');
            script.src = MERMAID_CDN_URL;
            script.async = true;
            script.onload = () => void renderMermaidDiagrams();
            script.onerror = () => markFailed(`Failed to load pinned Mermaid CDN script: ${{MERMAID_CDN_URL}}`);
            document.head.appendChild(script);
          }}

          window.prWalkthroughRenderMermaid = renderMermaidDiagrams;
          window.prWalkthroughOpenMermaidLightbox = openMermaidLightbox;
          if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', loadMermaidRuntime, {{ once: true }});
          }} else {{
            loadMermaidRuntime();
          }}
        }})();
        </script>
        """
    ).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit reusable Mermaid walkthrough HTML snippets.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--css", action="store_true", help="Print CSS for Mermaid containers, fallbacks, and lightbox viewing.")
    group.add_argument("--runtime", action="store_true", help="Print the pinned-CDN Mermaid runtime/lightbox loader script.")
    group.add_argument("--figure", action="store_true", help="Read Mermaid source from stdin and print a semantic figure with an Open diagram control.")
    parser.add_argument("--caption", default="Generated Mermaid diagram", help="Figure caption for --figure.")
    parser.add_argument("--id", default=None, help="Optional stable figure id for --figure.")
    args = parser.parse_args()

    if args.css:
        print(mermaid_css())
    elif args.runtime:
        print(mermaid_runtime_script())
    elif args.figure:
        print(mermaid_figure(sys.stdin.read(), args.caption, args.id))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
