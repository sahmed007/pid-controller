"""Execute reference solutions separately from reader work and check course structure.
Run from the checkout: uv run python scripts/validate_tutorial.py
"""
from pathlib import Path
import ast
import re
import tempfile
import xml.etree.ElementTree as ET
import nbformat as nb
import numpy as np
from scipy.linalg import expm
from scipy.integrate import solve_ivp
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1] / 'src/notebooks'


def reference_cells(notebook):
    for cell in notebook.cells:
        if cell.cell_type == 'code' and 'previously-implemented' in cell.metadata.get('tags', []):
            yield cell.source
        if cell.metadata.get('pid_solution'):
            match = re.search(r'```python\n(.*?)\n```', cell.source, re.S)
            if not match:
                raise AssertionError('Solution has no Python block')
            yield match[1]


def definitions(number):
    n = nb.read(next(ROOT.glob(f'{number:02d}_*.ipynb')), 4)
    scope = dict(np=np, solve_ivp=solve_ivp, R=1.0, L=.01, K_t=.1, K_e=.1, J=.01, b=.001)
    for code in reference_cells(n):
        nodes = [node for node in ast.parse(code).body if isinstance(node, (ast.FunctionDef, ast.ClassDef))]
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<reference definitions>', 'exec'), scope)
    return scope


def independent_checks():
    s = definitions(9)
    # Independent state-space matrix and exact held-input propagation.
    A = np.array([[-100., -10.], [10., -.1]])
    B = np.array([[100., 0.], [0., -100.]])
    for voltage, load in [(6., 0.), (4.4, .1), (-3., -.05)]:
        equilibrium = np.linalg.solve(A, -(B @ [voltage, load]))
        np.testing.assert_allclose(s['motor_dynamics'](0, equilibrium, voltage, load), [0, 0], atol=1e-10)
        initial = np.array([.7, 12.])
        exact = equilibrium + expm(A*.013) @ (initial-equilibrium)
        numeric = solve_ivp(s['motor_dynamics'], (0,.013), initial, args=(voltage,load), rtol=1e-9, atol=1e-11)
        np.testing.assert_allclose(numeric.y[:,-1], exact, rtol=1e-8, atol=1e-9)
    # Entire sampled PI trajectory against exact interval-by-interval plant propagation.
    dt=.001; exact=np.zeros(2); integral=0.; expected=[]
    M=expm(A*dt); G=np.linalg.solve(A,(M-np.eye(2))@B)
    for k in range(1000):
        expected.append(exact.copy())
        error=40-exact[1]; integral+=error*dt
        exact=M@exact+G@np.array([.4*error+.5*integral,0.])
    run=s['simulate'](s['PID'](.4,.5,0),duration=1)
    np.testing.assert_allclose(np.array(expected), np.array([run['current'],run['speed']]).T, atol=1e-6, rtol=1e-7)
    for kwargs in [dict(dt=0),dict(dt=-1),dict(dt=np.nan),dict(duration=0),dict(duration=-1),dict(duration=np.inf),dict(duration=.0015),dict(noise=-1)]:
        try:s['simulate'](s['PID'](.4,.5,0),**kwargs)
        except ValueError:pass
        else:raise AssertionError(f'Invalid simulation accepted: {kwargs}')
    for bounds in [(),(1,),(-1,1,2),(1,-1),(0,np.inf)]:
        try:s['PracticalPID'](.4,.5,.01,limits=bounds)
        except ValueError:pass
        else:raise AssertionError(f'Invalid bounds accepted: {bounds}')
    for sign in [-1,1]:
        c=s['PracticalPID'](1,1,0,limits=(-1,1),anti_windup=True)
        assert c.update(sign*10,0,.1)==sign
        assert c.integral==0
        c.integral=sign*2
        c.update(-sign*.1,0,.1)
        assert abs(c.integral)<2  # Allow an inward increment while saturated.
    m=definitions(7)['metrics']
    sample={'time':np.arange(9)*.1,'speed':np.array([0,4,20,36,44,39.5,41,40.2,40]),'voltage':np.ones(9)}
    result=m(sample)
    np.testing.assert_allclose([result['rise'],result['overshoot'],result['settling']],[.2,10,.7])
    sample['speed']=np.zeros(9)
    assert m(sample)['rise'] is None and m(sample)['settling'] is None
    for target in [0,-40,np.nan]:
        try:m(sample,target)
        except ValueError:pass
        else:raise AssertionError('Invalid metric target accepted')
    print('PASS independent matrix-exponential, sampled trajectory, validation, anti-windup, and metrics checks',flush=True)


def main():
    independent_checks()
    with tempfile.TemporaryDirectory(prefix='pid-review-') as temporary:
        for path in sorted(ROOT.glob('*.ipynb')):
            source=nb.read(path,4);nb.validate(source)
            test=nb.v4.new_notebook(metadata=source.metadata, cells=[nb.v4.new_code_cell('%matplotlib inline')]+[nb.v4.new_code_cell(code) for code in reference_cells(source)])
            NotebookClient(test,timeout=240,kernel_name='python3',resources={'metadata':{'path':temporary}}).execute()
            rendered,_=HTMLExporter().from_notebook_node(source)
            soup=BeautifulSoup(rendered,'html.parser')
            tasks=len(soup.select('.implementation-task'))
            assert tasks==sum(bool(c.metadata.get('pid_solution')) for c in source.cells)
            assert all(not d.has_attr('open') for d in soup.find_all('details'))
            for image in soup.find_all('img'):
                url=image.get('src','')
                if url.startswith('assets/'):
                    ET.parse(ROOT/url)
            for a in soup.find_all('a',href=True):
                if a['href'].endswith('.ipynb'):assert (ROOT/a['href']).is_file()
            print(f'PASS {path.name}: {tasks} exercises, fresh kernel, HTML and links',flush=True)


if __name__ == '__main__':
    main()
