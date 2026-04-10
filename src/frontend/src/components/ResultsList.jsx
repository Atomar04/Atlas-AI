export default function ResultsList({ places, onSelect }) {
  return (
    <div className="results">
      {places.map((p) => (
        <div key={p.id} onClick={() => onSelect(p)} className="card">
          {p.rank}. {p.name} ⭐{p.rating} ({p.distance_km} km)
        </div>
      ))}
    </div>
  );
}