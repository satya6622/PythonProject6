#!/usr/bin/env python3
"""Resume matching agent whose filesystem access is exclusively via MCP."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


class McpClient:
    """Minimal synchronous stdio JSON-RPC MCP client for one server process."""
    def __init__(self, root: str, server_path: Path | None = None, trace: bool = False) -> None:
        server_path = server_path or Path(__file__).with_name("filesystem_mcp_server.py")
        self.process = subprocess.Popen([sys.executable, str(server_path), "--root", root], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
        self.request_id = 0
        self.trace = trace
        self.request("initialize", {"protocolVersion": "2024-11-05", "clientInfo": {"name": "resume-matcher", "version": "1.0.0"}, "capabilities": {}})
        self.notify("notifications/initialized")

    def request(self, method: str, params: dict[str, Any] | None = None) -> Any:
        self.request_id += 1
        assert self.process.stdin and self.process.stdout
        request = {"jsonrpc": "2.0", "id": self.request_id, "method": method, "params": params or {}}
        if self.trace: print(f"MCP -> {json.dumps(request)}", file=sys.stderr)
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        response = json.loads(self.process.stdout.readline())
        if self.trace: print(f"MCP <- {json.dumps(response)}", file=sys.stderr)
        if "error" in response:
            raise RuntimeError(f"MCP {response['error']['code']}: {response['error']['message']}")
        return response["result"]

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        assert self.process.stdin
        self.process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": method, "params": params or {}}) + "\n")
        self.process.stdin.flush()

    def tool(self, name: str, **arguments: Any) -> Any:
        return self.request("tools/call", {"name": name, "arguments": arguments})["structuredContent"]

    def close(self) -> None:
        if self.process.stdin and not self.process.stdin.closed:
            self.process.stdin.close()
        if self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=2)
        if self.process.stdout and not self.process.stdout.closed:
            self.process.stdout.close()

    def __enter__(self) -> "McpClient": return self
    def __exit__(self, *_: object) -> None: self.close()


def keywords(text: str) -> set[str]:
    stop_words = {"and", "the", "for", "with", "from", "that", "this", "are", "you", "your", "years", "experience", "have", "will", "our", "all"}
    return {word.lower() for word in re.findall(r"[A-Za-z][A-Za-z+#.-]{1,}", text) if word.lower() not in stop_words}


class ResumeMatchingAgent:
    """Workflow: discover via MCP -> batch read via MCP -> score locally -> rank."""
    def __init__(self, client: McpClient) -> None: self.client = client

    def match(self, job_description: str, directory: str = ".") -> list[dict[str, Any]]:
        files = self.client.tool("list_directory", path=directory)
        resumes = [item["path"] for item in files if item["type"] == "file" and item["path"].lower().endswith((".txt", ".md"))]
        batch = self.client.tool("batch_process", paths=resumes)
        required = keywords(job_description)
        ranked = []
        for resume in batch["processed"]:
            found = keywords(resume["content"])
            matched = sorted(required & found)
            ranked.append({"resume": resume["path"], "score": round(100 * len(matched) / max(1, len(required)), 1), "matched_keywords": matched})
        return sorted(ranked, key=lambda candidate: candidate["score"], reverse=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Match text resumes using MCP filesystem resources")
    parser.add_argument("job_description")
    parser.add_argument("--root", default=".")
    parser.add_argument("--directory", default=".")
    parser.add_argument("--trace", action="store_true", help="Print MCP JSON-RPC requests and responses to stderr")
    args = parser.parse_args()
    with McpClient(args.root, trace=args.trace) as client:
        print(json.dumps(ResumeMatchingAgent(client).match(args.job_description, args.directory), indent=2))


if __name__ == "__main__":
    main()
