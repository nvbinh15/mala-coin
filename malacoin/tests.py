from django.test import TestCase
from models import *


chain = Blockchain()
transaction1 = Transaction('A', 'B', 100)
block1 = Block(transactions=[transaction1], time='now', index=1)
chain.add_block(block1)
for block in chain.chain:
    print(block)

print(transaction1)

