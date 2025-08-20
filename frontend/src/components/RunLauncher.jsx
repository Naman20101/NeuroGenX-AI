import React, { useState, useEffect } from "react"
export default function RunLauncher({API, dataset, onStarted, onStatus}){
  const [target, setTarget] = useState("")
  const [trials, setTrials] = useState(40)
  const [runId, setRunId] = useState(null)
  useEffect(()=>{
    if(!runId) return
    const id = setInterval(async ()=>{
      const r = await fetch(`${API}/runs/${runId}/status`)
      onStatus(await r.json())
    }, 1500)
    return ()=>clearInterval(id)
  }, [runId])
  async function launch(){
    const body = {dataset_id: dataset.dataset_id, target, n_trials: Number(trials)}
    const r = await fetch(`${API}/runs/start`, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body)})
    const j = await r.json()
    setRunId(j.run_id); onStarted(j)
  }
  return (
    <div>
      <h3>2) Launch run</h3>
      {dataset ? (
        <div>
          <label>Target column: </label>
          <input value={target} onChange={e=>setTarget(e.target.value)} placeholder="e.g. Class"/>
          <label style={{marginLeft:12}}>Trials:</label>
          <input type="number" min="5" max="200" value={trials} onChange={e=>setTrials(e.target.value)}/>
          <button onClick={launch} disabled={!target}>Start</button>
        </div>
      ) : <small>Upload a dataset first.</small>}
      {runId && <div>Run ID: {runId}</div>}
    </div>
  )
}