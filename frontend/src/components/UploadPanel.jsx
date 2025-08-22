import React, { useState } from "react"
export default function UploadPanel({API, onUploaded}){
  const [cols, setCols] = useState([])
  async function onChange(e){
    const f = e.target.files[0]
    const fd = new FormData(); fd.append("file", f)
    const r = await fetch(`${API}/datasets/upload`, {method:"POST", body: fd})
    const j = await r.json()
    setCols(j.columns); onUploaded(j)
  }
  return (
    <div>
      <h3>1) Upload CSV</h3>
      <input type="file" accept=".csv" onChange={onChange}/>
      {cols.length>0 && <small>Detected columns: {cols.join(", ")}</small>}
    </div>
  )
}
