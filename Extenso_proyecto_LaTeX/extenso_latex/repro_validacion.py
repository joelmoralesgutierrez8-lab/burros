"""Reproduce, desde el CSV mensual publicado, los números de validación del extenso."""
import json, numpy as np, pandas as pd
CSV='/home/claude/work/entrega/calendario_quemas/datos_armonizados/hotspots_armonizados_estado_mes.csv'
d=pd.read_csv(CSV)
claves=sorted(d.estado.unique()); NS=len(claves); idx={c:i for i,c in enumerate(claves)}
def arr(col):
    a=np.zeros((26,12,NS))
    for r in d.itertuples(): a[r.anio-2000, r.mes-1, idx[r.estado]] += getattr(r,col)
    return a
T=arr('modis_terra'); A=arr('modis_aqua'); V=arr('viirs_snpp'); M=T+A
def kfit(Mx,X,years,level,tau=100.0,mask=True):
    yi=[y-2000 for y in years]; n,dd=Mx[yi].copy(),X[yi].copy()
    if mask and 2012 in years and years[0]==2012:
        j=years.index(2012); n[j,0]=0; dd[j,0]=0
    ns,ds=n.sum(0),dd.sum(0)
    if level=='global': return np.full_like(ns,ns.sum()/ds.sum())
    knat=ns.sum(1)/ds.sum(1)
    if level=='mes': return np.repeat(knat[:,None],NS,1)
    return (ns+tau*knat[:,None])/(ds+tau), knat
def score(pred,obs,years):
    pred,obs=pred.copy(),obs.copy()
    if 2012 in years:
        j=years.index(2012); pred[j,0]=np.nan; obs[j,0]=np.nan
    ok=~np.isnan(obs); sm=np.abs(pred-obs)[ok].sum()/obs[ok].sum()
    pn,on=np.nansum(pred,2),np.nansum(obs,2); bad=np.isnan(obs).all(2); pn[bad]=np.nan; on[bad]=np.nan
    nm=np.nansum(np.abs(pn-on))/np.nansum(on)
    an=np.abs(np.nansum(pred,(1,2))-np.nansum(obs,(1,2))).sum()/np.nansum(obs)
    return dict(sm=sm,nm=nm,an=an,sesgo=(np.nansum(pred)-np.nansum(obs))/np.nansum(obs))
TR,TE=list(range(2012,2020)),list(range(2020,2026))
def ev(level,tau=100.0):
    f=[]
    for y in TR:
        tr=[t for t in TR if t!=y]; k=kfit(M,V,tr,level,tau); k=k[0] if isinstance(k,tuple) else k
        f.append(score(V[[y-2000]]*k[None],M[[y-2000]],[y]))
    loyo={q:np.mean([x[q] for x in f]) for q in f[0]}
    k=kfit(M,V,TR,level,tau); k=k[0] if isinstance(k,tuple) else k
    ho=score(V[[y-2000 for y in TE]]*k[None],M[[y-2000 for y in TE]],TE)
    return loyo,ho
if __name__=='__main__':
    ref=json.load(open('/home/claude/work/app/data/validacion.json',encoding='utf-8'))['niveles']
    for lv,r in zip(['global','mes','estado-mes'],ref):
        l,h=ev(lv); print(lv,'LOYO sm %.4f (json %.4f) an %.4f (%.4f) | HO sm %.4f (%.4f) an %.4f (%.4f)'%(l['sm'],r['loyo']['wape_estado_mes'],l['an'],r['loyo']['wape_anual'],h['sm'],r['holdout']['wape_estado_mes'],h['an'],r['holdout']['wape_anual']))
    print('--- sensibilidad a tau (estado-mes)')
    for tau in [0,10,30,100,300,1000]:
        l,h=ev('estado-mes',tau); print(tau,'LOYO sm %.4f an %.4f | HO sm %.4f an %.4f'%(l['sm'],l['an'],h['sm'],h['an']))
    k,knat=kfit(M,V,TR,'estado-mes')
    print('knat',np.round(knat,3).tolist()); print('1/knat',np.round(1/knat,2).tolist())
    print('k rango',k.min().round(3),k.max().round(3))
