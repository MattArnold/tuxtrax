import penguicontrax
import os

penguicontrax.init()

app = penguicontrax.app
apppath = os.path.abspath(os.path.dirname(__file__))

extra_dirs = [apppath + '/penguicontrax/templates/js']
extra_files = extra_dirs[:]
for extra_dir in extra_dirs:
    for dirname, dirs, files in os.walk(extra_dir):
        for filename in files:
            filename = os.path.join(dirname, filename)
            if os.path.isfile(filename):
                extra_files.append(filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', extra_files=extra_files)
