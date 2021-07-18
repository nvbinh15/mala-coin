from django.core import validators
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User


class Blockchain(models.Model):
    difficulty = models.IntegerField(
        blank=True, null=True, default=4,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    miner_rewards = models.FloatField(
        blank=True, null=True, default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    block_size = models.IntegerField(blank=True, null=True, default=10)

    def __str__(self):
        return "Malacoin Blockchain"


class Block(models.Model):
    id = models.AutoField(primary_key=True) # block number
    time = models.TimeField(auto_now_add=True) # the time at which block is created
    prev = models.CharField(max_length=64, default="") # hash of the previous block
    nonce = models.IntegerField()
    hash = models.CharField(max_length=64, default="") # hash of block

    def __str__(self):
        result = f"Block: {self.index}\n" + f"Hash: {self.hash}\n"
        # result += f"Transactions:\n"
        # for transaction in self.transactions:
        #     result += '    ' + str(transaction) + '\n'
        result += f"Time created: {self.time}\n" + f"Previous hash: {self.prev}\n" + f"Nonce: {self.nonce}\n"
        return result

class Transaction(models.Model):
    sender = models.OneToOneField(User, on_delete=models.PROTECT)
    receiver = models.OneToOneField(User, on_delete=models.PROTECT)
    amount = models.IntegerField(validators=[MinValueValidator(0)], blank=False, null=False) # amount of coins transferred
    time = models.TimeField(auto_now_add=True) # the time at which transaction is make
    hash = models.CharField(max_length=64, default="") # hash of transaction

    def __str__(self):
        return str(self.sender + ' ---> ' + self.receiver + ': ' + str(self.amount) + ' MAL at ' + str(self.time))

