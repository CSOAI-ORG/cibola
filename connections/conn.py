#!/usr/bin/env python3
"""conn.py — the living connections database (CSOAI LTD).

Single source of truth for EVERY outward contact, message, account and move:
   contacts   — who (org, role, email, channel, source, status, notes)
   messages   — every email/send (contact_id, direction, subject, status, ts, archive)
   accounts   — every external account (service, account_id, email, status, token_ref)
   moves      — external actions tracked to their move id + owner gate state

CLI:
   conn.py init                 create DB (idempotent)
   conn.py seed                 seed known contacts from this file + mail audit
   conn.py add <email> [--org O] [--role R] [--channel C] [--source S] [--status ST]
   conn.py log <email> --subject S --direction out --status sent --note N
   conn.py search <term>        search contacts+messages
   conn.py list [--status ST]   list contacts
   conn.py account add <service> <email> --status ST
   conn.py stats                counts

DB: connections/connections.db (repo-committed, append-only ethics: edits via notes, never delete rows).
All lanes (JEEVES/K3/Claude/Kimi/Cursor) interact via this CLI or the MCP tools
(connections.search / connections.log) so outreach never duplicates.
"""
import sqlite3, sys, os, json, datetime

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "connections.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS contacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE,
  org TEXT, role TEXT, channel TEXT DEFAULT 'email',
  source TEXT DEFAULT '', status TEXT DEFAULT 'new',
  notes TEXT DEFAULT '', created_at TEXT, updated_at TEXT
);
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  contact_id INTEGER, direction TEXT DEFAULT 'out',
  subject TEXT, body TEXT, status TEXT DEFAULT 'sent',
  ts TEXT, archive TEXT DEFAULT '', move_id TEXT DEFAULT '',
  FOREIGN KEY(contact_id) REFERENCES contacts(id)
);
CREATE TABLE IF NOT EXISTS accounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  service TEXT, account_id TEXT, email TEXT,
  status TEXT DEFAULT 'active', token_ref TEXT DEFAULT '',
  created_at TEXT, updated_at TEXT, UNIQUE(service, account_id)
);
CREATE TABLE IF NOT EXISTS moves (
  id TEXT PRIMARY KEY, title TEXT, owner TEXT DEFAULT 'LANE',
  gate_state TEXT DEFAULT 'open', last_action TEXT, updated_at TEXT
);
"""
now = lambda: datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

SEED = [
    # (email, org, role, channel, source, status, notes)
    ("hello@metr.org", "METR", "measurements lead", "email", "pack-v2 2026-08-24", "awaiting", "METR pack v2 sent; GPT-5.6 Sol hook; co-sign offer; no free tokens"),
    ("drcf@fca.org.uk", "DRCF (FCA secretariat)", "digital regulators forum", "email", "phase-2 2026-08-25", "awaiting", "Phase 2 signed-feed pilot offer; ASRS pre-commitment structure"),
    ("media-types@iana.org", "IANA media-types list", "expert-review", "email", "vnd.cibola 2026-08-25", "awaiting", "community review for application/vnd.cibola.measurement-card+json"),
    ("giulio.tanganelli@equidam-88d5f8b18090.intercom-mail.com", "Equidam", "Giulio (valuation partner)", "email", "inbound 25 Aug", "awaiting", "full-report question; Aug 19 call CANCELED — reschedule"),
    ("zainab@inngot.com", "Inngot", "Zainab Miah (IP services)", "email", "profile 15 Aug", "active", "Goldseam MLKX-CDVI profile; IP services thread open"),
    ("info@onboarding.tracxn.com", "Tracxn", "onboarding", "email", "tracked 17 Aug", "active", "CSOAI tracked 104/1,061; onboarding 12 x; 101 emails re AI data access"),
    ("kervin@ssl.com", "SSL.com", "Kervin Sanchez (C2PA certs)", "email", "C2PA thread", "active", "C2PA inquiry thread; 4 msgs since Jul 28"),
    ("ebarratt@linuxfoundation.org", "Linux Foundation", "Erin Barratt (C2PA membership)", "email", "application 1 Aug", "done", "C2PA Contributor Member — docusign 7C9592DB"),
    ("partnerships@trustcloud.ai", "TrustCloud", "partnerships", "email", "Apr 27", "paused", "auditor-verifiable certificates pitch; no reply tracked"),
    ("jhillier@certisyn.com", "Certisyn", "SCITT WG co-author, jhillier", "email", "SCITT thread 25 Aug", "active", "ESI interop citable report proposal thread"),
    ("BSI Standards Development", "BSI", "ART/1 seat", "portal", "activation 25 Aug", "activated", "account activated via link; seat application pack at SOVOS/BSI_ART1_SEAT"),
    ("noreply@stripe.com", "Stripe", "payments", "portal", "keystone chain", "owner-gated", "sync-vercel keys → live-flip; money gate"),
]

def conn():
    c = sqlite3.connect(DB)
    c.executescript(SCHEMA)
    return c

def upsert_contact(c, email, org=None, role=None, channel=None, source=None, status=None, notes=None):
    ts = now()
    c.execute("INSERT INTO contacts(email,org,role,channel,source,status,notes,created_at,updated_at) "
              "VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(email) DO UPDATE SET "
              "org=COALESCE(excluded.org,org),role=COALESCE(excluded.role,role),channel=COALESCE(excluded.channel,channel),"
              "source=COALESCE(excluded.source,source),status=COALESCE(excluded.status,status),"
              "notes=CASE WHEN excluded.notes!='' THEN excluded.notes ELSE notes END, updated_at=excluded.updated_at",
              (email, org, role, channel or 'email', source or '', status or 'new', notes or '', ts, ts))
    c.execute("SELECT id FROM contacts WHERE email=?", (email,))
    return c.execute("SELECT id FROM contacts WHERE email=?", (email,)).fetchone()[0]

def log_msg(c, email, subject, direction='out', status='sent', body='', archive='', move_id=''):
    cid = upsert_contact(c, email)
    ts = now()
    c.execute("INSERT INTO messages(contact_id,direction,subject,body,status,ts,archive,move_id) VALUES(?,?,?,?,?,?,?,?)",
              (cid, direction, subject, body, status, ts, archive, move_id))
    c.execute("UPDATE contacts SET updated_at=?, status=COALESCE(NULLIF(?, ''), status) WHERE id=?", (ts, status, cid))
    return cid

def main():
    args = sys.argv[1:]
    c = conn()
    cmd = args[0] if args else 'stats'
    if cmd == 'init':
        print(f"DB ready: {DB}")
    elif cmd == 'seed':
        for row in SEED:
            upsert_contact(c, *row[:7]) if len(row) == 7 else upsert_contact(c, *row)
        c.commit(); print(f"seeded {len(SEED)}")
    elif cmd == 'add':
        e = args[1]; kw = dict(a.split('=') for a in args[2:] if '=' in a)
        upsert_contact(c, e, **{k: kw[k] for k in ('org','role','channel','source','status','notes') if k in kw})
        c.commit(); print(f"added {e}")
    elif cmd == 'log':
        e = args[1]; kw = dict(a.split('=') for a in args[2:] if '=' in a)
        cid = log_msg(c, e, kw.get('subject',''), kw.get('direction','out'), kw.get('status','sent'),
                      kw.get('body',''), kw.get('archive',''), kw.get('move_id',''))
        c.commit(); print(f"logged msg {cid} -> {e}")
    elif cmd == 'search':
        term = args[1]
        rows = c.execute("SELECT email,org,status FROM contacts WHERE email LIKE ? OR org LIKE ? OR notes LIKE ?", (f"%{term}%",)*3).fetchall()
        for r in rows: print(r)
        for m in c.execute("SELECT m.subject,m.status,m.ts FROM messages m JOIN contacts c ON m.contact_id=c.id WHERE c.email LIKE ? OR m.subject LIKE ?", (f"%{term}%",)*2).fetchall():
            print('  MSG', m)
    elif cmd == 'list':
        rows = c.execute("SELECT email,org,status,updated_at FROM contacts ORDER BY updated_at DESC LIMIT 40").fetchall()
        for r in rows: print(' | '.join(str(x) for x in r))
    elif cmd == 'account':
        if len(args) >= 4 and args[1] == 'add':
            ts = now()
            c.execute("INSERT OR IGNORE INTO accounts(service,account_id,email,status,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                      (args[2], args[3], args[4] if len(args) > 4 else '', 'active', ts, ts))
            c.commit(); print('account added')
    else:
        ts = now()
        print(f"stats — contacts={c.execute('SELECT COUNT(*) FROM contacts').fetchone()[0]}, "
              f"messages={c.execute('SELECT COUNT(*) FROM messages').fetchone()[0]}, "
              f"accounts={c.execute('SELECT COUNT(*) FROM accounts').fetchone()[0]}, ts={ts}")

if __name__ == '__main__':
    main()
