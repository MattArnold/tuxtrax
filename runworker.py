import penguicontrax
from rq import Worker, Queue, Connection

penguicontrax.init()
listen = ['high', 'default', 'low']
conn = penguicontrax.conn

if __name__ == '__main__':
	with Connection(conn):
		worker = Worker(map(Queue, listen))
		worker.work()

