import NISTfit
import numpy as np, time
import matplotlib.pyplot as plt

def get_eval_poly(Npoints):
    x = np.linspace(0,1,Npoints)
    y = 1 + 2*x + 3*x**2 + 4*x**6
    order = 6
    outputs = [NISTfit.PolynomialOutput(order, NISTfit.NumericInput(_x, _y)) 
               for _x,_y in zip(x, y)]
    eva = NISTfit.NumericEvaluator()
    eva.add_outputs(outputs)
    return eva, [1.5]*(order+1)

def get_eval_decaying_exponential(Norder):
    a = 0.2; b = 3; c = 1.3;
    x = np.linspace(0, 2, 1000)
    y = np.exp(-a*x)*np.sin(b*x)*np.cos(c*x)
    outputs = [NISTfit.DecayingExponentialOutput(Norder, NISTfit.NumericInput(_x, _y)) 
               for _x,_y in zip(x, y)]
    eva = NISTfit.NumericEvaluator()
    eva.add_outputs(outputs)
    return eva, [0.5, 2, 0.8]

def speedtest(get_eva, args, ofname):

    o = NISTfit.LevenbergMarquardtOptions()
    o.tau0 = 1

    fig, ax = plt.subplots(1,1,figsize=(4,3))
    
    for arg in args: # order of Taylor series expansion
        
        # Serial evaluation
        eva, o.c0 = get_eva(arg)
        Nserial = 3000
        eva.set_coefficients(o.c0)
        N = eva.get_outputs_size()
        tic = time.clock()
        for i in range(Nserial):
            eva.evaluate_serial(0, N, 0)
        toc = time.clock()
        elap = toc-tic
        time_serial = elap/Nserial

        # Parallel evaluation
        o.threading = True
        times = []
        for Nthreads in [1,2,3,4,5,6,7,8]:
            #NISTfit.Eigen_setNbThreads(Nthreads)
            eva, o.c0 = get_eva(arg)
            eva.set_coefficients(o.c0)
            elap = 0
            tic = time.clock()
            Nrepeat = 3000
            for i in range(Nrepeat):
                cfinal = eva.evaluate_parallel(Nthreads)
            toc = time.clock()
            elap = toc-tic
            times.append(elap/Nrepeat)
        line, = plt.plot(range(1, len(times)+1),time_serial/np.array(times))
        if arg < 0:
            lbl = 'native'
        else:
            lbl = 'N: '+str(arg)
        plt.text(len(times)-0.5, (time_serial/np.array(times))[-1], lbl, 
                 ha='right', va='center',
                 color=line.get_color(),
                 bbox = dict(facecolor='w',
                             edgecolor=line.get_color(),
                             boxstyle='round')
                 )

    plt.plot([1,8],[1,8],'k',lw=3,label='linear speedup')
    plt.xlabel(r'$N_{\rm threads}$ (-)')
    plt.ylabel(r'Speedup $t_{\rm serial}/t_{\rm parallel}$ (-)')
    plt.tight_layout(pad=0.3)
    plt.savefig(ofname)
    plt.show()

if __name__=='__main__':
    speedtest(get_eval_poly, [100,10000],'speedup_polynomial.pdf')
    speedtest(get_eval_decaying_exponential, [-1,5,20], 
              'speedup_decaying_exponential.pdf')