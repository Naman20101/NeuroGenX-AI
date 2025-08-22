import React, { useState } from "react"
import { v4 as uuidv4 } from 'uuid';

export default function UploadPanel({API, onUploaded}){
  const [cols, setCols] = useState([])

  async function onChange(e){
    const f = e.target.files[0]
    // Generate a unique ID for the dataset right here in the browser
    const datasetId = uuidv4();
    
    // Append the file and the new dataset ID to the form data
    const fd = new FormData();
    fd.append("file", f);
    fd.append("dataset_id", datasetId); // Pass the new ID to the backend
    
    // Send the upload request
    const r = await fetch(`${API}/datasets/upload`, {method:"POST", body: fd})
    const j = await r.json()
    
    // Now we are sure the returned ID is the unique one we just generated
    setCols(j.columns);
    onUploaded(j);
  }

  return (
    <div>
      <h3>1) Upload CSV</h3>
      <input type="file" accept=".csv" onChange={onChange}/>
      {cols.length > 0 && <small>Detected columns: {cols.join(", ")}</small>}
    </div>
  )
}
