"""Genera fragmentos LaTeX (tablas y macros numéricas) desde los resultados verificados, para que el texto no lleve números tecleados a mano."""
import sys, json, numpy as np, warnings
warnings.filterwarnings('ignore'); sys.path.insert(0,'.')
from repro_validacion import M,V,T,A,TR,TE,kfit,claves,d
J=json.load(open('/home/claude/work/app/data/validacion.json',encoding='utf-8'))
S=json.load(open('/home/claude/work/deck/series.json'))
OUT='tex/'
def f1(x): return f'{x*100:.1f}'.replace('.',',') if False else f'{x*100:.1f}'
def pct(x,dec=1): return f'{x*100:.{dec}f}'
def w(name,s):
    s=s.rstrip()
    if s.endswith('\\\\'): s=s[:-2].rstrip()
    open(OUT+name,'w',encoding='utf-8').write(s+'\n')

# ---- tabla de niveles
rows=[]
for n in J['niveles']:
    l,h=n['loyo'],n['holdout']
    rows.append(f"{n['nombre'].replace('τ','$\\tau$')} & {pct(l['wape_estado_mes'])} & {pct(h['wape_estado_mes'])} & {pct(l['wape_nacional_mes'])} & {pct(h['wape_nacional_mes'])} & {pct(l['wape_anual'])} & {pct(h['wape_anual'])} \\\\")
w('tab_niveles.tex','\n'.join(rows))
rows=[]
for n in J['niveles']:
    l,h=n['loyo'],n['holdout']
    rows.append(f"{n['nombre'].replace('τ','$\\tau$')} & {pct(l['sesgo'],2)} & {pct(h['sesgo'],2)} & {l['r_nacional_mes']:.4f} & {h['r_nacional_mes']:.4f} \\\\")
w('tab_sesgo.tex','\n'.join(rows).replace('& -','& $-$'))
# ---- variantes
rows=[]
for n in J['variantes']:
    l,h=n['loyo'],n['holdout']; nom=n['nombre'].replace('≥','$\\geq$').replace(' (elegida)','').replace('Huella +','Huella de 1 km $+$')
    if 'elegida' in n['nombre']: nom='\\textbf{Sin huella ni umbral de FRP (elegida)}'
    rows.append(f"{nom} & {pct(l['wape_estado_mes'])} & {pct(h['wape_estado_mes'])} & {pct(l['wape_anual'])} & {pct(h['wape_anual'])} & {pct(h['sesgo'],1)} \\\\")
w('tab_variantes.tex','\n'.join(rows).replace('& -','& $-$'))
t=J['terra']; w('num_terra.tex',f"\\newcommand{{\\terraSM}}{{{pct(t['wape_estado_mes'])}}}\\newcommand{{\\terraNM}}{{{pct(t['wape_nacional_mes'])}}}\\newcommand{{\\terraAN}}{{{pct(t['wape_anual'])}}}\\newcommand{{\\terraSesgo}}{{{pct(t['sesgo'],2)}}}\n")
# ---- sensibilidad a tau (recalculada desde los CSV)
from repro_validacion import ev
rows=[]
for tau in [0,10,30,100,300,1000]:
    l,h=ev('estado-mes',tau); mark='\\textbf{%s}' if tau==100 else '%s'
    rows.append(' & '.join([mark%str(tau)]+[mark%pct(x) for x in (l['sm'],h['sm'],l['an'],h['an'])])+' \\\\')
w('tab_tau.tex','\n'.join(rows))
# ---- ejemplos de contracción
k,knat=kfit(M,V,TR,'estado-mes'); yi=[y-2000 for y in TR]; n=M[yi].copy(); dd=V[yi].copy(); n[0,0]=0; dd[0,0]=0; ns,ds=n.sum(0),dd.sum(0)
MESN=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
rows=[]; ej=[('Tlaxcala',11),('Aguascalientes',8),('Morelos',10),('Guerrero',5)]
for e,m in ej:
    s=claves.index(e); a,b=ns[m-1,s],ds[m-1,s]; kh=a/b; kn=knat[m-1]; om=b/(b+100); kt=(a+100*kn)/(b+100); cv=np.sqrt(1/a+1/b)
    rows.append(f"{e} ({MESN[m-1]}) & {int(a):,} & {int(b):,} & {kh:.3f} & {kn:.3f} & {om:.3f} & {kt:.3f} & {cv*100:.1f} \\\\".replace(',','\\,'))
w('tab_ejemplos.tex','\n'.join(rows))
# ---- factores nacionales
yt=[y-2000 for y in range(2003,2012)]; kT=M[yt].sum((0,2))/T[yt].sum((0,2))
rows=[f"{MESN[m].capitalize()} & {knat[m]:.3f} & {1/knat[m]:.2f} & {kT[m]:.3f} \\\\" for m in range(12)]
w('tab_knat.tex','\n'.join(rows))
# ---- conteos
tot={'Terra':T.sum(),'Aqua':A.sum(),'S-NPP':V.sum()}
w('tab_conteos.tex',f"MODIS Terra & {int(T.sum()):,} \\\\\nMODIS Aqua & {int(A.sum()):,} \\\\\nVIIRS S-NPP & {int(V.sum()):,} \\\\\n\\midrule\nTotal filtrado & {int(T.sum()+A.sum()+V.sum()):,} \\\\".replace(',','\\,'))
# ---- piso de ruido Poisson
def piso(years):
    kk=kfit(M,V,TR,'estado-mes')[0]; yi=[y-2000 for y in years]
    var=kk*(1+kk)*V[yi]           # Var(kV - M) = k(1+k) mu
    sm=np.sqrt(2/np.pi)*np.sqrt(var).sum()/M[yi].sum()
    an=np.sqrt(2/np.pi)*np.sqrt(var.sum((1,2))).sum()/M[yi].sum()
    return sm,an
sm,an=piso(TE); 
w('num_piso.tex',f"\\newcommand{{\\pisoSM}}{{{pct(sm)}}}\\newcommand{{\\pisoAN}}{{{pct(an)}}}\n"); print('piso',sm,an)
# ---- pronóstico: nacional y estados
P=J['pronostico']; nm={'day':'Diario (1--30 días)','week':'Semanal (1--12 semanas)','month':'Mensual (1--12 meses)'}
rows=[f"{nm[l]} & {pct(P['nacional'][l]['modelo'])} & {pct(P['nacional'][l]['clim'])} & {pct(P['nacional'][l]['naive'])} & {pct(P['nacional'][l]['sesgo'])} & {pct(P['nacional'][l]['cobertura'],1)} \\\\" for l in nm]
w('tab_pron_nac.tex','\n'.join(rows))
rows=[f"{nm[l]} & {pct(P['estados'][l]['mediana_modelo'])} & {pct(P['estados'][l]['mediana_clim'])} & {pct(P['estados'][l]['mediana_naive'])} & {P['estados'][l]['estados_modelo_mejor_que_naive']} & {P['estados'][l]['estados_modelo_mejor_que_clim']} & {pct(P['estados'][l]['mediana_cobertura'],1)} \\\\" for l in nm]
w('tab_pron_est.tex','\n'.join(rows))
# ---- rejilla de ajuste
o=json.load(open('/tmp/ajuste_pronostico.json')); o.sort(key=lambda x:x['obj'])
rows=[]
for i,r in enumerate(o[:5]):
    p=r['P']; ws=r['w']; mk='\\textbf{%s}' if i==0 else '%s'
    rows.append(' & '.join([mk%str(p['K']),mk%(f"{p['lam']:g}"),mk%str(p['W']),mk%str(p['tau'])]+[mk%pct(x) for x in ws]+[mk%pct(r['obj'])])+' \\\\')
w('tab_rejilla.tex','\n'.join(rows)); print('grid',len(o))
# ---- pronóstico 2026
p=S['pron']; rows=[f"{MESN[i].capitalize()} 2026 & {p['pred'][i]:,.0f} & {p['lo'][i]:,.0f}--{p['hi'][i]:,.0f} & {S['obs2025'][i]:,.0f} & {S['clim13_25'][i]:,.0f} \\\\".replace(',','\\,') for i in range(12)]
rows.append('\\midrule'); rows.append(f"Total & {sum(p['pred']):,.0f} & --- & {sum(S['obs2025']):,.0f} & {sum(S['clim13_25']):,.0f} \\\\".replace(',','\\,'))
w('tab_pron2026.tex','\n'.join(rows))
w('num_misc.tex',f"\\newcommand{{\\totalArm}}{{{d.hotspots_armonizados.sum():,.0f}}}\\newcommand{{\\razonVM}}{{{sum(a['viirs_crudo'] for a in J['anual'])/sum(a['modis_observado'] for a in J['anual']):.2f}}}\\newcommand{{\\difArm}}{{{(sum(a['viirs_armonizado'] for a in J['anual'])/sum(a['modis_observado'] for a in J['anual'])-1)*100:.2f}}}\\newcommand{{\\crec}}{{{(sum(p['pred'])/sum(S['obs2025'])-1)*100:.1f}}}\n".replace(',','\\,'))
print('ok')
