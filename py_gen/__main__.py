import subprocess
import os
import sys

def _pack_main():
    file_dir = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(file_dir, 'venv/bin/activate')

    # activate venv
    subprocess.run('source {venv_path}'.format(venv_path=venv_path), shell=True,  executable='/bin/bash', check=True)

    # run
    args = ' '.join(sys.argv[1:])
    main_path = os.path.join(file_dir, 'main.py')
    subprocess.run('python3 {main_path} {args}'.format(main_path=main_path, args=args),
         executable='/bin/bash',
        shell=True, 
        check=True)
        #stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    # deactivate venv

    # on exit deactive venv
