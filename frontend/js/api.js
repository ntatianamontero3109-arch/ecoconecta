const KEY = 'ecoconecta_session';
export const session = {
  get token(){return sessionStorage.getItem(KEY)||''},
  set token(value){value?sessionStorage.setItem(KEY,value):sessionStorage.removeItem(KEY)}
};
export async function api(path,{method='GET',body}={}){
  const options={method,headers:{'Content-Type':'application/json'}};
  if(session.token) options.headers.Authorization=`Bearer ${session.token}`;
  if(body!==undefined) options.body=JSON.stringify(body);
  let response;
  try { response=await fetch('/api'+path,options); }
  catch { throw Error('Sin conexión con el servidor. Revisa tu conexión e inténtalo de nuevo.'); }
  let data; try {data=await response.json()}catch{data={detail:'Ocurrió un error inesperado'}}
  if(!response.ok){
    let message=typeof data.detail==='string'?data.detail:JSON.stringify(data.detail||'Solicitud rechazada');
    if(response.status===401 && !path.startsWith('/auth/')){session.token='';window.dispatchEvent(new Event('session-expired'))}
    throw Error(message);
  }
  return data;
}
