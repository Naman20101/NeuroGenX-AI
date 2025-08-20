import React from "react"
export default function MetricsCard({API, champ, setChamp}){
  async function refresh(){
    const r = await fetch(`${API}/models/champion`)
    const j = await r.json()
    setChamp(j.detail ? null : j)
  }
  return (
    <div>
      <h3>3) Champion</h3>
      <button onClick={refresh}>Refresh</button>
      {champ ? (
        <pre style={{background:"#f5f5f5", padding:10, borderRadius:8}}>
{JSON.stringify(champ.metrics, null, 2)}
        </pre>
      ) : <small>No champion yet.</small>}
    </div>
  )
}