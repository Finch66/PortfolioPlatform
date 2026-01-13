import React, { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
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
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState("market_value");
  const [sortDir, setSortDir] = useState("desc");

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

  const allocationByType = portfolio?.allocation?.by_asset_type || [];
  const allocationByCurrency = portfolio?.allocation?.by_currency || [];

  const chartColors = ["#f07c3b", "#ffb174", "#f2a65a", "#e36e3f", "#f6c28b"];

  const holdings = useMemo(() => portfolio?.holdings || [], [portfolio]);
  const filteredHoldings = useMemo(() => {
    const term = search.trim().toLowerCase();
    const filtered = term
      ? holdings.filter((holding) =>
          [holding.asset_id, holding.asset_name, holding.asset_type]
            .join(" ")
            .toLowerCase()
            .includes(term)
        )
      : holdings;

    const sorted = [...filtered].sort((a, b) => {
      const dir = sortDir === "asc" ? 1 : -1;
      const key = sortKey;
      if (typeof a[key] === "number" && typeof b[key] === "number") {
        return (a[key] - b[key]) * dir;
      }
      return String(a[key]).localeCompare(String(b[key])) * dir;
    });
    return sorted;
  }, [holdings, search, sortKey, sortDir]);

  const topHoldings = useMemo(() => {
    return [...holdings]
      .sort((a, b) => b.market_value - a.market_value)
      .slice(0, 6)
      .map((holding) => ({
        name: holding.asset_id,
        value: holding.market_value
      }));
  }, [holdings]);

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

      <div className="grid two-col">
        <div className="card chart-card">
          <h3>Allocation (Asset Type)</h3>
          {!allocationByType.length ? (
            <p className="muted">Nessuna allocazione disponibile.</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={allocationByType} dataKey="market_value" nameKey="label" innerRadius={60} outerRadius={90}>
                  {allocationByType.map((entry, index) => (
                    <Cell key={entry.label} fill={chartColors[index % chartColors.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => numberFormatter.format(value)} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="card chart-card">
          <h3>Top Holdings (Market Value)</h3>
          {!topHoldings.length ? (
            <p className="muted">Nessuna posizione disponibile.</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={topHoldings}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.08)" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tickFormatter={(value) => numberFormatter.format(value)} />
                <Tooltip formatter={(value) => numberFormatter.format(value)} />
                <Bar dataKey="value" fill="#f07c3b" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="card table-card">
        <div className="table-header">
          <div>
            <h3>Holdings</h3>
            <p className="muted">Filtra e ordina le posizioni per analizzarle piu` velocemente.</p>
          </div>
          <div className="table-controls">
            <input
              type="text"
              placeholder="Cerca asset, nome o tipo"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
            <select value={sortKey} onChange={(event) => setSortKey(event.target.value)}>
              <option value="market_value">Market Value</option>
              <option value="unrealized_pl">P/L</option>
              <option value="quantity">Quantita`</option>
              <option value="asset_id">Asset</option>
              <option value="asset_type">Tipo</option>
            </select>
            <button className="ghost" onClick={() => setSortDir(sortDir === "asc" ? "desc" : "asc")}>
              {sortDir === "asc" ? "Asc" : "Desc"}
            </button>
          </div>
        </div>
        {!filteredHoldings.length ? (
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
            {filteredHoldings.map((holding) => (
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
