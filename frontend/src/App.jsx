import React, { useEffect, useMemo, useState } from "react";
import { fetchPortfolio, importTransactionsCsv } from "./api";

const numberFormatter = new Intl.NumberFormat("en-US", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
});

const percentFormatter = new Intl.NumberFormat("en-US", {
  style: "percent",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
});

function StatCard({ label, value, hint }) {
  return (
    <div className="card stat-card">
      <span className="stat-label">{label}</span>
      <strong className="stat-value">{value}</strong>
      {hint && <span className="stat-hint">{hint}</span>}
    </div>
  );
}

function AllocationBlock({ title, buckets }) {
  if (!buckets?.length) {
    return (
      <div className="card allocation-card">
        <h3>{title}</h3>
        <p className="muted">No allocation data yet.</p>
      </div>
    );
  }

  return (
    <div className="card allocation-card">
      <h3>{title}</h3>
      <div className="allocation-list">
        {buckets.map((bucket) => (
          <div key={bucket.label} className="allocation-row">
            <div className="allocation-meta">
              <span>{bucket.label}</span>
              <span>{percentFormatter.format(bucket.weight)}</span>
            </div>
            <div className="allocation-bar">
              <span style={{ width: `${Math.max(bucket.weight * 100, 4)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function App() {
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [file, setFile] = useState(null);
  const [importState, setImportState] = useState({ status: "idle", result: null, error: "" });

  const loadPortfolio = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await fetchPortfolio();
      setPortfolio(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPortfolio();
  }, []);

  const metrics = useMemo(() => {
    return portfolio?.metrics || {
      total_assets: 0,
      total_market_value: 0,
      total_invested: 0,
      total_unrealized_pl: 0,
      total_unrealized_pl_pct: 0
    };
  }, [portfolio]);

  const onFileChange = (event) => {
    setFile(event.target.files?.[0] || null);
    setImportState({ status: "idle", result: null, error: "" });
  };

  const onDrop = (event) => {
    event.preventDefault();
    setFile(event.dataTransfer.files?.[0] || null);
    setImportState({ status: "idle", result: null, error: "" });
  };

  const onImport = async () => {
    if (!file) return;
    setImportState({ status: "loading", result: null, error: "" });
    try {
      const result = await importTransactionsCsv(file);
      setImportState({ status: "done", result, error: "" });
      await loadPortfolio();
    } catch (err) {
      setImportState({ status: "error", result: null, error: err.message });
    }
  };

  return (
    <div className="app">
      <div className="hero">
        <div>
          <span className="chip">Local Only</span>
          <h1>Portfolio Console</h1>
          <p>
            Importa CSV, monitora l&apos;allocazione e controlla le metriche del tuo
            portafoglio in tempo reale.
          </p>
        </div>
        <button className="ghost" onClick={loadPortfolio} disabled={loading}>
          {loading ? "Aggiornamento..." : "Aggiorna dati"}
        </button>
      </div>

      <div className="grid metrics-grid">
        <StatCard label="Market Value" value={`${numberFormatter.format(metrics.total_market_value)}`} />
        <StatCard label="Invested" value={`${numberFormatter.format(metrics.total_invested)}`} />
        <StatCard
          label="Unrealized P/L"
          value={`${numberFormatter.format(metrics.total_unrealized_pl)}`}
          hint={percentFormatter.format(metrics.total_unrealized_pl_pct)}
        />
        <StatCard label="Assets" value={`${metrics.total_assets}`} />
      </div>

      <div className="grid two-col">
        <div className="card upload-card" onDragOver={(e) => e.preventDefault()} onDrop={onDrop}>
          <h3>Import CSV</h3>
          <p className="muted">
            Trascina il file oppure selezionalo. Il formato e` descritto in
            docs/sample-portfolio.csv.
          </p>
          <div className="upload-area">
            <input type="file" accept=".csv" onChange={onFileChange} />
            <span>{file ? file.name : "Nessun file selezionato"}</span>
          </div>
          <button className="primary" onClick={onImport} disabled={!file || importState.status === "loading"}>
            {importState.status === "loading" ? "Import in corso..." : "Carica CSV"}
          </button>
          {importState.status === "done" && (
            <div className="import-result success">
              <strong>Import completato</strong>
              <span>Inserite: {importState.result.inserted}</span>
              <span>Saltate: {importState.result.skipped}</span>
            </div>
          )}
          {importState.status === "error" && (
            <div className="import-result error">
              <strong>Errore import</strong>
              <span>{importState.error}</span>
            </div>
          )}
        </div>

        <div className="card insight-card">
          <h3>Note rapide</h3>
          <ul>
            <li>I dati restano nel tuo database locale.</li>
            <li>I prezzi attuali sono stimati dall&apos;ultimo trade.</li>
            <li>Quando vuoi, colleghiamo una fonte prezzi esterna.</li>
          </ul>
          {error && <p className="error-text">Errore API: {error}</p>}
        </div>
      </div>

      <div className="grid two-col">
        <AllocationBlock title="Allocation by Asset Type" buckets={portfolio?.allocation?.by_asset_type} />
        <AllocationBlock title="Allocation by Currency" buckets={portfolio?.allocation?.by_currency} />
      </div>

      <div className="card table-card">
        <h3>Holdings</h3>
        {!portfolio?.holdings?.length ? (
          <p className="muted">Nessuna posizione: importa un CSV per iniziare.</p>
        ) : (
          <div className="table">
            <div className="table-row header">
              <span>Asset</span>
              <span>Type</span>
              <span>Qty</span>
              <span>Avg Cost</span>
              <span>Last Price</span>
              <span>Market Value</span>
              <span>P/L</span>
            </div>
            {portfolio.holdings.map((holding) => (
              <div className="table-row" key={`${holding.asset_id}-${holding.currency}`}>
                <span>
                  <strong>{holding.asset_id}</strong>
                  <small>{holding.asset_name}</small>
                </span>
                <span>{holding.asset_type}</span>
                <span>{holding.quantity.toFixed(6)}</span>
                <span>{numberFormatter.format(holding.average_cost)}</span>
                <span>{numberFormatter.format(holding.last_price)}</span>
                <span>{numberFormatter.format(holding.market_value)}</span>
                <span className={holding.unrealized_pl >= 0 ? "pos" : "neg"}>
                  {numberFormatter.format(holding.unrealized_pl)}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
