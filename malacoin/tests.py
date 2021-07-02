from django.test import TestCase
from models import *


chain = Blockchain()
transaction1 = Transaction('A', 'B', 100)
block1 = Block(transactions=[transaction1], time='now', index=1)
block1.mine_block()
chain.add_block(block1)


transaction2 = Transaction('c', 'd', 50)
transaction3 = Transaction('a', 'd', 150)
transaction4 = Transaction('a', 'b', 10000000)
block2 = Block(transactions=[transaction2, transaction3, transaction4], time='tomorrow', index=2)
block2.mine_block()
chain.add_block(block2)

chain.generate_keys()

for block in chain.chain:
    print(block)


