import React from "react";

type InboxItem = {
  id: string;
  channel: string;
  receivedAt: string;
  from: string;
  name?: string;
  text?: string;
};

const API_BASE = (import.meta as any).env?.VITE_API_BASE ?? "http://localhost:8080";

export function App() {
  const [items, setItems] = React.useState<InboxItem[]>([]);
  const [loading, setLoading] = React.useState(false);

  async function refresh() {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/v1/inbox`);
      const data = (await res.json()) as { items: InboxItem[] };
      setItems(data.items ?? []);
    } finally {
      setLoading(false);
    }
  }

  React.useEffect(() => {
    refresh();
    const id = window.setInterval(refresh, 2000);
    return () => window.clearInterval(id);
  }, []);

  return (
    <div className="page">
      <header className="header">
        <div>
          <div className="title">Unified Inbox</div>
          <div className="subtitle">Multi Channel Auto Reply, Calls & Business Automation Platform</div>
        </div>
        <button className="btn" onClick={refresh} disabled={loading}>
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </header>

      <main className="content">
        <section className="card">
          <div className="cardTitle">Recent enquiries</div>
          {items.length === 0 ? (
            <div className="empty">No items yet. POST a webhook payload to the API to see it here.</div>
          ) : (
            <ul className="list">
              {items.map((it) => (
                <li key={it.id} className="row">
                  <div className="rowMain">
                    <div className="rowTop">
                      <span className={`pill pill-${it.channel}`}>{it.channel}</span>
                      <span className="from">{it.name ? `${it.name} (${it.from})` : it.from}</span>
                    </div>
                    <div className="text">{it.text ?? "(no text)"}</div>
                  </div>
                  <div className="time" title={it.receivedAt}>
                    {new Date(it.receivedAt).toLocaleString()}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="card">
          <div className="cardTitle">Test webhook</div>
          <div className="helper">
            Example: <code>POST /v1/webhooks/webchat/inbound</code> with JSON <code>{"{ \"from\":\"+91...\", \"text\":\"Hi\" }"}</code>
          </div>
        </section>
      </main>
    </div>
  );
}
