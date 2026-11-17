#!/usr/bin/env python3
"""Wrapper for llama-benchy that reads OPENAI_API_KEY/LLM_KEY_BOX from env
(never via CLI argv) and passes it to llama_benchy. Also writes a sibling .md
table whenever --format json and --save-result <path.json> are used."""
import os
import sys

def main():
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_KEY_BOX") or "EMPTY"
    # Inject --api-key inside Python so /proc/<pid>/cmdline never contains the key.
    # Also intercept BenchmarkResults.save_report to emit both JSON and Markdown.
    from llama_benchy.results import BenchmarkResults
    orig_save = BenchmarkResults.save_report

    def save_both(self, filename, fmt, concurrency=1):
        orig_save(self, filename, fmt, concurrency)
        if filename and fmt == "json":
            md_path = filename[:-5] + ".md" if filename.endswith(".json") else filename + ".md"
            md_text = self._generate_md_report(concurrency)
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_text + "\n")
            print(f"Also wrote Markdown summary to {md_path}")

    BenchmarkResults.save_report = save_both

    # Build sanitized argv for llama_benchy
    sys.argv = [sys.argv[0], "--api-key", api_key] + sys.argv[1:]
    from llama_benchy.__main__ import main as benchy_main
    benchy_main()

if __name__ == "__main__":
    main()
