export default function ResultsList({ places, selected, onSelect, onAskFollowup }) {
  return (
    <div className="results-panel">
      <div className="results-header">
        <div className="results-title">Ranked Results</div>
        <div className="results-subtitle">
          Click a card to focus it on the map
        </div>
      </div>

      <div className="results">
        {places.length === 0 ? (
          <div className="results-empty">
            No places yet. Ask Atlas a place-based question to begin.
          </div>
        ) : (
          places.map((p) => {
            const isSelected = selected?.id === p.id;

            return (
              <div
                key={p.id}
                onClick={() => onSelect(p)}
                className={`card ${isSelected ? "selected-card" : ""}`}
              >
                <div className="card-top">
                  <div className="card-title">
                    <span className="rank-badge">{p.rank}</span>
                    <span>{p.name}</span>
                  </div>

                  <div className="card-metrics">
                    <span>⭐ {p.rating ?? "N/A"}</span>
                    <span>{p.distance_km ?? "N/A"} km</span>
                  </div>
                </div>

                <div className="card-address">
                  {p.address || "Address unavailable"}
                </div>

                <div className="card-tags">
                  {p.category ? <span className="tag">{p.category}</span> : null}
                  <span className={`tag ${p.open_now ? "open" : "closed"}`}>
                    {p.open_now ? "Open now" : "Closed / unknown"}
                  </span>
                </div>

                <div className="card-actions">
                  <button
                    type="button"
                    className="secondary-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelect(p);
                    }}
                  >
                    Show on map
                  </button>

                  <button
                    type="button"
                    className="ghost-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      onAskFollowup?.(`Tell me more about ${p.name}`);
                    }}
                  >
                    Ask follow-up
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}