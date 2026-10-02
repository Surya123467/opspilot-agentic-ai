const API=import.meta.env.VITE_API_BASE_URL||'http://localhost:8000';
async function request(path:string,options:RequestInit={}){
  let r:Response;
  try{r=await fetch(`${API}${path}`,options)}catch(e){throw new Error(`Cannot reach OpsPilot API at ${API}. Make sure Docker/backend is running.`)}
  const body=await r.text();
  if(!r.ok){
    let detail=body;
    try{const parsed=JSON.parse(body); detail=parsed.detail||body}catch{}
    throw new Error(`API ${r.status}: ${detail}`)
  }
  try{return JSON.parse(body)}catch{throw new Error('OpsPilot returned an invalid JSON response.')}
}
export const runAgent=(message:string)=>request('/api/runs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message})});
export const approveRun=(id:string)=>request(`/api/runs/${id}/approve`,{method:'POST'});
export const rejectRun=(id:string)=>request(`/api/runs/${id}/reject`,{method:'POST'});
