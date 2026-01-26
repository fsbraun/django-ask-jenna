import sys
import requests

DJANGO_MCP_URL = "http://localhost:8000/mcp/"


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            response = requests.post(
                DJANGO_MCP_URL,
                data=line,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json,text/event-stream",
                },
                timeout=30,
            )
        except Exception as e:
            # Return JSON-RPC error envelope manually
            sys.stdout.write(
                f'{{"jsonrpc":"2.0","error":{{"code":-32000,"message":"{e}"}}}}\n'
            )
            sys.stdout.flush()
            continue

        if response.content:
            sys.stdout.write(response.text + "\n")
            sys.stdout.flush()
        # notifications → no output


if __name__ == "__main__":
    main()
