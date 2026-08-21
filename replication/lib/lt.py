from fractions import Fraction as F
from sympy import Poly, symbols, cyclotomic_poly, QQ

z=symbols('z'); t=symbols('t')

class Ram:
    """Totally ramified ext of Q_p of degree e = Q[t]/(g), g = Phi_N(1+t) Eisenstein.
       v normalized v(p)=1 ; v(t)=1/e. Elements: list of e Fractions (coeffs of t^i)."""
    def __init__(self,p,N):
        self.p=p
        phi=Poly(cyclotomic_poly(N,z),z)
        g=Poly(phi.as_expr().subs(z,1+t),t)
        g=g.monic()
        self.e=g.degree()
        # reduction: t^e = -(g - t^e)
        cs=[F(int(c.p),int(c.q)) for c in [QQ.to_sympy(x).as_numer_denom() and QQ.to_sympy(x) for x in g.all_coeffs()]]
        allc=[F(str(x)) for x in g.all_coeffs()]
        assert allc[0]==1
        self.red=[-allc[self.e-i] for i in range(self.e)]  # t^e = sum red[i] t^i
        self.N=N
    def zero(self): return [F(0)]*self.e
    def one(self):
        z0=self.zero(); z0[0]=F(1); return z0
    def add(self,a,b): return [x+y for x,y in zip(a,b)]
    def sub(self,a,b): return [x-y for x,y in zip(a,b)]
    def smul(self,s,a): return [F(s)*x for x in a]
    def reduce(self,long):
        out=long[:]
        for d in range(len(out)-1,self.e-1,-1):
            c=out[d]
            if c==0: continue
            out[d]=F(0)
            for i in range(self.e):
                out[d-self.e+i]+= c*self.red[i]
        return out[:self.e]
    def mul(self,a,b):
        L=[F(0)]*(2*self.e)
        for i,x in enumerate(a):
            if x==0: continue
            for j,y in enumerate(b):
                if y==0: continue
                L[i+j]+=x*y
        return self.reduce(L)
    def pw(self,a,n):
        r=self.one()
        for _ in range(n): r=self.mul(r,a)
        return r
    def inv(self,a):
        # extended euclid in Q[t]/(g) -- use sympy
        from sympy import invert, Poly as P
        gp=P([F(1)]+[ -self.red[self.e-1-i] for i in range(self.e)],t,domain=QQ)
        # rebuild g properly: g = t^e - sum red[i] t^i
        coeffs=[F(1)]+[F(0)]*self.e
        gg=[F(0)]*(self.e+1); gg[self.e]=F(1)
        for i in range(self.e): gg[i]-=self.red[i]
        Gp=P(list(reversed([__import__('sympy').Rational(x.numerator,x.denominator) for x in gg])),t,domain=QQ)
        Ap=P(list(reversed([__import__('sympy').Rational(x.numerator,x.denominator) for x in a])),t,domain=QQ)
        Ip=invert(Ap,Gp)
        cs=Ip.all_coeffs() if hasattr(Ip,'all_coeffs') else P(Ip,t,domain=QQ).all_coeffs()
        cs=list(reversed(cs))
        out=self.zero()
        for i,c in enumerate(cs):
            r=__import__('sympy').Rational(c)
            out[i]=F(int(r.p),int(r.q))
        return out

def v2(fr,p):
    if fr==0: return None
    n,d=fr.numerator,fr.denominator; v=0
    while n%p==0: n//=p; v+=1
    while d%p==0: d//=p; v-=1
    return v
def val(R,a):
    best=None
    for i,x in enumerate(a):
        if x==0: continue
        vv=F(v2(x,R.p))+F(i,R.e)
        if best is None or vv<best: best=vv
    return best

def sexp(R,f,N):
    c=[R.zero() for _ in range(N+1)]; c[0]=R.one()
    for n in range(1,N+1):
        acc=R.zero()
        for k in range(1,n+1):
            if all(y==0 for y in f[k]): continue
            acc=R.add(acc,R.smul(k,R.mul(f[k],c[n-k])))
        c[n]=R.smul(F(1,n),acc)
    return c
def sdiv(R,A,B,N):
    """A/B, B[0] invertible"""
    b0=R.inv(B[0]); C=[R.zero() for _ in range(N+1)]
    for n in range(N+1):
        s=A[n][:]
        for k in range(1,n+1):
            if all(y==0 for y in B[k]): continue
            s=R.sub(s,R.mul(B[k],C[n-k]))
        C[n]=R.mul(s,b0)
    return C
def subst_pow(R,A,q,N):
    C=[R.zero() for _ in range(N+1)]
    k=0
    while q*k<=N: C[q*k]=A[k][:]; k+=1
    return C

def Em(p,m,N):
    """Pulita E_m(T) = exp( sum_{j=0}^m varpi_{m-j} T^{p^j} / p^j ), varpi_j = zeta_{p^{j+1}} - 1
       (Lubin-Tate = multiplicative group; Matsuda's choice; at p=2, P(X)=2X+X^2 exactly)."""
    Nc=p**(m+1); R=Ram(p,Nc)
    zeta=R.zero(); zeta[0]=F(1)
    if R.e>=2: zeta[1]=F(1)      # zeta_{p^{m+1}} = 1+t
    else: zeta[0]=F(1)           # e=1 only if m=0,p=2 -> zeta_2 = -1
    if R.e==1: zeta=[F(-1)]
    def varpi(j):
        # zeta_{p^{j+1}} - 1 = zeta^{p^{m-j}} - 1
        w=R.pw(zeta,p**(m-j))
        return R.sub(w,R.one())
    f=[R.zero() for _ in range(N+1)]
    for j in range(m+1):
        d=p**j
        if d>N: break
        f[d]=R.smul(F(1,p**j),varpi(m-j))
    return R,sexp(R,f,N),[varpi(j) for j in range(m+1)]

def report(p,m,N):
    R,E,ws=Em(p,m,N)
    print("="*74)
    print("p=%d  m=%d  (character order p^{m+1}=%d)  field Q_%d(zeta_%d), e=%d"%(p,m,p**(m+1),p,p**(m+1),R.e))
    print("  v(varpi_j) j=0..m :",[str(val(R,w)) for w in ws], " (expect 1/(p^j(p-1)))")
    rs=[(k,val(R,E[k])) for k in range(1,N+1)]
    print("  --- Pulita E_m(T): v(c_k) and v(c_k)/k ---")
    print("   k :", " ".join("%d"%k for k in range(1,min(N,20)+1)))
    print("  v/k:", " ".join(str(v/k) if v is not None else "inf" for k,v in rs[:20]))
    fin=[(k,v/k) for k,v in rs if v is not None]
    print("  min over k<=%d of v/k = %s   (v(varpi_m)=%s)"%(N,min(r for _,r in fin),val(R,ws[m])))
    print("  tail min over k in [%d,%d] = %s"%(N//2,N,min(r for k,r in fin if k>=N//2)))
    # theta = E(T^p)/E(T)
    Ep=subst_pow(R,E,p,N)
    TH=sdiv(R,Ep,E,N)
    rs2=[(k,val(R,TH[k])) for k in range(1,N+1)]
    fin2=[(k,v/k) for k,v in rs2 if v is not None]
    print("  --- theta_m(T) = E_m(T^p)/E_m(T)  [the OVERCONVERGENT splitting function] ---")
    print("   k :", " ".join("%d"%k for k in range(1,min(N,20)+1)))
    print("  v/k:", " ".join(str(v/k) if v is not None else "inf" for k,v in rs2[:20]))
    mn=min(r for _,r in fin2); at=[k for k,r in fin2 if r==mn]
    print("  min over k<=%d of v/k = %s  at k=%s"%(N,mn,at[:8]))
    print("  tail min over k in [%d,%d] = %s   -> in units of v(varpi_m)=%s : %s"%(
        N//2,N,min(r for k,r in fin2 if k>=N//2), val(R,ws[m]), min(r for k,r in fin2 if k>=N//2)/val(R,ws[m])))
    return R,E,TH
