import sys, json, numpy as np, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0,'.')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from repro_validacion import M,V,T,A,TR,kfit
AZ,RJ,GR,AZC='#1f4e9c','#c23b2e','#8a94a6','#a9c1e8'
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.25,'grid.linewidth':.6,'axes.axisbelow':True,'font.family':'DejaVu Sans'})
J=json.load(open('/home/claude/work/app/data/validacion.json',encoding='utf-8'))
INI=list('EFMAMJJASOND')
MES=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
def save(f,n): f.tight_layout(); f.savefig(f'fig/{n}.pdf'); f.savefig(f'fig/{n}.png',dpi=130); plt.close(f)

# 1 anual
an=J['anual']; yrs=[a['anio'] for a in an]; x=np.arange(len(yrs)); w=.27
f,ax=plt.subplots(figsize=(6.4,3.1))
ax.bar(x-w,[a['modis_observado']/1e3 for a in an],w,color=RJ,label='MODIS observado (Terra+Aqua)')
ax.bar(x,[a['viirs_armonizado']/1e3 for a in an],w,color=AZ,label='VIIRS armonizado')
ax.bar(x+w,[a['viirs_crudo']/1e3 for a in an],w,color=AZC,label='VIIRS sin armonizar')
ax.set_xticks(x); ax.set_xticklabels(yrs,rotation=0,fontsize=8); ax.set_ylabel('Hotspots por año (miles)'); ax.legend(frameon=False,fontsize=8,loc='upper right',ncol=1)
save(f,'fig_anual')

# 2 factores nacionales por mes
k,knat=kfit(M,V,TR,'estado-mes'); yt=[y-2000 for y in range(2003,2012)]
kT=M[yt].sum((0,2))/T[yt].sum((0,2))
f,(a1,a2)=plt.subplots(1,2,figsize=(6.4,2.8))
a1.bar(range(12),knat,color=AZ); a1.set_xticks(range(12)); a1.set_xticklabels(INI,fontsize=8); a1.set_ylabel(r'$k^{V}_{\mathrm{nac},m}$ (MODIS por detección VIIRS)'); a1.set_title('VIIRS → MODIS (2012–2019)',fontsize=9)
for i,v in enumerate(knat): a1.text(i,v+.004,f'{v:.2f}',ha='center',fontsize=6.5)
a2.bar(range(12),kT,color=RJ); a2.set_xticks(range(12)); a2.set_xticklabels(INI,fontsize=8); a2.set_ylabel(r'$k^{T}_{\mathrm{nac},m}$ (Terra+Aqua por detección Terra)'); a2.set_title('Terra → Terra+Aqua (2003–2011)',fontsize=9)
for i,v in enumerate(kT): a2.text(i,v+.03,f'{v:.2f}',ha='center',fontsize=6.5)
a1.set_ylim(0,.36); a2.set_ylim(0,3.0)
for a in (a1,a2): a.yaxis.label.set_size(7.5)
save(f,'fig_knat')

# 3 contracción
s=np.logspace(0.5,5.5,300); f,ax=plt.subplots(figsize=(6.0,2.9))
for tau,c,ls,lw in [(30,GR,'--',1),(100,AZ,'-',2.2),(300,GR,':',1.4)]: ax.plot(s,s/(s+tau),color=c,ls=ls,lw=lw,label=fr'$\tau={tau}$')
ex=[(22,'Tlaxcala, nov.'),(113412,'Guerrero, may.')]
for v,lab in ex:
    ax.plot([v],[v/(v+100)],'o',color=RJ,ms=5); ax.annotate(lab+f'\n$\\omega={v/(v+100):.3f}$',(v,v/(v+100)),textcoords='offset points',xytext=(-60,30) if v<100 else (-80,-34),fontsize=7.5,color=RJ,arrowprops=dict(arrowstyle='-',color=RJ,lw=.6))
ax.set_xscale('log'); ax.set_xlabel(r'Detecciones VIIRS de entrenamiento en la celda estado–mes, $\sum V$'); ax.set_ylabel(r'Peso propio $\omega=\sum V/(\sum V+\tau)$'); ax.set_ylim(0,1.05); ax.legend(frameon=False,fontsize=8,loc='lower right')
save(f,'fig_contraccion')

# 4 niveles
niv=J['niveles']; lab=['Factor único','Factor por mes','Factor por\nestado y mes']; x=np.arange(3); w=.36
f,ax=plt.subplots(figsize=(6.0,2.9))
l=[n['loyo']['wape_estado_mes']*100 for n in niv]; h=[n['holdout']['wape_estado_mes']*100 for n in niv]
b1=ax.bar(x-w/2,l,w,color=AZ,label='Un año fuera, 2012–2019'); b2=ax.bar(x+w/2,h,w,color=RJ,label='Fuera de muestra, 2020–2025')
for b in list(b1)+list(b2): ax.text(b.get_x()+b.get_width()/2,b.get_height()+.4,f'{b.get_height():.1f}',ha='center',fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(lab); ax.set_ylabel('Error por estado y mes (WAPE, %)'); ax.set_ylim(0,30); ax.legend(frameon=False,fontsize=8,loc='upper right')
save(f,'fig_niveles')

# 5 estacionalidad
import pandas as pd
d=pd.read_csv('/home/claude/work/entrega/calendario_quemas/datos_armonizados/hotspots_armonizados_estado_mes.csv')
a=d.groupby(['anio','mes']).hotspots_armonizados.sum().unstack(level=1).fillna(0).loc[2001:]
sh=a.sum(axis=0)/a.values.sum()*100
f,ax=plt.subplots(figsize=(6.0,2.7))
ax.bar(range(12),sh.values,color=[RJ if m in (4,5) else AZ for m in range(1,13)])
for i,v in enumerate(sh.values): ax.text(i,v+.6,f'{v:.1f}',ha='center',fontsize=7.5)
ax.set_xticks(range(12)); ax.set_xticklabels(MES); ax.set_ylabel('% de los hotspots del año'); ax.set_ylim(0,44)
save(f,'fig_estacionalidad'); print('abr+may',sh[[4,5]].sum(),'mar-jun',sh[[3,4,5,6]].sum())

# 6 decaimiento
h=np.arange(0,181); f,ax=plt.subplots(figsize=(6.0,2.7))
ax.plot(h,np.exp(-h/60),color=AZ,lw=2.2)
for hh in (30,60,120):
    ax.plot([hh],[np.exp(-hh/60)],'o',color=RJ,ms=5); ax.annotate(f'h={hh}: {np.exp(-hh/60):.2f}',(hh,np.exp(-hh/60)),textcoords='offset points',xytext=(6,6),fontsize=8,color=RJ)
ax.axhline(.5,color=GR,lw=.8,ls='--'); ax.text(178,.52,'vida media ≈ 42 días',ha='right',fontsize=8,color=GR)
ax.set_xlabel('Horizonte h (días)'); ax.set_ylabel(r'Peso del ajuste, $e^{-h/\tau}$, $\tau=60$'); ax.set_ylim(0,1.05)
save(f,'fig_decaimiento')

# 7 pronóstico 2026
S=json.load(open('/home/claude/work/deck/series.json')); p=S['pron']; x=np.arange(12)
f,ax=plt.subplots(figsize=(6.4,3.1))
ax.fill_between(x,np.array(p['lo'])/1e3,np.array(p['hi'])/1e3,color=AZC,alpha=.7,label='Intervalo de 80 % (por mes)')
ax.plot(x,np.array(p['pred'])/1e3,color=AZ,lw=2.2,marker='o',ms=3.5,label='Pronóstico 2026')
ax.plot(x,np.array(S['obs2025'])/1e3,color=RJ,lw=1.8,marker='s',ms=3,label='Observado 2025')
ax.plot(x,np.array(S['clim13_25'])/1e3,color=GR,lw=1.2,ls='--',label='Promedio 2013–2025')
ax.set_xticks(x); ax.set_xticklabels(MES); ax.set_ylabel('Hotspots equivalentes por mes (miles)'); ax.legend(frameon=False,fontsize=8)
save(f,'fig_pron2026')

# 8 error del pronóstico
P=J['pronostico']; f,axs=plt.subplots(1,2,figsize=(6.6,2.9),sharey=False)
lv=['day','week','month']; ln=['Diario','Semanal','Mensual']; x=np.arange(3); w=.26
nat=P['nacional']; est=P['estados']
vals_n={'m':[nat[l]['modelo']*100 for l in lv],'c':[nat[l]['clim']*100 for l in lv],'n':[nat[l]['naive']*100 for l in lv]}
vals_e={'m':[est[l]['mediana_modelo']*100 for l in lv],'c':[est[l]['mediana_clim']*100 for l in lv],'n':[est[l]['mediana_naive']*100 for l in lv]}
for ax,v,t in [(axs[0],vals_n,'Todo México'),(axs[1],vals_e,'Mediana de los 32 estados')]:
    for i,(k,c,lab) in enumerate([('m',AZ,'Modelo'),('c',GR,'Solo climatología'),('n',RJ,'Mismo periodo, año anterior')]):
        bb=ax.bar(x+(i-1)*w,v[k],w,color=c,label=lab)
        for b in bb: ax.text(b.get_x()+b.get_width()/2,b.get_height()+.8,f'{b.get_height():.0f}',ha='center',fontsize=7)
    ax.set_xticks(x); ax.set_xticklabels(ln); ax.set_title(t,fontsize=9)
axs[0].set_ylabel('Error (WAPE, %)'); axs[0].legend(frameon=False,fontsize=7,loc='upper left',bbox_to_anchor=(0,1.0)); axs[0].set_ylim(0,52); axs[1].set_ylim(0,105)
save(f,'fig_error_pron')
print('ok')
