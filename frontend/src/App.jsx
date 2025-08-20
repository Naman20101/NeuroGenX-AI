import React, { useState } from "react"
import UploadPanel from "./components/UploadPanel.jsx"
import RunLauncher from "./components/RunLauncher.jsx"
import MetricsCard from "./components/MetricsCard.jsx"
import TrialTable from "./components/TrialTable.jsx"

const API = import.meta.env.VITE_API || "https://YOUR-BACKEND.onrender.com"

export default function App(){
  const [dataset, setDataset] = useState(null)
  const [run, setRun] = useState(null)
  const [status, setStatus] = useState(null)
  const [champ, setChamp] = useState(null)

  return (
    <div style={{fontFamily:"Inter, system-ui", padding:16, maxWidth:900, margin:"0 auto"}}>
      <h1>NeuroGenX NG-1</h1>
      <p>Upload → Run search → Monitor → Champion → Predict</p>
      <UploadPanel API={API} onUploaded={setDataset}/>
      <RunLauncher API={API} dataset={dataset} onStarted={setRun} onStatus={setStatus}/>
      <MetricsCard API={API} champ={champ} setChamp={setChamp}/>
      <TrialTable status={status}/>
      <footer style={{marginTop:24, opacity:0.7}}>Backend: {API}</footer>
    </div>
  )
}