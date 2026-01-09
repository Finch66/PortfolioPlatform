# React: concetti base (mini guida)

## Cos e React
React e una libreria JavaScript per costruire interfacce utente a componenti.
La UI e una funzione dello stato: se lo stato cambia, la UI si aggiorna.

## Componenti
Un componente e una funzione che ritorna JSX (HTML-like):
```jsx
function Card({ title }) {
  return <div>{title}</div>;
}
```

## JSX
Sintassi che assomiglia a HTML ma e JavaScript:
- Attributi camelCase: `className`, `onClick`
- Puoi inserire espressioni con `{}`:
```jsx
<h1>{user.name}</h1>
```

## Props
Sono i parametri che passi a un componente:
```jsx
<Card title="Portfolio" />
```
Dentro il componente: `function Card({ title }) { ... }`

## State (useState)
Serve per dati che cambiano nel tempo:
```jsx
const [count, setCount] = useState(0);
```
Quando chiami `setCount`, React ricalcola la UI.

## Effetti (useEffect)
Per eseguire codice quando il componente si monta o cambia stato:
```jsx
useEffect(() => {
  fetchData();
}, []);
```
`[]` significa: esegui solo al mount.

## Fetch di dati
Tipico pattern:
```jsx
useEffect(() => {
  async function load() {
    const data = await fetch("/api").then((r) => r.json());
    setData(data);
  }
  load();
}, []);
```

## Eventi
Eventi DOM come `onClick`, `onChange`:
```jsx
<button onClick={() => setCount(count + 1)}>+</button>
```

## Rendering condizionale
Mostrare elementi solo se esistono dati:
```jsx
{error && <p>{error}</p>}
```

## Liste
Per renderizzare array:
```jsx
items.map((item) => <li key={item.id}>{item.name}</li>)
```

## Struttura tipica
- `App.jsx`: entry principale
- `components/`: componenti riutilizzabili
- `api.js`: chiamate API

## Cosa studiare dopo
- React Router (navigazione)
- State management (Context / Zustand)
- Charting (Recharts, Chart.js)
- Forms (React Hook Form)
