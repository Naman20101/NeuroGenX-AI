import React from "react"
export default function TrialTable({status}){
  return (
    <div>
      <h3>4) Live status</h3>
      <pre style={{background:"#fafafa", padding:10, borderRadius:8, maxHeight:220, overflow:"auto"}}>
{JSON.stringify(status, null, 2)}
      </pre>
    </div>
  )
}