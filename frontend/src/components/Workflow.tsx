type Props={steps:string[]; completed?:boolean};
const nodes=['Planner','RAG Researcher','Tool Executor','Reviewer','Finalizer'];
export default function Workflow({steps,completed=false}:Props){
  const activeCount=completed?nodes.length:Math.min(steps.length,nodes.length);
  return <div className="workflow">{nodes.map((n,i)=><div className="workflow-row" key={n}>
    <div className={`node ${i<activeCount?'active':''}`}><span>{i+1}</span><div><strong>{n}</strong><small>{i<steps.length?steps[i]:completed?'Completed':'Waiting'}</small></div></div>
    {i<nodes.length-1&&<div className="connector"/>}
  </div>)}</div>
}
