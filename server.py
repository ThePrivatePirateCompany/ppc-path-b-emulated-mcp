#!/usr/bin/env python3
"""PPC Path B — emulated reference MCP (Streamable HTTP)."""
from __future__ import annotations
import json, os, secrets, threading, time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse
PROTOCOL='2025-03-26'
SERVER_NAME='ppc-path-b-emulated-mcp'
SERVER_VERSION='0.1.0'
PROJECT='PPC-GROK-BOT-P1-REQ-001'
_lock=threading.Lock(); _items={}; _seq=0
def _now():
    return datetime.now(timezone.utc).isoformat()
def _ok_text(payload):
    return {'content':[{'type':'text','text':json.dumps(payload,indent=2)}],'structuredContent':payload,'isError':False}
def _err_text(message):
    return {'content':[{'type':'text','text':message}],'isError':True}
def create_item(args):
    global _seq
    title=(args.get('title') or '').strip()
    if not title: return _err_text('create requires title')
    with _lock:
        _seq += 1
        item_id=f'PPC-{_seq:04d}'
        item={'id':item_id,'title':title,'body':args.get('body') or '','assignee':None,'status':'created','approved':False,'approver':None,'created_at':_now(),'updated_at':_now(),'project':PROJECT,'emulated':True}
        _items[item_id]=item
        return _ok_text({'ok':True,'item':item})
def assign_item(args):
    item_id=(args.get('id') or '').strip(); assignee=(args.get('assignee') or '').strip()
    if not item_id or not assignee: return _err_text('assign requires id and assignee')
    with _lock:
        item=_items.get(item_id)
        if not item: return _err_text(f'unknown id: {item_id}')
        if item['status']=='approved': return _err_text(f'{item_id} already approved; reassignment blocked')
        item['assignee']=assignee; item['status']='assigned'; item['updated_at']=_now()
        return _ok_text({'ok':True,'item':item})
def status_item(args):
    item_id=(args.get('id') or '').strip()
    with _lock:
        if item_id:
            item=_items.get(item_id)
            if not item: return _err_text(f'unknown id: {item_id}')
            return _ok_text({'ok':True,'item':item})
        listing=sorted(_items.values(), key=lambda x: x['id'])
        return _ok_text({'ok':True,'count':len(listing),'items':listing,'server':SERVER_NAME,'version':SERVER_VERSION,'project':PROJECT})
def approve_item(args):
    item_id=(args.get('id') or '').strip(); approver=(args.get('approver') or 'grok-connector').strip(); note=args.get('note') or ''
    if not item_id: return _err_text('approve requires id')
    with _lock:
        item=_items.get(item_id)
        if not item: return _err_text(f'unknown id: {item_id}')
        if item['status']=='created': return _err_text(f'{item_id} is created but unassigned; assign before approve')
        item['approved']=True; item['approver']=approver; item['status']='approved'; item['approval_note']=note; item['updated_at']=_now()
        return _ok_text({'ok':True,'item':item})
TOOLS=[{'name':'create','description':'Create a PPC work item on the Path B emulated reference MCP.','inputSchema':{'type':'object','properties':{'title':{'type':'string'},'body':{'type':'string'}},'required':['title']}},{'name':'assign','description':'Assign an existing PPC work item.','inputSchema':{'type':'object','properties':{'id':{'type':'string'},'assignee':{'type':'string'}},'required':['id','assignee']}},{'name':'status','description':'Read one work item or list all.','inputSchema':{'type':'object','properties':{'id':{'type':'string'}}}},{'name':'approve','description':'Approve an assigned PPC work item.','inputSchema':{'type':'object','properties':{'id':{'type':'string'},'approver':{'type':'string'},'note':{'type':'string'}},'required':['id']}}]
HANDLERS={'create':create_item,'assign':assign_item,'status':status_item,'approve':approve_item}
def rpc_result(req_id, result): return {'jsonrpc':'2.0','id':req_id,'result':result}
def rpc_error(req_id, code, message): return {'jsonrpc':'2.0','id':req_id,'error':{'code':code,'message':message}}
def handle_rpc(msg):
    method=msg.get('method'); req_id=msg.get('id'); params=msg.get('params') or {}
    if method and str(method).startswith('notifications/'): return None
    if method=='initialize':
        client_proto=params.get('protocolVersion') or PROTOCOL
        return rpc_result(req_id, {'protocolVersion':client_proto or PROTOCOL,'capabilities':{'tools':{'listChanged':False},'logging':{}},'serverInfo':{'name':SERVER_NAME,'version':SERVER_VERSION},'instructions':'PPC Path B emulated reference MCP. Tools: create, assign, status, approve.'})
    if method=='ping': return rpc_result(req_id, {})
    if method=='tools/list': return rpc_result(req_id, {'tools':TOOLS})
    if method=='tools/call':
        name=params.get('name'); args=params.get('arguments') or {}; fn=HANDLERS.get(name)
        if not fn: return rpc_result(req_id, _err_text(f'unknown tool: {name}'))
        try: return rpc_result(req_id, fn(args if isinstance(args, dict) else {}))
        except Exception as exc: return rpc_result(req_id, _err_text(str(exc)))
    if method=='resources/list': return rpc_result(req_id, {'resources':[]})
    if method=='prompts/list': return rpc_result(req_id, {'prompts':[]})
    return rpc_error(req_id, -32601, f'Method not found: {method}')
AUTH_TOKEN=os.environ.get('PPC_MCP_TOKEN','').strip()
class Handler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    def log_message(self, fmt, *args):
        print(f'{self.log_date_time_string()} {fmt % args}', file=__import__('sys').stderr)
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS, DELETE')
        self.send_header('Access-Control-Allow-Headers','Content-Type, Accept, Authorization, MCP-Session-Id, Mcp-Session-Id')
        self.send_header('Access-Control-Expose-Headers','Mcp-Session-Id, MCP-Session-Id')
    def _auth_ok(self):
        if not AUTH_TOKEN: return True
        return self.headers.get('Authorization','')==f'Bearer {AUTH_TOKEN}'
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_GET(self):
        path=urlparse(self.path).path
        if path in ('/','/health','/healthz'):
            body=json.dumps({'ok':True,'server':SERVER_NAME,'version':SERVER_VERSION,'project':PROJECT,'transport':'streamable-http','path':'/mcp','tools':[t['name'] for t in TOOLS]}).encode()
            self.send_response(200); self._cors(); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body); return
        accept=self.headers.get('Accept','')
        if path in ('/mcp','/mcp/') and 'text/event-stream' in accept:
            self.send_response(200); self._cors(); self.send_header('Content-Type','text/event-stream'); self.send_header('Cache-Control','no-cache'); self.send_header('Connection','keep-alive'); self.end_headers()
            try:
                self.wfile.write(b': ppc-path-b ready\n\n'); self.wfile.flush()
                while True:
                    time.sleep(25); self.wfile.write(b': keepalive\n\n'); self.wfile.flush()
            except BrokenPipeError:
                return
            return
        self.send_response(404); self._cors(); self.end_headers()
    def do_DELETE(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_POST(self):
        if not self._auth_ok():
            body=json.dumps({'jsonrpc':'2.0','id':None,'error':{'code':-32004,'message':'Unauthorized'}}).encode()
            self.send_response(401); self._cors(); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body); return
        length=int(self.headers.get('Content-Length') or 0)
        raw=self.rfile.read(length) if length else b'{}'
        try: payload=json.loads(raw.decode() or '{}')
        except json.JSONDecodeError:
            body=json.dumps({'jsonrpc':'2.0','id':None,'error':{'code':-32700,'message':'Parse error'}}).encode()
            self.send_response(400); self._cors(); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body); return
        accept=self.headers.get('Accept','')
        use_sse='text/event-stream' in accept and 'application/json' not in accept
        messages=payload if isinstance(payload, list) else [payload]
        responses=[]
        for msg in messages:
            if isinstance(msg, dict):
                out=handle_rpc(msg)
                if out is not None: responses.append(out)
        session=self.headers.get('Mcp-Session-Id') or self.headers.get('MCP-Session-Id') or secrets.token_hex(8)
        if use_sse:
            self.send_response(200); self._cors(); self.send_header('Content-Type','text/event-stream'); self.send_header('Cache-Control','no-cache'); self.send_header('Mcp-Session-Id',session); self.end_headers()
            for resp in responses:
                self.wfile.write(f'event: message\ndata: {json.dumps(resp)}\n\n'.encode())
            self.wfile.flush(); return
        if not responses:
            self.send_response(202); self._cors(); self.send_header('Mcp-Session-Id',session); self.end_headers(); return
        body_obj=responses[0] if len(responses)==1 else responses
        body=json.dumps(body_obj).encode()
        self.send_response(200); self._cors(); self.send_header('Content-Type','application/json'); self.send_header('Mcp-Session-Id',session); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
def main():
    host=os.environ.get('HOST','0.0.0.0'); port=int(os.environ.get('PORT','8787'))
    httpd=ThreadingHTTPServer((host, port), Handler)
    print(f'{SERVER_NAME} {SERVER_VERSION} listening on http://{host}:{port}/mcp', flush=True)
    httpd.serve_forever()
if __name__=='__main__':
    main()
