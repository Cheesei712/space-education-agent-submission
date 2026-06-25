import os
import subprocess
import json
import time

def main():
    mcp_script = os.path.abspath("nasa_mcp_server.py")
    python_exe = os.path.abspath(".venv/Scripts/python.exe")
    
    print(f"Spawning MCP server subprocess: {python_exe} -u {mcp_script}")
    proc = subprocess.Popen(
        [python_exe, "-u", mcp_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Check if process is running
    time.sleep(1)
    if proc.poll() is not None:
        print("MCP server failed to start. Stderr:")
        print(proc.stderr.read())
        return

    print("MCP Server started successfully.")
    
    # 1. Send initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    
    print("Sending initialize request...")
    proc.stdin.write(json.dumps(init_request) + "\n")
    proc.stdin.flush()
    
    # Read response
    print("Waiting for initialize response...")
    line = proc.stdout.readline()
    print("Initialize Response:")
    print(line)
    
    # Send initialized notification
    initialized_notification = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    print("Sending initialized notification...")
    proc.stdin.write(json.dumps(initialized_notification) + "\n")
    proc.stdin.flush()
    
    # 2. Call tool: get_planetary_details
    call_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "get_planetary_details",
            "arguments": {"planet_name": "Mars"}
        }
    }
    
    print("Sending tools/call request for Mars...")
    proc.stdin.write(json.dumps(call_request) + "\n")
    proc.stdin.flush()
    
    # Read response
    print("Waiting for tools/call response...")
    line = proc.stdout.readline()
    print("Tools/Call Response:")
    print(line)
    
    # Clean up
    proc.terminate()
    proc.wait()
    print("Done.")

if __name__ == "__main__":
    main()
